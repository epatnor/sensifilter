# app_gradio.py

import cv2
import gradio as gr
from sensifilter import analyze

DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

def run_analysis(image_path):
    print(f"📷 Received image: {image_path}")
    result = analyze.analyze_image(image_path, DEFAULT_SETTINGS)

    annotated = result.get("annotated_image")

    caption_data = result.get("caption", ("", 0.0))
    caption_text = caption_data[0] if isinstance(caption_data, tuple) else ""
    blip_confidence = caption_data[1] if isinstance(caption_data, tuple) else 0.0

    scene = result.get("scene", "")
    pose = result.get("pose", "")
    contains_human = result.get("contains_human", False)
    label = result.get("label", "")
    yolo_skipped = result.get("yolo_skipped", False)

    # Beräkna total skin %
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
        result
    )

def label_to_badge(label):
    # Map label to color
    colors = {
        "safe": "#4CAF50",        # grön
        "sensitive": "#F44336",   # röd
        "review": "#FF9800",      # orange
    }
    color = colors.get(label.lower(), "#757575")  # grå som fallback
    # Return a HTML span badge
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

with gr.Blocks(title="Sensifilter Analyzer") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="filepath")
            run_button = gr.Button("Run Analysis", variant="primary")

        with gr.Column():
            image_annotated = gr.Image(label="🎯 Annotated", type="numpy")

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

    def toggle_raw_result(visible):
        return not visible

    toggle_button = gr.Button("Toggle Raw Result")

    toggle_button.click(toggle_raw_result, inputs=full_output, outputs=full_output)

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
        ],
        postprocess=lambda outputs: (
            outputs[0],  # annotated
            label_to_badge(outputs[1]),  # label as badge
            *outputs[2:]
        )
    )

if __name__ == "__main__":
    print("✅ Environment ready. Launching UI...")
    demo.launch()
