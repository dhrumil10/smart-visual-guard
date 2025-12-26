# RAG-based guidance text

# app/agents/guidance_agent.py
from typing import List

from app.models import PersonPresenceSummary, Guidance


# Very simple in-memory "knowledge base" for later RAG
SAFETY_KB = [
    {
        "mode": "intrusion",
        "title": "Intruder safety basics",
        "content": (
            "If an intruder is suspected and you are not at home, do not return alone. "
            "Contact local authorities and avoid direct confrontation."
        ),
    },
    {
        "mode": "intrusion",
        "title": "Verifying suspicious activity",
        "content": (
            "Use a live camera feed or a trusted neighbor to visually confirm suspicious activity "
            "before taking further action."
        ),
    },
    {
        "mode": "normal",
        "title": "Non-critical detections",
        "content": (
            "If detections happen while you are home and expecting people, alerts can be treated as informational."
        ),
    },
]


def retrieve_relevant_docs(mode: str) -> List[str]:
    """
    Very simple mock retriever: return content snippets
    for the given mode ("intrusion", "normal", later: "baby_monitor", "fire").
    """
    return [item["content"] for item in SAFETY_KB if item["mode"] == mode]


def generate_guidance(summary: PersonPresenceSummary, mode: str = "intrusion") -> Guidance:
    """
    Generate high-level guidance from person presence summary.
    Currently rule-based, but shaped so we can swap in an LLM later.
    """

    # We don't actually use docs yet, but this is where RAG will plug in
    _docs = retrieve_relevant_docs(mode)

    # Case 1: no person at all
    if not summary.has_person:
        return Guidance(
            title="No person detected in video",
            summary="No human presence was detected in any processed frame.",
            recommended_actions=[
                "No immediate action is required.",
                "If this was unexpected, verify that your camera is positioned correctly."
            ],
            notify_user=False,
            escalation_level="none",
        )

    # Case 2: intrusion mode + medium/high severity -> escalate
    if mode == "intrusion" and summary.severity in ("medium", "high"):
        return Guidance(
            title="Possible intrusion detected",
            summary=(
                f"A person was detected in {summary.event_count} frame(s) "
                f"with maximum confidence {summary.max_conf_overall:.2f} "
                f"while the system is in intrusion mode."
            ),
            recommended_actions=[
                "Open your live camera feed to visually confirm the situation.",
                "If you are not at home and this is unexpected, contact local authorities.",
                "Save or export this video clip for future reference."
            ],
            notify_user=True,
            escalation_level="high" if summary.severity == "high" else "medium",
        )

    # Case 3: person detected but not clearly critical
    return Guidance(
        title="Person detected in monitored area",
        summary=(
            f"A person was detected in {summary.event_count} frame(s) "
            f"with maximum confidence {summary.max_conf_overall:.2f}."
        ),
        recommended_actions=[
            "Check if this activity was expected (family member, guest, etc.).",
            "If it was unexpected, review the recorded clip for more details."
        ],
        notify_user=True,
        escalation_level="low",
    )
