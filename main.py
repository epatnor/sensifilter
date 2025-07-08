# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import tempfile
import base64
from io import BytesIO
from sensifilter.analyze import analyze_image
from PIL import Image

app = FastAPI()

DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# Serve static files (e.g. index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html as the root
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Image analysis endpoint
@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # ✅ Run analysis with settings
        result = analyze_image(tmp_path, DEFAULT_SETTINGS)
        os.remove(tmp_path)

        # 🧠 Convert annotated image to base64
        annotated = result.pop("annotated_image", None)
        if isinstance(annotated, Image.Image):
            buffer = BytesIO()
            annotated.save(buffer, format="PNG")
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            result["annotated_base64"] = encoded

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
