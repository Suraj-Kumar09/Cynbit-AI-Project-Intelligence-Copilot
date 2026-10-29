import pytest
from pydantic import ValidationError

from schemas import MAX_INQUIRY_CHARS, InquiryInput, ProjectBrief, brief_to_markdown
from tests.sample_brief import SAMPLE_BRIEF, SAMPLE_INPUT


def test_valid_input_is_stripped():
    assert InquiryInput(inquiry=f"  {SAMPLE_INPUT}  ").inquiry == SAMPLE_INPUT


@pytest.mark.parametrize("bad", ["", "   ", "too short", "x" * (MAX_INQUIRY_CHARS + 1)])
def test_invalid_inputs_rejected(bad):
    with pytest.raises(ValidationError):
        InquiryInput(inquiry=bad)


def test_brief_validates_and_exports_markdown():
    md = brief_to_markdown(ProjectBrief.model_validate(SAMPLE_BRIEF))
    assert "AI chatbot and business automation" in md
    assert "Missing information" in md and "Order API availability" in md


def test_unknown_category_rejected():
    bad = {**SAMPLE_BRIEF, "categories": ["Blockchain"]}
    with pytest.raises(ValidationError):
        ProjectBrief.model_validate(bad)
