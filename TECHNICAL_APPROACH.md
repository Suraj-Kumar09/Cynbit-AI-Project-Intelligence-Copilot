# Technical Approach

## Pipeline
Client/User -> Streamlit form -> Input validation (Pydantic: empty, min/max length)
-> LLM analysis (single structured call covering classification, extraction, gaps, approach/risks)
-> JSON parse + schema validation (one corrective retry) -> Project brief (Markdown/JSON export).

## Decisions
- **Single call, not multi-agent (v1):** one reliable structured-output call is easier to test and debug.
  Split into 4 stages (classify -> extract -> gaps -> architecture) or move to LangGraph only if quality
  data shows a single call is insufficient.
- **OpenAI-compatible client:** one code path for Gemini, OpenAI or a self-hosted model; switch via env vars.
- **Schema-first:** the Pydantic model is the contract; its JSON Schema is embedded in the prompt.
- **Untrusted input:** inquiry is wrapped in `<inquiry>` tags and treated as data (prompt-injection mitigation).
- **No invented facts:** unstated details go to `missing_information`, not `requirements`.
- **Human in the loop:** output is labelled a draft; no pricing or time estimates are produced.

## Known limitations
- Output quality depends on the model; confidence is self-reported, not calibrated.
- Don't paste confidential client data into a third-party API without approval.
- No persistence in v1 (briefs live in session state; export to save).

## Roadmap
1. Evaluation set of 20-30 real (anonymised) inquiries with reviewer scoring.
2. Multi-stage pipeline / LangGraph if evals justify it.
3. Save briefs, history, CRM/Jira export.
4. Streaming UI, language support (Hinglish/Hindi inquiries).
