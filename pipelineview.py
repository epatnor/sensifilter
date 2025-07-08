# pipelineview.py

STEP_NAMES = [
    "Captioning",
    "Keyword Matching",
    "Scene Classification",
    "Pose Detection",
    "YOLO & Skin Detection",
]

# Return a colored badge HTML based on the label
def label_to_badge(label):
    colors = {
        "safe": "#4CAF50",
        "sensitive": "#F44336",
        "review": "#FF9800",
    }
    color = colors.get(label.lower(), "#757575")
    return f'<span style="background-color:{color}; color:white; padding:6px 12px; border-radius:12px; font-weight:600; font-family:monospace;">{label.upper()}</span>'

# Build a flat HTML string of pipeline steps (no lists)
def render_pipeline(timings, label):
    try:
        if not isinstance(timings, dict):
            timings = {}

        label = (label or "").lower()
        if label == "safe":
            passed_index = len(STEP_NAMES)
        elif label == "review":
            passed_index = len(STEP_NAMES) - 1
        else:
            passed_index = len(STEP_NAMES) - 2

        html = ""
        for i, step in enumerate(STEP_NAMES):
            passed = i < passed_index
            color = "#4CAF50" if passed else "#888888"
            icon = "✅" if passed else "⏺️"
            key = step.lower().replace(" & ", "_").replace(" ", "_")
            sec = float(timings.get(key, 0.0))
            html += f'<div style="color:{color}; font-weight:600; margin-bottom:4px;">{icon} {step} <small style="font-weight:normal; color:#555;">({sec:.2f}s)</small></div>'
        return html

    except Exception as e:
        print(f"⚠️ render_pipeline error: {e}")
        return '<div style="color:red;">⚠️ Pipeline rendering failed</div>'

# Return a neutral gray preview before analysis
def render_pipeline_preview():
    html = ""
    for step in STEP_NAMES:
        html += f'<div style="color:#888888; font-weight:600; margin-bottom:4px;">⏺️ {step} <small style="font-weight:normal; color:#555;">(0.00s)</small></div>'
    return html
