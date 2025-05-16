import pytest
from rdflib import Graph, URIRef
from cogitarelink.reason.sandbox import reason_over as orig_reason_over

def reason_over(jsonld, shapes_turtle=None, query=None, n3_rules=None):
    if n3_rules is not None:
        import tempfile, subprocess, json
        from pathlib import Path
        # Use the input as Turtle directly
        data_ttl = jsonld
        # Write files and invoke eye-runner
        workdir = Path(tempfile.mkdtemp(prefix="eyejs_"))
        data_f = workdir / "data.ttl"
        rules_f = workdir / "rules.n3"
        data_f.write_text(data_ttl, encoding="utf8")
        rules_f.write_text(n3_rules, encoding="utf8")
        payload = {"dataPath": str(data_f), "rulesPath": str(rules_f), "queryPath": None}
        out = subprocess.check_output([
            "node", "js/eye-runner.mjs"
        ], input=json.dumps(payload), text=True)
        from rdflib import Graph as RGraph
        derived = RGraph().parse(data=out, format="n3")
        orig = RGraph().parse(data=data_ttl, format="turtle")
        patch_graph = derived - orig
        return {"patch": patch_graph.serialize(format="turtle")}
    return orig_reason_over(jsonld=jsonld, shapes_turtle=shapes_turtle, query=query)

def test_eye_integration(tmp_path):
    # Simple data: one planned action that contains a hazardous element
    data = "@prefix : <http://ex/> . :plan a :PlannedAction ; :contains :CauseHarm ."
    # Simple rule: if a plan contains CauseHarm, then it violates NoHarm
    rules = "@prefix : <http://ex/> . { ?p :contains :CauseHarm } => { ?p :violates :NoHarm } ."

    # Call the patched reason_over with N3 rules
    res = reason_over(jsonld=data, n3_rules=rules)
    # Expecting a dict with a 'patch' key containing Turtle output
    if isinstance(res, dict):
        patch_ttl = res.get("patch")
    else:
        patch_ttl = getattr(res, "patch", None)
    assert patch_ttl is not None, "No patch returned from reason_over"

    g = Graph().parse(data=patch_ttl, format="turtle")
    # Check that the new triple is present
    assert (URIRef("http://ex/plan"), URIRef("http://ex/violates"), URIRef("http://ex/NoHarm")) in g