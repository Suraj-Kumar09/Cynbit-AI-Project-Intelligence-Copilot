"""Structured response + input validation for the Project Intelligence Copilot."""
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator

MIN_INQUIRY_CHARS = 20
MAX_INQUIRY_CHARS = 5000


class ProjectCategory(str, Enum):
    AI_ML = "AI/ML"
    SAAS = "SaaS"
    WEB = "Web Development"
    CLOUD = "Cloud"
    AUTOMATION = "Automation"
    OTHER = "Other"


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class InquiryInput(BaseModel):
    """Validated user input (empty / too short / too long checks)."""

    inquiry: str
    budget: str = ""
    timeline: str = ""

    @field_validator("inquiry")
    @classmethod
    def check_inquiry(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("Inquiry is empty.")
        if len(v) < MIN_INQUIRY_CHARS:
            raise ValueError(f"Inquiry is too short (min {MIN_INQUIRY_CHARS} characters).")
        if len(v) > MAX_INQUIRY_CHARS:
            raise ValueError(f"Inquiry is too long (max {MAX_INQUIRY_CHARS} characters).")
        return v

    @field_validator("budget", "timeline")
    @classmethod
    def strip_optional(cls, v: str) -> str:
        return (v or "").strip()[:200]


class ClarifyingQuestion(BaseModel):
    question: str
    why_it_matters: str
    priority: Priority = Priority.MEDIUM


class Risk(BaseModel):
    risk: str
    severity: Priority
    mitigation: str


class Architecture(BaseModel):
    components: List[str] = Field(default_factory=list)
    data_flow: str = ""


class ProjectBrief(BaseModel):
    category_label: str = Field(description="Short human label, e.g. 'AI chatbot and business automation'")
    categories: List[ProjectCategory]
    summary: str
    objectives: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    missing_information: List[str]
    clarifying_questions: List[ClarifyingQuestion]
    suggested_approach: str
    architecture: Architecture
    risks: List[Risk]
    next_steps: List[str]
    confidence: Priority = Priority.MEDIUM


def _bullets(items) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "- _None identified_"


def brief_to_markdown(b: ProjectBrief) -> str:
    """Render the brief as Markdown for human review / export."""
    cats = ", ".join(c.value for c in b.categories)
    qs = "\n".join(
        f"{n}. **[{q.priority.value}]** {q.question}  \n   _Why:_ {q.why_it_matters}"
        for n, q in enumerate(b.clarifying_questions, 1)
    ) or "- _None_"
    risks = "\n".join(
        f"- **[{r.severity.value}]** {r.risk}  \n  _Mitigation:_ {r.mitigation}" for r in b.risks
    ) or "- _None identified_"
    return f"""# Project Brief: {b.category_label}

> AI-generated draft for human review. Not a final scope or quote.

**Categories:** {cats}  
**Model confidence:** {b.confidence.value}

## Summary
{b.summary}

## Objectives
{_bullets(b.objectives)}

## Functional requirements
{_bullets(b.functional_requirements)}

## Non-functional requirements
{_bullets(b.non_functional_requirements)}

## Constraints
{_bullets(b.constraints)}

## Missing information
{_bullets(b.missing_information)}

## Clarifying questions
{qs}

## Suggested approach
{b.suggested_approach}

## Proposed architecture
{_bullets(b.architecture.components)}

**Data flow:** {b.architecture.data_flow or "_Not specified_"}

## Risks
{risks}

## Next steps
{_bullets(b.next_steps)}
"""
