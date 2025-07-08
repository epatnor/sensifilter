import cv2
import numpy as np
import gradio as gr
from sensifilter import analyze
from pipelineview import label_to_badge, render_pipeline, render_pipeline_preview

# Default inställningar för analys
DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# Statisk mockup för test/visning i UI
def render_pipeline_mockup():
    steps = [
        ("Captioning", 0.12, True),
        ("Keyword Matching", 0.08, True),
        ("Scene Classification", 0.15, False),
        ("Pose Detection", 0.07, False),
        ("YOLO & Skin Detection", 0.22, False),
    ]
    html_lines = []
    for step, time_sec, passed in steps:
        color = "#4CAF50" if passed else "#888888"
        icon = "✅" if passed else "⏺️"
        html_lines.append(
            f'<div style="color:{color}; font-weight:600; margin-bottom:4px;">'
            f'{icon} {step} <small style="font-weight:normal; color:#555;">({time_sec:.2f}s)</small></div>'
        )
    return "<br>".join(html_lines)

def run_analysis(image_path):
    print(f"📷 Received image: {image_path}")
    result = analyze.analyze_image(image_path, DEFAULT_SETTINGS)

    annotated = result.get("annotated_image")
    if annotated is None:
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
    except Exception:
        skin_percent = 0.0

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

with gr.Blocks(title="Sensifilter Analyzer") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="filepath")
            run_button = gr.Button("Run Analysis", variant="primary")

        with gr.Column():
            image_annotated = gr.Image(label="🎯 Annotated", type="numpy")

        # Här visar vi både pipeline-status från analys + statisk mockup-lista bredvid
        with gr.Column(scale=1):
            pipeline_status = gr.HTML(label="Pipeline Progress", value=render_pipeline_preview())
            gr.Markdown("### Static Mockup Pipeline")
            pipeline_mockup = gr.HTML(label="Pipeline Mockup", value=render_pipeline_mockup())

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

    def toggle_raw(visible):
        return gr.update(visible=not visible)

    toggle_button.click(
        toggle_raw,
        inputs=full_output,
        outputs=full_output,
    )

    def postprocess(outputs):
        try:
            annotated = outputs[0]
            if annotated is None:
                annotated = np.zeros((100, 100, 3), dtype=np.uint8)
            elif hasattr(annotated, 'convert'):  # PIL Image -> numpy
                annotated = np.array(annotated)
    
            label = outputs[1] or "unknown"
            timings = outputs[-1] or {}
    
            sanitized = []
            for o in outputs[2:-2]:
                sanitized.append(o if o is not None else "")
    
            pipeline_html = render_pipeline(timings, label)
    
            # Debug: kontrollera att vi har en sträng och att det ser ut som HTML
            print(f"DEBUG: pipeline_html type before conversion: {type(pipeline_html)}")
            if not isinstance(pipeline_html, str):
                pipeline_html = str(pipeline_html)
            print(f"DEBUG: pipeline_html preview:\n{pipeline_html[:200]}")
    
            return (
                annotated,
                label_to_badge(label),
                *sanitized,
                outputs[-2] or {},
                pipeline_html,
            )
        except Exception as e:
            print(f"❌ Postprocess error: {e}")
            return (
                np.zeros((100, 100, 3), dtype=np.uint8),
                label_to_badge("error"),
                *[""] * (len(outputs) - 4),
                {},
                "",
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
        postprocess=postprocess,
    )

if __name__ == "__main__":
    print("✅ Environment ready. Launching UI...")
    demo.launch()
