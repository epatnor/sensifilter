# app_gradio.py

import cv2
import gradio as gr
from sensifilter import analyze

# === Globala inställningar ===
DEFAULT_SETTINGS = {
    "enable_scene_filter": True,
    "enable_caption_filter": True,
    "enable_keyword_filter": True,
}

def run_analysis(image_path):
    print(f"📷 Received image: {image_path}")
    result = analyze.analyze_image(image_path, DEFAULT_SETTINGS)

    # === Läs in originalbild som NumPy-array (RGB) ===
    try:
        original = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    except:
        original = None

    annotated = result.get("annotated_image")

    # === Extrahera övriga resultat ===
    caption_text = result.get("caption", [""])[0]
    scene = result.get("scene", "")
    try:
        skin_percent = round(result.get("skin_percent", 0), 2)
    except:
        skin_percent = 0.0
    pose = result.get("pose", "")
    contains_human = result.get("contains_human", False)
    label = result.get("label", "")

    return (
        original,
        annotated,
        label,
        caption_text,
        scene,
        skin_percent,
        pose,
        contains_human,
        result
    )

with gr.Blocks(title="Sensifilter Analyzer") as demo:
    gr.Markdown("🧪 **Sensifilter Analyzer (Gradio Edition)**")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="📤 Upload image", type="filepath")
            run_button = gr.Button("Run Analysis", variant="primary")

        with gr.Column():
            image_original = gr.Image(label="🖼 Original", type="numpy")
            image_annotated = gr.Image(label="🎯 Annotated", type="numpy")

    with gr.Row():
        label_output = gr.Label(label="Label")
        caption_output = gr.Textbox(label="Caption")
        scene_output = gr.Textbox(label="Scene")
        skin_output = gr.Number(label="Skin %")
        pose_output = gr.Textbox(label="Pose")
        human_output = gr.Checkbox(label="Contains Human")

    full_output = gr.JSON(label="📋 Full Raw Result", visible=True)

    run_button.click(
        fn=run_analysis,
        inputs=[image_input],
        outputs=[
            image_original,
            image_annotated,
            label_output,
            caption_output,
            scene_output,
            skin_output,
            pose_output,
            human_output,
            full_output
        ]
    )

if __name__ == "__main__":
    print("✅ Environment ready. Launching UI...")
    demo.launch()
