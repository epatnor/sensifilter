# app_gradio.py

import gradio as gr
from sensifilter import analyze_image
from PIL import Image

# === Default analysis settings ===
DEFAULT_SETTINGS = {
    "confidence_threshold": 0.5,
    "min_skin_percent": 15,
    "min_people": 1,
    "enable_scene_filter": True,
    "enable_keyword_filter": True,
    "enable_caption_filter": True,
}

def analyze(file: Image.Image):
    """
    Main Gradio handler. Accepts a PIL image, runs analysis,
    returns: preview image, result label, and metadata.
    """
    temp_path = "temp/uploaded.jpg"
    file.save(temp_path)

    result = analyze_image(temp_path, settings=DEFAULT_SETTINGS)

    # Format outputs
    annotated = result.get("annotated_image")
    label = result.get("label", "-")
    caption = result.get("caption", ("-", 0))[0]
    scene = result.get("scene", "-")
    skin_percent = round(result.get("skin_percent", 0), 2)
    pose = result.get("pose", "-")
    contains_human = result.get("contains_human", False)

    # Convert annotation to image
    if annotated is not None:
        annotated_pil = Image.fromarray(annotated)
    else:
        annotated_pil = None

    return (
        file,  # original
        annotated_pil,  # annotated
        label,
        caption,
        scene,
        skin_percent,
        pose,
        contains_human,
        result  # raw JSON
    )

# === Gradio UI ===
with gr.Blocks(title="Sensifilter UI") as demo:
    gr.Markdown("## 🧪 Sensifilter Analyzer (Gradio Edition)")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Upload Image")
            analyze_btn = gr.Button("Run Analysis", variant="primary")
        with gr.Column():
            output_orig = gr.Image(label="Original")
            output_annot = gr.Image(label="Annotated")

    with gr.Row():
        output_label = gr.Label(label="Label")
        output_caption = gr.Textbox(label="Caption", max_lines=1)
        output_scene = gr.Textbox(label="Scene", max_lines=1)
        output_skin = gr.Number(label="Skin %")
        output_pose = gr.Textbox(label="Pose", max_lines=1)
        output_human = gr.Checkbox(label="Contains Human")

    gr.Markdown("### 🧾 Full Raw Result")
    output_json = gr.JSON()

    analyze_btn.click(
        analyze,
        inputs=[input_image],
        outputs=[
            output_orig, output_annot, output_label,
            output_caption, output_scene, output_skin,
            output_pose, output_human, output_json
        ]
    )

# === Launch App ===
if __name__ == "__main__":
    demo.launch()
