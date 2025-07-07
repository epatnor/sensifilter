# testnice.py

from nicegui import ui
import os
from sensifilter import analyze_image
from PIL import Image
import json

os.makedirs("temp", exist_ok=True)

default_settings = {
    "confidence_threshold": 0.5,
    "min_skin_percent": 15,
    "min_people": 1,
    "enable_scene_filter": True,
    "enable_keyword_filter": True,
    "enable_caption_filter": True,
}

# === GLOBAL UI ELEMENTS ===
ui.dark_mode()

with ui.container().style("max-width: 1100px; margin: 0 auto; padding: 30px;"):

    ui.markdown("## 🧪 Sensifilter Test UI (NiceGUI)")

    with ui.row().classes("gap-8"):
        with ui.column():
            ui.upload(on_upload=lambda e: handle_upload(e), label="Upload Image", auto_upload=True)
            preview_image = ui.image().style("max-width: 100%; margin-top: 8px")
            ui.label("Original Image").style("margin-bottom: 20px;")

        with ui.column():
            annotated_image = ui.image().style("max-width: 100%; margin-top: 8px")
            ui.label("Annotated Image (with bounding boxes)").style("margin-bottom: 20px;")

    ui.separator().style("margin: 20px 0")

    info_box = ui.column().style("gap: 4px;")

    ui.markdown("### 🧾 Raw Result").style("margin-top: 30px")
    raw_result_box = ui.textarea().props("readonly").style("width: 100%; height: 250px; font-family: monospace")


# === ANALYSIS FUNCTION ===
def handle_upload(e):
    uploaded = e.content.read()
    temp_path = "temp/uploaded.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded)

    preview_image.set_source(temp_path)
    ui.notify("Analyzing...", type="info")

    try:
        result = analyze_image(temp_path, settings=default_settings)

        label = result.get("label", "-")
        caption = result.get("caption", ("-", 0))
        scene = result.get("scene", "-")
        skin = round(result.get("skin_percent", 0), 2)
        human = result.get("contains_human", "-")
        pose = result.get("pose", "-")

        info_box.clear()
        with info_box:
            ui.label(f"🔖 Label: {label}")
            ui.label(f"📝 Caption: {caption[0]} ({caption[1]})")
            ui.label(f"🌄 Scene: {scene}")
            ui.label(f"🧍‍♀️ Pose: {pose}")
            ui.label(f"🟤 Skin %: {skin}%")
            ui.label(f"✅ Human detected: {human}")

        annotated = result.get("annotated_image")
        if annotated is not None:
            annotated_path = "temp/annotated.jpg"
            Image.fromarray(annotated).save(annotated_path)
            annotated_image.set_source(annotated_path)
        else:
            annotated_image.set_source("")

        raw_result_box.value = json.dumps(result, indent=2)

    except Exception as err:
        ui.notify(f"Error: {err}", type="negative")


ui.run(title="Sensifilter UI", reload=False, port=8080)
