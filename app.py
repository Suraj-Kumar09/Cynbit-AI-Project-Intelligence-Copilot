"""Streamlit UI for Cynbit AI Project Intelligence Copilot."""
import streamlit as st
from dotenv import load_dotenv

from pipeline import AnalysisError, analyze_inquiry
from schemas import MAX_INQUIRY_CHARS, brief_to_markdown

load_dotenv()

SAMPLES = {
    "E-commerce AI assistant": "We need an AI assistant for our e-commerce website that answers customer questions and tracks orders.",
    "Invoice automation": "Our finance team manually enters supplier invoices into our ERP. We want this automated.",
    "SaaS dashboard": "We want to build a multi-tenant analytics dashboard for gyms, hosted on AWS, with subscription billing.",
}

st.set_page_config(page_title="Project Intelligence Copilot", page_icon="🧭", layout="wide")
st.title("🧭 Cynbit AI Project Intelligence Copilot")
st.caption("Turn a raw client inquiry into a structured project brief. Output is a draft for human review.")

with st.sidebar:
    st.header("Samples")
    for name, text in SAMPLES.items():
        if st.button(name, use_container_width=True):
            st.session_state["inquiry"] = text

inquiry = st.text_area("Client inquiry", key="inquiry", height=160, max_chars=MAX_INQUIRY_CHARS)
c1, c2 = st.columns(2)
budget = c1.text_input("Budget (optional)")
timeline = c2.text_input("Timeline (optional)")

if st.button("Analyze inquiry", type="primary"):
    try:
        with st.spinner("Analyzing..."):
            st.session_state["brief"] = analyze_inquiry(inquiry, budget, timeline)
    except AnalysisError as e:
        st.session_state.pop("brief", None)
        st.error(str(e))

brief = st.session_state.get("brief")
if brief:
    st.subheader(brief.category_label)
    st.write(" · ".join(c.value for c in brief.categories), f"| Confidence: {brief.confidence.value}")
    st.write(brief.summary)

    t1, t2, t3, t4 = st.tabs(["Requirements", "Questions", "Approach & Architecture", "Risks & Next steps"])
    with t1:
        st.markdown("**Objectives**\n" + "\n".join(f"- {x}" for x in brief.objectives))
        st.markdown("**Functional**\n" + "\n".join(f"- {x}" for x in brief.functional_requirements))
        st.markdown("**Non-functional**\n" + "\n".join(f"- {x}" for x in brief.non_functional_requirements))
        st.markdown("**Constraints**\n" + "\n".join(f"- {x}" for x in brief.constraints))
        st.markdown("**Missing information**\n" + "\n".join(f"- {x}" for x in brief.missing_information))
    with t2:
        for q in brief.clarifying_questions:
            st.markdown(f"**[{q.priority.value}]** {q.question}\n\n_{q.why_it_matters}_")
    with t3:
        st.write(brief.suggested_approach)
        st.markdown("**Components**\n" + "\n".join(f"- {x}" for x in brief.architecture.components))
        st.markdown(f"**Data flow:** {brief.architecture.data_flow}")
    with t4:
        for r in brief.risks:
            st.markdown(f"**[{r.severity.value}]** {r.risk}\n\n_Mitigation: {r.mitigation}_")
        st.markdown("**Next steps**\n" + "\n".join(f"- {x}" for x in brief.next_steps))

    d1, d2 = st.columns(2)
    d1.download_button("⬇ Export Markdown", brief_to_markdown(brief), "project_brief.md", "text/markdown")
    d2.download_button("⬇ Export JSON", brief.model_dump_json(indent=2), "project_brief.json", "application/json")
