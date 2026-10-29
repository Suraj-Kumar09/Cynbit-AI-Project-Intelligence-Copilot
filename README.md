# Cynbit AI Project Intelligence Copilot

LLM-powered tool that turns a raw client inquiry into a structured project brief
(category, requirements, missing info, clarifying questions, approach, architecture, risks)
for **human review**.

> Proposed solution for AI automation / software consulting workflows. It is not a verified
> description of any company's internal process, and its output is a draft, not a final scope or quote.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your API key
streamlit run app.py
pytest                      # tests run offline with a fake LLM client
```

## Structure
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, results tabs, Markdown/JSON export |
| `pipeline.py` | Input validation -> LLM call -> JSON parse -> schema validation (1 retry) |
| `prompts.py` | System + user prompt templates |
| `schemas.py` | Pydantic models, input limits, Markdown export |
| `tests/` | Pytest suite (no network needed) |
| `TECHNICAL_APPROACH.md` | Architecture and design decisions |
| `AI_OPPORTUNITY_REPORT.md` | Opportunity analysis template |

## Example
Input: *"We need an AI assistant for our e-commerce website that answers customer questions and tracks orders."*
Output: category *AI chatbot and business automation*; approach *LLM + RAG + order API*;
missing: platform, order API availability, expected traffic; next step: gather requirements first.

## Deploy
Streamlit Community Cloud: connect the repo, set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` in Secrets.
