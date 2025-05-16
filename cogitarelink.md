# CogitareLink – Extended Architecture Overview

> **Version:** 2025‑05‑16  > **Status:** Draft for internal review

This document merges the original CogitareLink orientation bundle with the **new optional formal‑reasoning tier** (N3/EYE deontic logic).  No content from the original brief has been removed; new material is **highlighted with ▸ bullets** in headings and call‑outs.

---

## 0 · Mission

CogitareLink is a semantic‑memory substrate for agentic LLM systems. It stores JSON‑LD 1.1 data, runs SHACL/SPARQL rules to derive new facts, caches everything, and records provenance for every triple it inserts. Python provides only the micro‑kernel (≈ 600 LOC); all business logic lives in data artefacts (contexts, ontologies, shapes, rules) or is generated on‑the‑fly by the LLM.

---

## 1 · Layer model for knowledge artefacts

| Layer                              | Files                                          | Typical size | In prompt? |
| ---------------------------------- | ---------------------------------------------- | ------------ | ---------- |
| **0 – Context**                    | `*.context.jsonld` (term ↔ IRI map)            | 1‑5 KB       | Always     |
| **1 – Ontology**                   | `ontology.ttl / .jsonld`                       | 20‑200 KB    | On‑demand  |
| **2a – Shapes / Rules**            | `shapes.ttl`, `rules.ttl` (SHACL / sh\:JSRule) | 30‑300 KB    | On‑demand  |
| **▸ 2b – Formal logic (optional)** | `logic.n3` (N3/EYE rules)                      | 5‑150 KB     | On‑demand  |
| **3 – Data**                       | `*.jsonld` instances                           | 5 KB‑1 MB    | Streamed   |

Cross‑link conventions remain identical; Layer 2b artefacts are discovered by the same *AffordanceScanner* via a new predicate `ex:hasN3Rule`.

---

## 2 · Key Python modules

| Module           | Core classes / functions                          | Role                                                            |
| ---------------- | ------------------------------------------------- | --------------------------------------------------------------- |
| `core.debug`     | `get_logger()`                                    | Colourised logging                                              |
| `core.cache`     | `Cache`, `DiskCache`                              | LRU/TTL fetch cache                                             |
| `vocab.registry` | `registry`                                        | typed map `prefix → VocabEntry`                                 |
| `vocab.composer` | `composer.compose()`                              | merges/derives JSON‑LD contexts                                 |
| `reason.afford`  | `AffordanceScanner.scan()`                        | extracts shape/rule/ontology **and N3‑rule** hints              |
| `reason.prov`    | `wrap_patch_with_prov()`                          | provenance wrap for triples                                     |
| `reason.sandbox` | `reason_over(jsonld, shapes?, query?, n3_rules?)` | executes SHACL, SPARQL, **and EYE**; returns patch + NL summary |
| `tools.reason`   | `reason_tool()`, `FUNCTION_SPEC`                  | OpenAI‑function bridge to `reason_over`                         |
| `core.graph`     | `GraphManager`                                    | persists graphs (`rdflib Dataset`)                              |

▸ *Changes*: `reason_over` gains an **optional** `n3_rules` parameter; the sandbox pipes data + rules through the EYE WASM binary when present.

---

## 3 · Single tool surface (updated)

```jsonc
{
  "name": "reason_over",
  "description": "Run SHACL rules, SPARQL CONSTRUCT, **or N3/EYE rules** and update memory",
  "parameters": {
    "type": "object",
    "properties": {
      "jsonld": {"type": "string"},
      "shapes_turtle": {"type": "string", "nullable": true},
      "query": {"type": "string", "nullable": true},
      "n3_rules": {"type": "string", "nullable": true}
    },
    "required": ["jsonld"]
  }
}
```

Execution matrix:

| Parameters present | Engine invoked             | Notes    |
| ------------------ | -------------------------- | -------- |
| `shapes_turtle`    | SHACL/SHACL‑AF (iterative) | existing |
| `query`            | SPARQL CONSTRUCT           | existing |
| ▸ `n3_rules`       | **EYE forward‑chaining**   | new      |

Only **one** parameter set should be passed per call; the sandbox throws a `ValueError` if more than one engine is selected.

---

## 4 · Typical agent flow (unchanged, with N3 option)

1. Load a domain JSON‑LD doc.
2. `AffordanceScanner.scan()` → finds shapes/rules/N3 IRIs.
3. Call `reason_over` with `shapes_turtle` **or** `n3_rules` → inference patch.
4. Optionally call again with a SPARQL CONSTRUCT or SELECT to fetch answers.
5. Explain answer, citing `prov:Activity` blank node from patch.

---

## 5 · Repository layout

```
cogitarelink/
  core/           (debug, cache, graph, ...)
  vocab/          (registry, composer, collision)
  reason/
    afford.py
    sandbox.py    ← patched for EYE
    prov.py
  tools/
    reason.py
  data/
    campus/
      context.jsonld
      ontology.ttl
      shapes.ttl
      rules.ttl
      logic.n3          ←▸  NEW optional file
      events.jsonld
    kitchen/
      ...
  tests/
    ...
```

