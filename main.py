# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import tempfile
import uuid
from sensifilter.analyze import analyze_image
from PIL import Image

app = FastAPI()

DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# Mount static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve main UI
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Analyze image endpoint
@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Run analysis
        result = analyze_image(tmp_path, DEFAULT_SETTINGS)

        # Extract and save annotated image
        annotated_img = result.pop("annotated_image", None)
        if annotated_img:
            output_path = os.path.join("static", "annotated", f"{uuid.uuid4().hex}.jpg")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            annotated_img.save(output_path)
            result["annotated_url"] = "/" + output_path.replace("\\", "/")

        # Clean up
        os.remove(tmp_path)

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
