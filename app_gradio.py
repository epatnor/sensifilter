import cv2
import gradio as gr
from sensifilter import analyze

DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

STEP_NAMES = [
    "Captioning",
    "Keyword Matching",
    "Scene Classification",
    "Pose Detection",
    "YOLO & Skin Detection",
]

def run_analysis(image_path):
    print(f"📷 Received image: {image_path}")
    result = analyze.analyze_image(image_path, DEFAULT_SETTINGS)

    annotated = result.get("annotated_image")
    if annotated is None:
        import numpy as np
        annotated = np.zeros((100, 100, 3), dtype=np.uint8)

    caption_data = result.get("caption", ("", 0.0))
    if not isinstance(caption_data, (tuple, list)) or len(caption_data) < 2:
        caption_text = str(caption_data) if caption_data else ""
        blip_confidence = 0.0
    else:
        caption_text = caption_data[0] or ""
        blip_confidence = caption_data[1] if isinstance(caption_data[1], (float, int)) else 0.0

    scene = result.get("scene", "")
    pose = result.get("pose", "")
    contains_human = result.get("contains_human", False)
    label = result.get("label", "")
    yolo_skipped = result.get("yolo_skipped", False)

    try:
        boxes = result.get("skin_human_boxes", [])
        total_pixels = 0
        total_skin_pixels = 0
        for b in boxes:
            x1, y1, x2, y2 = b["box"]
            area = max((x2 - x1), 1) * max((y2 - y1), 1)
            skin_ratio = b.get("skin_ratio", 0)
            skin_pixels = skin_ratio * area
            total_pixels += area
            total_skin_pixels += skin_pixels
        skin_percent = round((total_skin_pixels / total_pixels) * 100, 2) if total_pixels > 0 else 0.0
    except:
        skin_percent = 0.0

    # Konvertera timings till vanliga python-typer för säker HTML-rendering i Gradio
    timings = result.get("timings", {})
    timings_clean = {str(k): float(v) if isinstance(v, (float, int)) else 0.0 for k, v in timings.items()}

    return (
        annotated,
        label,
        caption_text,
        scene,
        skin_percent,
        pose,
        contains_human,
        blip_confidence,
        yolo_skipped,
        result,
        timings_clean,
    )


def label_to_badge(label):
    colors = {
        "safe": "#4CAF50",
        "sensitive": "#F44336",
        "review": "#FF9800",
    }
    color = colors.get(label.lower(), "#757575")
    return f"""<span style="
        background-color: {color};
        color: white;
        padding: 6px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-family: monospace;
        display: inline-block;
        min-width: 80px;
        text-align: center;
    ">{label.upper()}</span>"""


def render_pipeline(timings, label):
    label_lc = label.lower()
    if label_lc == "safe":
        safe_index = len(STEP_NAMES)
    elif label_lc == "review":
        safe_index = len(STEP_NAMES) - 1
    else:
        safe_index = len(STEP_NAMES) - 2

    html_lines = []
    for i, step in enumerate(STEP_NAMES):
        passed = i < safe_index
        color = "#4CAF50" if passed else "#888888"
        icon = "✅" if passed else "⏺️"
        timing_key = step.lower().replace(" & ", "_").replace(" ", "_")
        timing = timings.get(timing_key, 0.0)
        html_lines.append(
            f'<div style="color:{color}; font-weight:600; margin-bottom:4px;">'
            f'{icon} {step} <small style="font-weight:normal; color:#555;">({timing:.2f}s)</small></div>'
        )
    return "<br>".join(html_lines)


with gr.Blocks(title="Sensifilter Analyzer") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="filepath")
            run_button = gr.Button("Run Analysis", variant="primary")

        with gr.Column():
            image_annotated = gr.Image(label="🎯 Annotated", type="numpy")

        with gr.Column(scale=1):
            pipeline_status = gr.HTML(label="Pipeline Progress")

    with gr.Row():
        label_output = gr.HTML(label="Label")
        caption_output = gr.Textbox(label="Caption")
        scene_output = gr.Textbox(label="Scene")
        skin_output = gr.Number(label="Skin %")
        pose_output = gr.Textbox(label="Pose")
        human_output = gr.Checkbox(label="Contains Human")
        blip_conf_output = gr.Number(label="BLIP Confidence")
        yolo_skipped_output = gr.Checkbox(label="YOLO Skipped")

    full_output = gr.JSON(label="📋 Full Raw Result", visible=False)
    toggle_button = gr.Button("Toggle Raw Result")

    toggle_button.click(
        lambda visible: not visible,
        inputs=full_output,
        outputs=full_output
    )

    def postprocess(outputs):
        annotated = outputs[0]
        label = outputs[1]
        timings = outputs[-1]
        return (
            annotated,
            label_to_badge(label),
            *outputs[2:-2],
            outputs[-2],  # full raw result JSON
            render_pipeline(timings, label),
        )

    run_button.click(
        fn=run_analysis,
        inputs=[image_input],
        outputs=[
            image_annotated,
            label_output,
            caption_output,
            scene_output,
            skin_output,
            pose_output,
            human_output,
            blip_conf_output,
            yolo_skipped_output,
            full_output,
            pipeline_status,
        ],
        postprocess=postprocess
    )

if __name__ == "__main__":
    print("✅ Environment ready. Launching UI...")
    demo.launch()
