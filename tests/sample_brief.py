SAMPLE_INPUT = "We need an AI assistant for our e-commerce website that answers customer questions and tracks orders."

SAMPLE_BRIEF = {
    "category_label": "AI chatbot and business automation",
    "categories": ["AI/ML", "Automation"],
    "summary": "Customer-facing assistant for Q&A and order tracking.",
    "objectives": ["Reduce support load", "Self-serve order tracking"],
    "functional_requirements": ["Customer Q&A", "Order tracking", "Integration with existing systems"],
    "non_functional_requirements": [],
    "constraints": [],
    "missing_information": ["E-commerce platform", "Order API availability", "Expected traffic"],
    "clarifying_questions": [
        {"question": "Which e-commerce platform do you use?", "why_it_matters": "Decides integration method", "priority": "High"}
    ],
    "suggested_approach": "LLM + RAG + order API integration",
    "architecture": {"components": ["Chat widget", "LLM gateway", "Vector store", "Order API adapter"], "data_flow": "Widget -> backend -> RAG/Order API -> LLM -> widget"},
    "risks": [{"risk": "Hallucinated order status", "severity": "High", "mitigation": "Answer order data only from API, never from LLM memory"}],
    "next_steps": ["Gather requirements before finalizing the architecture"],
    "confidence": "Medium",
}
