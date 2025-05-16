"""
Monkey-patch cogitarelink.tools.reason to support N3/EYE rules in its OpenAI-function bridge.
"""
import cogitarelink.tools.reason as tool_mod
import cogitarelink.reason.sandbox as sandbox
from rdflib import Dataset

# Extend the function spec to include n3_rules
tool_mod.FUNCTION_SPEC["parameters"]["properties"]["n3_rules"] = {
    "type": "string",
    "nullable": True
}

# Preserve existing GraphManager
gm = tool_mod.gm

def reason_tool(jsonld: str,
                shapes_turtle: str | None = None,
                query: str | None = None,
                n3_rules: str | None = None) -> str:
    """Run SHACL rules or SPARQL CONSTRUCT on JSON-LD and update memory."""
    # Delegate to sandbox
    patch, summary = sandbox.reason_over(
        jsonld=jsonld,
        shapes_turtle=shapes_turtle,
        query=query,
        n3_rules=n3_rules
    )
    # Ingest patch JSON-LD into GraphManager as nquads
    ds = Dataset()
    ds.parse(data=patch, format="json-ld")
    nquads = ds.serialize(format="nquads")
    gm.ingest_nquads(nquads, graph_id="patch")
    return summary

# Apply monkey-patch
tool_mod.reason_tool = reason_tool