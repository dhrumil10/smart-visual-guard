# Decide severity, notify or not
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import VideoAnalysisResult, PersonPresenceSummary


def summarize_person_presence(result: VideoAnalysisResult) -> PersonPresenceSummary:
    """
    Take raw VideoAnalysisResult and compute a simple person presence summary.
    """

    event_count = len(result.events)
    has_person = event_count > 0

    if event_count == 0:
        return PersonPresenceSummary(
            has_person=False,
            event_count=0,
            first_seen_frame=None,
            last_seen_frame=None,
            max_conf_overall=0.0,
            presence_ratio=0.0,
            severity="none",
        )

    first_seen_frame = result.events[0].frame_index
    last_seen_frame = result.events[-1].frame_index
    max_conf_overall = max(e.max_confidence for e in result.events)

    # Avoid division by zero
    if result.processed_frames > 0:
        presence_ratio = event_count / result.processed_frames
    else:
        presence_ratio = 0.0

    # Very simple severity rule for now
    if not has_person:
        severity = "none"
    elif event_count < 3 and max_conf_overall < 0.8:
        severity = "low"
    elif event_count < 10:
        severity = "medium"
    else:
        severity = "high"

    return PersonPresenceSummary(
        has_person=has_person,
        event_count=event_count,
        first_seen_frame=first_seen_frame,
        last_seen_frame=last_seen_frame,
        max_conf_overall=max_conf_overall,
        presence_ratio=presence_ratio,
        severity=severity,
    )
