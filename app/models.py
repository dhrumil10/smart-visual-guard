# # Pydantic models / schemas
# from typing import List, Optional
# from pydantic import BaseModel


# class PersonEvent(BaseModel):
#     frame_index: int
#     persons: int
#     max_confidence: float


# class PersonPresenceSummary(BaseModel):
#     has_person: bool
#     event_count: int
#     first_seen_frame: Optional[int]
#     last_seen_frame: Optional[int]
#     max_conf_overall: float
#     presence_ratio: float  # events / processed_frames
#     severity: str          # "none" | "low" | "medium" | "high"


# class VideoAnalysisResult(BaseModel):
#     total_frames: int
#     processed_frames: int
#     events: List[PersonEvent]
#     summary: Optional[PersonPresenceSummary] = None

from typing import List, Optional
from pydantic import BaseModel


class PersonEvent(BaseModel):
    frame_index: int
    persons: int
    max_confidence: float


class PersonPresenceSummary(BaseModel):
    has_person: bool
    event_count: int
    first_seen_frame: Optional[int]
    last_seen_frame: Optional[int]
    max_conf_overall: float
    presence_ratio: float  # events / processed_frames
    severity: str          # "none" | "low" | "medium" | "high"


class Guidance(BaseModel):
    title: str
    summary: str
    recommended_actions: List[str]
    notify_user: bool
    escalation_level: str  # "none" | "low" | "medium" | "high"


class VideoAnalysisResult(BaseModel):
    total_frames: int
    processed_frames: int
    events: List[PersonEvent]
    summary: Optional[PersonPresenceSummary] = None
    guidance: Optional[Guidance] = None
