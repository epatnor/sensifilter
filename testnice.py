# testnice.py

from nicegui import ui
import os
from sensifilter import analyze_image

# Skapa temporär mapp för uppladdade filer
os.makedirs("temp", exist_ok=True)

# Standardinställningar för analysen
default_settings = {
    "confidence_threshold": 0.5,
    "min_skin_percent": 15,
    "min_people": 1,
    "enable_scene_filter": True,
    "enable_keyword_filter": True,
    "enable_caption_filter": True,
}

# UI-komponenter vi refererar senare
preview_image = ui.image().style("max-width: 100%")
annotated_image = ui.image().style("max-width: 100%")
info_box = ui.column()
raw_result_box = ui.textarea(label="Raw Result", readonly=True).style("width: 100%; height: 200px; font-family: monospace")

# === Funktion som kör analysen ===
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

        # Annoterad bild om den finns
        annotated = result.get("annotated_image")
        if annotated is not None:
            from PIL import Image
            annotated_path = "temp/annotated.jpg"
            Image.fromarray(annotated).save(annotated_path)
            annotated_image.set_source(annotated_path)
        else:
            annotated_image.set_source("")

        import json
        raw_result_box.value = json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as err:
        ui.notify(f"Error: {err}", type="negative")

# === UI Layout ===
ui.markdown("## 🧪 Sensifilter Test UI (NiceGUI)").classes("text-2xl")

with ui.row().classes("gap-6"):
    with ui.column():
        ui.upload(on_upload=handle_upload, label="Upload Image", auto_upload=True)
        preview_image
        ui.label("Original Image")

    with ui.column():
        annotated_image
        ui.label("Annotated Image")

ui.separator()
info_box
ui.separator()
ui.markdown("### 🧾 Raw JSON Result")
raw_result_box

ui.run(title="Sensifilter UI", port=8080, reload=False)
