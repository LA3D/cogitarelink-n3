"""
Simple Cosette-based demo agent for CogitareLink N3/EYE reasoning.
Requires OPENAI_API_KEY in the environment.
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env (so OPENAI_API_KEY is set)
load_dotenv()

# Ensure OpenAI key is set
if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError('Please set OPENAI_API_KEY in the environment')

# Apply sandbox and tool patches for N3/EYE reasoning
try:
    import patch_reason_sandbox  # noqa: F401
    import patch_reason_tool     # noqa: F401
except ImportError:
    pass

from cosette import Chat
from cogitarelink.tools.reason import reason_tool, FUNCTION_SPEC

def main():
    # Print the function spec the agent will use
    print('--- reason_over function spec ---')
    print(json.dumps(FUNCTION_SPEC, indent=2))

    # System prompt: instruct the agent on using the tool
    system_prompt = '''
You are CogitareLink Assistant. You can invoke the function `reason_tool`
to run SHACL, SPARQL, or N3/EYE reasoning on JSON-LD input. To apply rules
of engagement from a mission order, pass the entire VC JSON-LD via the `jsonld`
parameter and the N3 rules string via the `n3_rules` parameter; the tool will
verify the credential, extract the data, run EYE on the rules, and return a
provenance-wrapped patch along with a natural-language summary.
Always call the function when reasoning is needed, and present only the final result.
'''.strip()

    # Create the chat with our reason_tool as a Cosette tool
    chat = Chat(
        model='gpt-4',
        sp=system_prompt,
        tools=[reason_tool]
    )

    # Example mission-order VC (JSON-LD string)
    mission_vc = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            {"ex": "http://ex/", "contains": {"@id": "ex:contains", "@type": "@id"}}
        ],
        "type": ["VerifiableCredential","MissionOrder"],
        "issuer": "did:example:commander123",
        "issuanceDate": "2025-05-16T12:00:00Z",
        "credentialSubject": {
            "@id": "http://ex/plan",
            "mission": {"objective": "Secure Area X"},
            # Indicate that the plan contains a hazardous element
            "contains": "http://ex/CauseHarm",
            "rulesOfEngagement": {
                "n3": """
@prefix ex: <http://ex/> .
{ ?p ex:contains ex:CauseHarm } => { ?p ex:obliges ex:AlertStaff } .
"""
            }
        },
        "proof": {"type":"Ed25519Signature2020","jws":"..."}
    }

    # User prompt: provide the VC and ask for reasoning
    user_message = 'Mission order VC: ' + json.dumps(mission_vc)
    print('--- User Prompt ---')
    print(user_message)

    # Try running via the LLM function tool; if that fails (e.g., no valid API key),
    # fall back to direct invocation of reason_tool.
    try:
        response = chat(user_message)
        used_chat = True
    except Exception as e:
        print(f"[Chat failed: {e}], falling back to direct tool call.")
        used_chat = False
    # If the model invoked our tool, execute and display its result
    try:
        from cosette.core import call_func_openai
        tcs = response.choices[0].message.tool_calls or []
    except Exception:
        tcs = []
    if used_chat:
        # If chat succeeded and invoked our tool, execute and display results
        try:
            from cosette.core import call_func_openai
            tcs = response.choices[0].message.tool_calls or []
        except Exception:
            tcs = []
        if tcs:
            for tc in tcs:
                summary = call_func_openai(tc.function, ns=[reason_tool])
                print('--- Tool Result ---')
                print(summary)
                # Display new triples from memory in a human-readable form
                from cogitarelink.tools.reason import gm
                triples = gm.query()
                if triples:
                    print('--- Ingested Triples ---')
                    for s, p, o in triples:
                        # Simple natural-language mapping for common predicates
                        sp = str(p)
                        so = str(o)
                        if sp.endswith('obliges'):
                            print(f"• Plan {s} is now obliged to {so}")
                        elif sp.endswith('violates'):
                            print(f"• Plan {s} violates {so}")
                        else:
                            print(f"• {s} {sp} {so}")
        else:
            # No tool call: print assistant's response content
            print('--- Assistant Response ---')
            content = None
            if hasattr(response, 'choices'):
                try:
                    content = response.choices[0].message.content
                except Exception:
                    pass
            print(content or response)
    else:
        # Directly call the tool with the mission VC
        print('--- Direct reason_tool invocation ---')
        vc_json = json.dumps(mission_vc)
        n3_rules = mission_vc['credentialSubject']['rulesOfEngagement']['n3']
        summary = reason_tool(jsonld=vc_json, n3_rules=n3_rules)
        print(summary)
        # Show patch triples
        from cogitarelink.tools.reason import gm
        triples = gm.query()
        if triples:
            print('--- Ingested Triples ---')
            for s, p, o in triples:
                sp = str(p)
                so = str(o)
                if sp.endswith('obliges'):
                    print(f"• Plan {s} is now obliged to {so}")
                elif sp.endswith('violates'):
                    print(f"• Plan {s} violates {so}")
                else:
                    print(f"• {s} {sp} {so}")

if __name__ == '__main__':
    main()