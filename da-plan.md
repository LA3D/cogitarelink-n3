Below is a practical play‑book for dropping an N3/EYE logic tier into CogitareLink without disturbing the existing SHACL/SPARQL tool‑chain.  I treat N3 as Layer 2b—a rule bundle that sits next to shapes.ttl, is discovered by the same affordance scan, and is executed by an EYE‑powered sandbox.

⸻

1 Where N3 fits in the four‑layer stack

 layer‑0  context.jsonld         (≤ 2 KB, unchanged)
 layer‑1  ontology.ttl           (RDFS/OWL, unchanged)
 layer‑2a shapes.ttl  rules.ttl  (SHACL / sh:JSRule, existing)
 layer‑2b logic.n3               (N3 rules †)   ←  **NEW**
 layer‑3  data.jsonld            (instances, unchanged)

† file name convention: logic.n3 or rules.n3 so the AffordanceScanner can pattern‑match it.

⸻

2 Execution pathway

Step	What happens	Implementation hook
1	Scanner sees ex:hasN3Rule <logic.n3> in the data or shapes graph.	no Python change needed – treat it like any other affordance.
2	Agent fetches the N3 text and calls the tool:	

{
  "name": "reason_over",
  "arguments": {
    "jsonld": "<events.jsonld>",
    "query": null,
    "shapes_turtle": null,
    "n3_rules": "<logic.n3>"      // ← you add this optional key
  }
}
``` |

| 3 | Sandbox detects `n3_rules` and pipelines **EYE**: `eye data.ttl logic.n3 --pass new --quiet`. | Small patch to `reason.sandbox`; 10‑20 LOC. |
| 4 | EYE emits derived triples **and** a Proof JSON; sandbox wraps the new triples with `prov:Activity _:b42`. | Re‑use existing `wrap_patch_with_prov()`. |
| 5 | Agent may issue a follow‑up SPARQL query (still through `reason_over`) or just read the NL summary. | No change. |

> **Dependency tip:** use the WASM build **eye‑js v18.16.1 (Apr 2025)** so the same binary runs in Node, Python (via *pyodide*), or the browser.  [oai_citation:0‡GitHub](https://github.com/eyereasoner/eye-js?utm_source=chatgpt.com) [oai_citation:1‡Zenodo](https://zenodo.org/records/15299683?utm_source=chatgpt.com)  

---

## 3 Mapping deontic concepts into N3

| Deontic idea | N3 rule sketch (prefixes omitted) |
|--------------|-----------------------------------|
| **Obligation** *O p* | `{ ?plan a ml:PlannedAction. } => { ?plan dl:obliges ex:Perform_p. }.` |
| **Prohibition** *F p* | `{ ?plan ex:contains p. } => { ?plan dl:violates ex:No_p. }.` |
| **CTD rescue** | `{ ?plan dl:violates ex:NoHarm. } => { ?plan dl:obliges ex:AlertStaff. }.` |
| **Priority** | Encode numeric `ex:priority` on rule heads; EYE’s built‑in `e:n3/compare` lets you prefer the highest. |

EYE can also import your SHACL violation graph and fire CTD rules **after** validation.  A ready‑made converter (`eye-shacl`) compiles shapes to N3, so one engine can do both validation and reasoning if you prefer a single runtime  [oai_citation:2‡GitHub](https://github.com/giacomociti/eye-shacl?utm_source=chatgpt.com).

---

## 4 File‑level wiring

```turtle
# data.jsonld  (excerpt, Turtle)
:plan42  a ml:PlannedAction ;
         ex:hasShape   shapes:NoHarmShape ;
         ex:hasN3Rule  n3:NoHarmDeonticRules .

	•	ex:hasN3Rule is a tiny term you add to Layer‑0 so the scanner recognises it.
	•	n3:NoHarmDeonticRules dereferences to /shapes/logic.n3 (Layer 2b).
	•	The ontology (ontology.ttl) simply declares ex:hasN3Rule rdfs:range owl:Ontology so RDFS inference works.

⸻

5 Sandbox glue code (Python sketch)

def reason_over(..., n3_rules=None):
    ...
    if n3_rules:
        data_ttl   = jsonld_to_turtle(jsonld)
        rules_path = save_temp(n3_rules, ".n3")
        cmd = ["eye", data_ttl, rules_path, "--pass", "new", "--quiet"]
        derived_ttl = subprocess.check_output(cmd, text=True)
        patch = turtle_to_graph(derived_ttl) - original_graph
        summary = f"💡 EYE derived {len(patch)} triples via {rules_path}"
        return wrap_patch_with_prov(patch, summary)

That is literally the only Python you need besides a helper to convert JSON‑LD ⇆ Turtle.

⸻

6 Proofs & explanation

EYE can output a JSON proof (--nope --repeat=1000 --pass new --quiet --proof proof.json) which:
	•	names every rule fired (IRI or blank node)
	•	records substitutions, premises, and conclusions.

Store the proof file next to the patch URI; when the agent explains a decision it can cite prov:Activity _:b42 owl:hasProof <proof.json> and selectively quote the relevant rule chain.  This gives users a step‑by‑step audit log—a feature often requested for safety reviews  ￼.

⸻

7 SHACL ⇄ N3 synergy
	•	Validate first with SHACL to surface violations.
	•	Feed the violation triples into N3 rules to trigger CTD or priority logic.
	•	Optionally compile selected SHACL shapes into N3 for a single‑engine run (eye‑shacl already does the translation  ￼).

Because everything stays in RDF/Turtle, the hand‑off is zero‑cost.

⸻

8 Performance notes
	•	EYE handles tens of thousands of triples in milliseconds for forward‑chaining; add --quiet --pass new for speed.
	•	WASM build streams into memory, so no Docker layer is required.
	•	Cache compiled rules (logic.n3) just like you cache shapes.ttl—they are immutable Layer‑2 artefacts.

⸻

TL;DR
	1.	Add a logic.n3 file (Layer 2b) and link it with ex:hasN3Rule.
	2.	Patch reason_over so that when n3_rules is present the sandbox calls EYE on the data.
	3.	Return the derived triples + prov + optional proof; everything else in CogitareLink (cache, explain, query) remains unchanged.

With ~20 lines of Python and one extra file per domain you obtain a full deontic‑capable rule engine that complements SHACL, leverages EYE’s WASM portability, and keeps CogitareLink true to its “all logic lives in data” ethos.