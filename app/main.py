# FastAPI entrypoint

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from ultralytics import YOLO
import tempfile
import cv2

app = FastAPI(title="Smart Visual Guard API", version="0.1.0")

# ---- Models ----

class DetectionEvent(BaseModel):
    frame_index: int
    persons: int
    info: str

class VideoAnalysisResult(BaseModel):
    total_frames: int
    processed_frames: int
    events: List[DetectionEvent]


# ---- Load YOLO model once at startup ----

# small model; good enough to begin
yolo_model = YOLO("yolov8n.pt")


# ---- Routes ----

@app.get("/")
def root():
    return {"message": "Smart Visual Guard backend is running."}


@app.post("/analyze-video", response_model=VideoAnalysisResult)
async def analyze_video(
    file: UploadFile = File(...),
    frame_stride: int = 10,
    max_frames: int = 300,
):
    """
    Accept a video file, sample frames, run YOLO, and return simple 'person' detection events.
    """

    # Validate file type (basic check)
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save uploaded file to a temp file
    try:
        suffix = "." + file.filename.split(".")[-1]
    except Exception:
        suffix = ".mp4"

    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    contents = await file.read()
    temp_video.write(contents)
    temp_video.flush()
    temp_path = temp_video.name

    cap = cv2.VideoCapture(temp_path)

    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Failed to open video file")

    total_frames = 0
    processed_frames = 0
    events: List[DetectionEvent] = []

    # Main processing loop
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

        persons_in_frame = 0
        boxes = result.boxes

        if boxes is not None:
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = result.names.get(cls_id, str(cls_id))

                if label == "person" and conf >= 0.5:
                    persons_in_frame += 1

        if persons_in_frame > 0:
            events.append(
                DetectionEvent(
                    frame_index=total_frames,
                    persons=persons_in_frame,
                    info=f"Detected {persons_in_frame} person(s) with YOLO",
                )
            )

    cap.release()

    result = VideoAnalysisResult(
        total_frames=total_frames,
        processed_frames=processed_frames,
        events=events,
    )

    return JSONResponse(content=result.model_dump())
