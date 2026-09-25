"""LangGraph workflow: extract -> assess severity/impact.

Uses Groq when GROQ_API_KEY is set, otherwise deterministic heuristics
so the UI demo and tests always work offline.
"""
import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from ..config import settings
from .document_parser import heuristic_extract, heuristic_severity
from .prompts import EXTRACTION_SYSTEM, SEVERITY_SYSTEM


class DeviationState(TypedDict):
    raw_text: str
    extracted: dict
    assessment: dict
    provider: str


def _groq_client():
    if not settings.groq_api_key:
        return None
    try:
        from groq import Groq

        return Groq(api_key=settings.groq_api_key)
    except Exception:
        return None


def _chat(client, system: str, user: str) -> tuple:
    """Call Groq with primary model, auto-retry with fallback model.

    Returns (content, model_used). Raises the last error if both fail.
    """
    last_err = None
    for model in (settings.groq_model, settings.groq_fallback_model):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content, model
        except Exception as e:  # e.g. model decommissioned, rate limit
            last_err = e
    raise last_err


def node_extract(state: DeviationState) -> dict:
    client = _groq_client()
    text = state["raw_text"][:12000]
    if client is None:
        return {"extracted": heuristic_extract(text), "provider": "heuristic-fallback"}
    try:
        content, model = _chat(client, EXTRACTION_SYSTEM, text)
        data = json.loads(content)
        merged = heuristic_extract(text)
        merged.update({k: str(v) for k, v in data.items() if k in merged})
        return {"extracted": merged, "provider": f"groq:{model}"}
    except Exception:
        return {"extracted": heuristic_extract(text), "provider": "heuristic-fallback"}


def node_assess(state: DeviationState) -> dict:
    client = _groq_client()
    extracted = state.get("extracted", {})
    if client is None:
        return {"assessment": heuristic_severity(extracted, state["raw_text"])}
    try:
        content, model = _chat(client, SEVERITY_SYSTEM, json.dumps(extracted))
        data = json.loads(content)
        sev = data.get("severity", "Minor")
        if sev not in ("Critical", "Major", "Minor"):
            sev = "Minor"
        return {"assessment": {
            "severity": sev,
            "impact_assessment": str(data.get("impact_assessment", "")),
            "capa_required": bool(data.get("capa_required", False)),
            "ai_reason": str(data.get("ai_reason", "")),
            "ai_confidence": float(data.get("ai_confidence", 0.7)),
        }, "provider": f"groq:{model}"}
    except Exception:
        return {"assessment": heuristic_severity(extracted, state["raw_text"])}


def build_graph():
    g = StateGraph(DeviationState)
    g.add_node("extract", node_extract)
    g.add_node("assess", node_assess)
    g.set_entry_point("extract")
    g.add_edge("extract", "assess")
    g.add_edge("assess", END)
    return g.compile()


_graph = build_graph()


def analyze_deviation(text: str) -> dict:
    result = _graph.invoke({"raw_text": text, "extracted": {}, "assessment": {}, "provider": "groq"})
    extracted = result.get("extracted", {})
    assessment = result.get("assessment", {})
    return {
        "extracted": extracted,
        "severity": assessment.get("severity", "Minor"),
        "impact_assessment": assessment.get("impact_assessment", ""),
        "ai_reason": assessment.get("ai_reason", ""),
        "ai_confidence": assessment.get("ai_confidence", 0.0),
        "capa_required": assessment.get("capa_required", False),
        "provider": result.get("provider", "groq"),
    }
