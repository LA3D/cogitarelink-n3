# n3-eye
Demo project that integrates the EYE (eyereasoner) WASM reasoner into CogitareLink’s `reason_over` pipeline,
enabling N3 rule execution alongside SHACL and SPARQL.

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher

## Installation

Clone the repo and enter its directory:
```bash
git clone https://github.com/LA3D/n3-eye.git
cd n3-eye
```

Create and activate a virtual environment, then install Python dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

Install Node dependencies for the EYE runner:
```bash
npm install
```

## Usage

Verify that patches are applied and the Node runner is available:
```bash
python main.py
```

Run the demo agent (set `OPENAI_API_KEY` for LLM-driven flow; otherwise it falls back to a direct EYE invocation):
```bash
export OPENAI_API_KEY=<YOUR_API_KEY>
python demo_agent.py
```

## Testing

Run the test suite:
```bash
pytest -q
```

## Project Structure

- `patch_reason_sandbox.py`: monkey-patch `reason_over` to support N3/EYE rules
- `patch_reason_tool.py`: extends the OpenAI function bridge and patches `reason_tool`
- `demo_agent.py`: Cosette-based demo agent demonstrating both LLM and direct tool invocation
- `main.py`: CLI script to verify patch application
- `js/eye-runner.mjs`: Node.js runner for EYE WASM
- `tests/`: unit tests covering sandbox and tool patches

## Next Steps

- Integrate SHACL validation and SPARQL CONSTRUCT in the unified pipeline
- Enhance natural-language summaries and system prompts
- Capture and expose proof objects in provenance for auditing
- Provide an interactive UI or REST API for end users
