"""Monkey-patch cogitarelink.reason.sandbox.reason_over to support N3/EYE rules."""
import json
import subprocess
import tempfile
from pathlib import Path

from rdflib import Graph

import cogitarelink.reason.sandbox as sandbox
# Preserve original JSON-LD loader to catch HTTP errors when parsing contexts
_orig_to_graph = sandbox._to_graph
def _patched_to_graph(data: str | dict, fmt: str = "json-ld"):
    """Attempt to parse JSON-LD, stripping remote @context on failure to avoid HTTP errors."""
    try:
        return _orig_to_graph(data, fmt)
    except Exception as e:
        # Fallback: remove @context to prevent remote fetch
        try:
            obj = data if isinstance(data, dict) else json.loads(data)
        except Exception:
            raise e
        if isinstance(obj, dict) and "@context" in obj:
            obj.pop("@context", None)
            try:
                return _orig_to_graph(obj, fmt)
            except Exception:
                pass
        # Reraise if fallback fails
        raise e
# Apply patched loader
sandbox._to_graph = _patched_to_graph
from cogitarelink.reason.prov import wrap_patch_with_prov

# Preserve the original reason_over function
_original_reason_over = sandbox.reason_over

def _eye_run(data_ttl: str, rules_n3: str) -> Graph:
    workdir = Path(tempfile.mkdtemp(prefix="eyejs_"))
    data_f = workdir / "data.ttl"
    rules_f = workdir / "rules.n3"
    data_f.write_text(data_ttl, encoding="utf8")
    rules_f.write_text(rules_n3, encoding="utf8")
    payload = {
        "dataPath": str(data_f),
        "rulesPath": str(rules_f),
        "queryPath": None
    }
    out = subprocess.check_output(
        ["node", "js/eye-runner.mjs"],
        input=json.dumps(payload),
        text=True
    )
    derived = Graph().parse(data=out, format="n3")
    return derived

def patched_reason_over(jsonld: str, shapes_turtle=None, query=None, n3_rules=None, *args, **kwargs):
    if n3_rules is not None:
        # If input looks like Turtle, use it directly; otherwise parse JSON-LD to Turtle
        if jsonld.strip().startswith('@prefix'):
            data_ttl = jsonld
        else:
            # Parse JSON-LD using patched loader to avoid remote context fetch
            ds = sandbox._to_graph(jsonld)
            data_ttl = ds.default_context.serialize(format="turtle")
        # Run EYE reasoning
        derived_graph = _eye_run(data_ttl, n3_rules)
        # Compute the delta
        original_graph = Graph().parse(data=data_ttl, format="turtle")
        patch_graph = derived_graph - original_graph
        # Wrap with provenance and return
        summary = f"💡 EYE derived {len(patch_graph)} triples via n3_rules"
        prov_patch = wrap_patch_with_prov(patch_graph)
        return prov_patch.serialize(format="json-ld"), summary
    # Fallback to original
    return _original_reason_over(jsonld=jsonld, shapes_turtle=shapes_turtle, query=query, *args, **kwargs)

# Apply the monkey-patch
sandbox.reason_over = patched_reason_over