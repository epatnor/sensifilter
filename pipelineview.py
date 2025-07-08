# pipelineview.py

STEP_NAMES = [
    "Captioning",
    "Keyword Matching",
    "Scene Classification",
    "Pose Detection",
    "YOLO & Skin Detection",
]

def label_to_badge(label):
    """
    Return a colored badge HTML based on the label.
    """
    colors = {
        "safe": "#4CAF50",       # green
        "sensitive": "#F44336",  # red
        "review": "#FF9800",     # orange
    }
    color = colors.get(label.lower(), "#757575")  # fallback gray
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
    """
    Build an HTML list displaying the pipeline steps.
    Green check marks for passed steps, gray circles otherwise.
    Shows timings with two decimals.
    """
    if not timings:
        timings = {}

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
        key = step.lower().replace(" & ", "_").replace(" ", "_")
        time_sec = timings.get(key, 0.0)
        html_lines.append(
            f'<div style="color:{color}; font-weight:600; margin-bottom:4px;">'
            f'{icon} {step} <small style="font-weight:normal; color:#555;">({time_sec:.2f}s)</small></div>'
        )

    return "<br>".join(html_lines)

def render_pipeline_preview():
    """
    Return a neutral gray pipeline view for preview.
    Used before analysis runs.
    """
    html_lines = []
    for step in STEP_NAMES:
        html_lines.append(
            f'<div style="color:#888888; font-weight:600; margin-bottom:4px;">'
            f'⏺️ {step} <small style="font-weight:normal; color:#555;">(0.00s)</small></div>'
        )
    return "<br>".join(html_lines)
