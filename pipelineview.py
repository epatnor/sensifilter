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

# Build an HTML list displaying the pipeline steps
def render_pipeline(timings, label):
    try:
        if not timings or not isinstance(timings, dict):
            timings = {}

        label_lc = (label or "").lower()
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
            key = step.lower().replace(" & ", "_").replace(" ", "_")
            time_sec = timings.get(key, 0.0)
            html_lines.append(
                f'<div style="color:{color}; font-weight:600; margin-bottom:4px;">'
                f'{icon} {step} <small style="font-weight:normal; color:#555;">({time_sec:.2f}s)</small></div>'
            )
        return "<br>".join(html_lines)

    except Exception as e:
        print(f"⚠️ render_pipeline error: {e}")
        return "<div style='color:red;'>⚠️ Pipeline rendering failed</div>"

# Return a neutral gray pipeline view for preview
def render_pipeline_preview():
    html_lines = []
    for step in STEP_NAMES:
        html_lines.append(
            f'<div style="color:#888888; font-weight:600; margin-bottom:4px;">'
            f'⏺️ {step} <small style="font-weight:normal; color:#555;">(0.00s)</small></div>'
        )
    return "<br>".join(html_lines)