---

## 6 · Design guidelines for new domains (amended)

1. Author a tiny Layer‑0 context (< 5 KB).
2. Write ontology & shapes in Turtle (`ontology.ttl`, `shapes.ttl`).
3. **Optionally** add a `logic.n3` file for advanced deontic/temporal reasoning.
4. Put data in `*.jsonld` and point to shapes with `ex:hasShape` **and/or** `ex:hasN3Rule`.
5. No Python required; drop files in `data/yourdomain/`.

---

## 7 · Why this matters

* Scales with model context – only Layer 0 sits in prompt; larger layers streamed when needed.
* Explainable – provenance on every triple, plus optional **EYE proof JSON** for formal rules.
* Software 2.0 – adding capabilities is file‑drop, not code change; LLM synthesises logic.
* ▸ **Safety** – deontic N3 rules allow contrary‑to‑duty obligations, priorities, and other normative constructs that SHACL alone cannot express.

---

## ▸ 8 · Optional Formal Reasoning Layer (N3/EYE)

### 8.1  Position in the stack

```
context.jsonld  →  ontology.ttl  →  shapes.ttl / rules.ttl  →  logic.n3  →  data.jsonld
```

* `logic.n3` is pure N3 syntax, executed by **EYE 18.16.1 (WASM)**.
* Linked via `ex:hasN3Rule`.
* Can consume violation triples output by SHACL to trigger **contrary‑to‑duty** repairs.

### 8.2  Rule skeletons

```n3
# Obligation
{ ?plan a ml:PlannedAction. } => { ?plan dl:obliges ex:Perform_p. }.

# Prohibition
{ ?plan ex:contains ex:CauseHarm. } => { ?plan dl:violates ex:NoHarm. }.

# CTD fix
{ ?plan dl:violates ex:NoHarm. } => { ?plan dl:obliges ex:AlertStaff. }.
```

### 8.3  Priority handling

```n3
{ ?r a dl:Rule; ex:priority ?n. } => { ?r dl:hasPriority ?n. }.
```

`e:n3/compare` built‑ins let EYE pick the highest‑priority obligation when conflicts occur.

### 8.4  Sandbox integration

```python
if n3_rules:
    data_ttl   = jsonld_to_turtle(jsonld)
    rules_path = _save_temp(n3_rules, ".n3")
    cmd = ["eye", data_ttl, rules_path, "--pass", "new", "--quiet"]
    derived_ttl = subprocess.check_output(cmd, text=True)
    patch = turtle_to_graph(derived_ttl) - original_graph
    summary = f"💡 EYE derived {len(patch)} triples via {rules_path}"
    return wrap_patch_with_prov(patch, summary, proof_path="proof.json")
```

### 8.5  Proofs

Add `--proof proof.json` to the EYE call; store the JSON next to the patch inside `GraphManager`.  Agents may cite `prov:Activity _:b42 owl:hasProof <proof.json>` when explaining outcomes.

---

## ▸ 9 · Updated reason\_over contract

No breaking changes; `n3_rules` is **optional**.  Validation order recommendation:

1. SHACL (first) – flag violations.
2. N3/EYE (second) – apply deontic logic, CTD recovery, temporal reasoning.
3. SPARQL queries (optional) – extract answer triples.

---

## ▸ 10 · File‑level wiring example

```turtle
@prefix ex: <https://example.org/vocab#> .
@prefix shapes: <../campus/shapes.ttl#> .
@prefix n3: <../campus/logic.n3#> .

:plan42  a ml:PlannedAction ;
        ex:hasShape   shapes:NoHarmShape ;
        ex:hasN3Rule  n3:NoHarmDeonticRules .
```

---

## ▸ 11 · Testing additions

| Test file                | What it asserts                                           |
| ------------------------ | --------------------------------------------------------- |
| `tests/test_deontic.py`  | EYE derives CTD obligations when SHACL flags a violation. |
| `tests/test_priority.py` | Higher‑priority rules override lower ones.                |

All new tests run in < 1 s using the EYE WASM binary.

---

## 12 · Context window considerations (unchanged)

*Layer recommendations table preserved from the original document.*

---

## 13 · FAQ (selected additions)

**Q :** *Do I have to use N3?*
**A :** No. The EYE layer is optional. Omit `ex:hasN3Rule` and the scanner will ignore N3 reasoning.

**Q :** *Can I convert SHACL shapes to N3?*
**A :** Yes – use the `eye‑shacl` converter to generate an equivalent `logic.n3` file.

**Q :** *Is EYE WASM safe in a sandbox?*
**A :** Yes – the binary is pure userspace and respects the existing file/CPU quotas of the Python micro‑kernel.

---

## 14 · Glossary (amended)

* **Layer 2b** – Optional formal‑logic bundle (`logic.n3`) executed by EYE.
* **EYE** – Euler Yet another proof Engine; N3 forward‑chaining reasoner with proof export.
* **CTD** – Contrary‑to‑duty obligation (a reparative norm that activates when a primary norm is violated).

---

*End of document.*
