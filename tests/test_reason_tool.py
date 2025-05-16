"""
Tests for the CogitareLink OpenAI-function bridge extension to support n3_rules.
"""
import pytest

# Ensure project root is on sys.path and apply sandbox/tool patches
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
__import__('patch_reason_sandbox')  # noqa: F401
__import__('patch_reason_tool')     # noqa: F401
import patch_reason_tool as tmod     # noqa: F401

import cogitarelink.tools.reason as rmod
from cogitarelink.tools.reason import reason_tool, FUNCTION_SPEC
from cogitarelink.core.graph import GraphManager
from rdflib import URIRef

@pytest.fixture(autouse=True)
def reset_graph_manager(monkeypatch):
    """Ensure a fresh GraphManager before each test (for the tool module)."""
    from cogitarelink.core.graph import GraphManager
    gm = GraphManager(use_rdflib=True)
    # Patch the gm that reason_tool writes into
    monkeypatch.setattr(tmod, 'gm', gm)
    return gm

def test_function_spec_includes_n3_rules():
    props = FUNCTION_SPEC['parameters']['properties']
    assert 'n3_rules' in props
    assert props['n3_rules'] == {'type': 'string', 'nullable': True}

def test_reason_tool_with_n3_rules(reset_graph_manager):
    data = "@prefix ex: <http://ex/>. ex:act a ex:MyAction."
    rules = "@prefix ex: <http://ex/>. { ?s a ex:MyAction } => { ?s ex:obliges ex:PerformAction }."
    summary = reason_tool(jsonld=data, n3_rules=rules)
    # The summary should report exactly one derived triple
    assert 'EYE derived 1' in summary
    # The GraphManager should contain the derived triple
    # Inspect the GraphManager used by the patched reason_tool
    triples = list(tmod.gm.query(
        URIRef('http://ex/act'),
        URIRef('http://ex/obliges'),
        URIRef('http://ex/PerformAction')
    ))
    assert len(triples) == 1, f"Expected 1 ingested triple, got {len(triples)}"