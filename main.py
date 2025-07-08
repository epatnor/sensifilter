# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import tempfile
from sensifilter.analyze import analyze_image

app = FastAPI()

# Default pipeline settings
DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# Serve static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the frontend page at root
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Endpoint for image analysis
@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = analyze_image(tmp_path, DEFAULT_SETTINGS)
        os.remove(tmp_path)

        # Remove unserializable items
        result.pop("annotated_image", None)

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Run dev server
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
