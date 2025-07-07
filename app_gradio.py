# app_gradio.py

import gradio as gr
import tempfile
import numpy as np
from sensifilter.analyze import analyze_image

# === App-inställningar ===
settings = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# === Gradio-funktion som anropar analyskedjan ===
def process_image(upload):
    if upload is None:
        return None, None, "", "", 0.0, "", False, {}, "No file uploaded"

    # Spara temporärt
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(upload.read())
        temp_path = tmp.name

    # Kör analys
    result = analyze_image(temp_path, settings)

    # Extrahera bilder (RGB → numpy → visningsbar)
    orig = result.get("original_image_rgb")
    annot = result.get("annotated_image")
    if orig is not None:
        orig = np.array(orig)
    if annot is not None:
        annot = np.array(annot)

    # Returnera till UI
    return (
        orig,
        annot,
        result.get("caption", [""])[0],
        result.get("scene", ""),
        round(result.get("skin_percent", 0.0), 2),
        result.get("pose", ""),
        result.get("contains_human", False),
        result.get("keywords", []),
        result,
    )

# === UI layout ===
with gr.Blocks(title="Sensifilter Analyzer (Gradio Edition)") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="file")
            run_btn = gr.Button("Run Analysis", elem_id="analyze_btn")
        with gr.Column():
            image_orig = gr.Image(label="🖼 Original", interactive=False)
            image_annot = gr.Image(label="📦 Annotated", interactive=False)

    with gr.Row():
        label_out = gr.Label(label="Label")
        caption_out = gr.Textbox(label="Caption")
        scene_out = gr.Textbox(label="Scene")
        skin_out = gr.Number(label="Skin %")
        pose_out = gr.Textbox(label="Pose")
        human_out = gr.Checkbox(label="Contains Human")

    keywords_out = gr.HighlightedText(label="🔑 Keywords")
    json_out = gr.Json(label="🪵 Full Raw Result", visible=True)

    run_btn.click(fn=process_image, inputs=[image_input], outputs=[
        image_orig, image_annot, caption_out, scene_out,
        skin_out, pose_out, human_out, keywords_out, json_out
    ])

# === Starta servern ===
if __name__ == "__main__":
    demo.launch()
