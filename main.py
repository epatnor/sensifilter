# main.py

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import tempfile
from sensifilter import analyze

app = FastAPI()

# Serve static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("static/index.html")


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = analyze.analyze_image(tmp_path)
        os.unlink(tmp_path)

        # Return simplified JSON for frontend use
        return JSONResponse({
            "label": result.get("label", ""),
            "caption": result.get("caption", ["", 0.0])[0],
            "blip_conf": result.get("caption", ["", 0.0])[1],
            "scene": result.get("scene", ""),
            "pose": result.get("pose", ""),
            "contains_human": result.get("contains_human", False),
            "skin_percent": result.get("skin_percent", 0.0),
            "timings": result.get("timings", {}),
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    print("🚀 Launching on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
