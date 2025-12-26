# YOLO + fire/baby/intrusion logic

from typing import List

import cv2
import tempfile
from ultralytics import YOLO

from app.models import PersonEvent, VideoAnalysisResult


# Load YOLO model once for all calls
yolo_model = YOLO("yolov8n.pt")


def analyze_video_file(
    temp_path: str,
    frame_stride: int = 10,
    max_frames: int = 300,
    person_conf_threshold: float = 0.5,
) -> VideoAnalysisResult:
    """
    Core vision logic:
    - Open video at temp_path
    - Sample frames
    - Run YOLO
    - Return VideoAnalysisResult with person events only
    """

    cap = cv2.VideoCapture(temp_path)

    if not cap.isOpened():
        raise RuntimeError("Failed to open video file")

    total_frames = 0
    processed_frames = 0
    events: List[PersonEvent] = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        # Only process every Nth frame
        if total_frames % frame_stride != 0:
            continue

        processed_frames += 1
        if processed_frames > max_frames:
            break

        # Run YOLO on this frame
        results = yolo_model(frame, verbose=False)
        result = results[0]
        boxes = result.boxes

        persons_in_frame = 0
        max_conf = 0.0

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = result.names.get(cls_id, str(cls_id))

                if label == "person" and conf >= person_conf_threshold:
                    persons_in_frame += 1
                    if conf > max_conf:
                        max_conf = conf

        if persons_in_frame > 0:
            events.append(
                PersonEvent(
                    frame_index=total_frames,
                    persons=persons_in_frame,
                    max_confidence=max_conf,
                )
            )

    cap.release()

    return VideoAnalysisResult(
        total_frames=total_frames,
        processed_frames=processed_frames,
        events=events,
    )
