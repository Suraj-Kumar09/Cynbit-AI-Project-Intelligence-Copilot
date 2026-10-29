"""LLM pipeline: validate input -> call model -> parse JSON -> validate schema (with one retry)."""
import json
import os
import re
from typing import Optional

from pydantic import ValidationError

from prompts import SYSTEM_PROMPT, build_retry_prompt, build_user_prompt
from schemas import InquiryInput, ProjectBrief


class AnalysisError(Exception):
    """Raised when input is invalid or the model never returns a valid brief."""


def get_client():
    """OpenAI-compatible client (works with OpenAI, Gemini's OpenAI endpoint, etc.)."""
    from openai import OpenAI

    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise AnalysisError("LLM_API_KEY is not set. See .env.example.")
    return OpenAI(api_key=api_key, base_url=os.getenv("LLM_BASE_URL") or None)


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model reply.")
    return json.loads(text[start : end + 1])


def analyze_inquiry(
    inquiry: str,
    budget: str = "",
    timeline: str = "",
    client=None,
    model: Optional[str] = None,
    max_retries: int = 1,
) -> ProjectBrief:
    try:
        data = InquiryInput(inquiry=inquiry, budget=budget, timeline=timeline)
    except ValidationError as e:
        raise AnalysisError(e.errors()[0]["msg"].replace("Value error, ", "")) from e

    client = client or get_client()
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(data.inquiry, data.budget, data.timeline)},
    ]

    last_error = ""
    for _ in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
        except Exception as e:  # network / auth / quota
            raise AnalysisError(f"LLM request failed: {e}") from e

        raw = resp.choices[0].message.content or ""
        try:
            return ProjectBrief.model_validate(_extract_json(raw))
        except (ValueError, ValidationError) as e:
            last_error = str(e)
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": build_retry_prompt(last_error)},
            ]
    raise AnalysisError(f"Model did not return a valid brief after retries: {last_error[:300]}")
