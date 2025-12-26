from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models import VideoAnalysisResult
from app.vision.detection import analyze_video_file
from app.agents.triage_agent import summarize_person_presence
from app.agents.guidance_agent import generate_guidance
 

app = FastAPI(title="Smart Visual Guard API", version="0.3.0")


@app.get("/")
def root():
    return {"message": "Smart Visual Guard backend is running."}


@app.post("/analyze-video", response_model=VideoAnalysisResult)
async def analyze_video(
    file: UploadFile = File(...),
    frame_stride: int = 10,
    max_frames: int = 300,
    person_conf_threshold: float = 0.5,
):
    """
    API layer:
    - Accept upload
    - Save to temp file
    - Call vision.analyze_video_file
    - Return JSON
    """

    # Basic file extension check
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save uploaded file to a temporary location
    try:
        suffix = "." + file.filename.split(".")[-1]
    except Exception:
        suffix = ".mp4"

    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    contents = await file.read()
    temp_video.write(contents)
    temp_video.flush()
    temp_path = temp_video.name

    try:
        result_obj = analyze_video_file(
            temp_path=temp_path,
            frame_stride=frame_stride,
            max_frames=max_frames,
            person_conf_threshold=person_conf_threshold,
        )
        # 🔹 Triage: compute summary from events
        summary = summarize_person_presence(result_obj)
        result_obj.summary = summary

        # 🔹 Guidance: generate human-friendly advice (mode can be parameterized later)
        guidance = generate_guidance(summary, mode="intrusion")
        result_obj.guidance = guidance
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content=result_obj.model_dump())
