# app_gradio.py

import cv2
import gradio as gr
from sensifilter import analyze

# === Global settings ===
DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

# === Main analysis function ===
def run_analysis(image_path):
    print(f"📷 Received image: {image_path}")
    result = analyze.analyze_image(image_path, DEFAULT_SETTINGS)

    annotated = result.get("annotated_image")

    # Extract results
    caption_text = result.get("caption", [""])[0]
    scene = result.get("scene", "")
    pose = result.get("pose", "")
    contains_human = result.get("contains_human", False)
    label = result.get("label", "")
    blip_confidence = result.get("blip_confidence", 0.0)
    yolo_skipped = result.get("yolo_skipped", False)

    # Calculate total skin % from all boxes
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

# === UI setup ===
with gr.Blocks(title="Sensifilter Analyzer") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="filepath")
            run_button = gr.Button("Run Analysis", variant="primary")

        with gr.Column():
            image_annotated = gr.Image(label="🎯 Annotated", type="numpy")

    with gr.Row():
        label_output = gr.Label(label="Label")
        caption_output = gr.Textbox(label="Caption")
        scene_output = gr.Textbox(label="Scene")
        skin_output = gr.Number(label="Skin %")
        pose_output = gr.Textbox(label="Pose")
        human_output = gr.Checkbox(label="Contains Human")
        blip_conf_output = gr.Number(label="BLIP Confidence")
        yolo_skipped_output = gr.Checkbox(label="YOLO Skipped")

    full_output = gr.JSON(label="📋 Full Raw Result", visible=True)

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
    )

if __name__ == "__main__":
    print("✅ Environment ready. Launching UI...")
    demo.launch()
