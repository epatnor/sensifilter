# test_ui.py

import streamlit as st
from sensifilter import analyze_image
import os
import cv2
from PIL import Image

st.set_page_config(page_title="Sensifilter Test UI", layout="centered")
st.title("🧪 Sensifilter Image Analyzer")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # === Visa båda bilder efter analys ===
    st.markdown("### Analyzing...")

    # 🔧 Standardinställningar för Sensifilter
    default_settings = {
        "confidence_threshold": 0.5,
        "min_skin_percent": 15,
        "min_people": 1,
        "min_skin_human_ratio": 0.4,
        "enable_scene_filter": True,
        "enable_keyword_filter": True,
        "enable_caption_filter": True,
    }

    try:
        result = analyze_image(temp_path, settings=default_settings)

        # === Visa bilder sida vid sida ===
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Original Image**")
            st.image(temp_path, use_column_width=True)

        with col2:
            st.markdown("**Detected Bounding Boxes**")
            if "annotated_image" in result:
                annotated_rgb = cv2.cvtColor(result["annotated_image"], cv2.COLOR_BGR2RGB)
                st.image(Image.fromarray(annotated_rgb), use_column_width=True)
            else:
                st.info("No bounding boxes found.")

        st.markdown("### 🔍 Analysis Result")
        st.write(f"**Label:** `{result.get('label', '-')}`")

        caption = result.get("caption", "-")
        if isinstance(caption, tuple):
            st.write(f"**Caption:** {caption[0]} ({caption[1]})")
        else:
            st.write(f"**Caption:** {caption}")

        st.write(f"**Scene:** {result.get('scene', '-')}")
        st.write(f"**Pose:** {result.get('pose', '-')}")
        st.write(f"**Skin % (Total):** {result.get('skin_percent', 0):.2f}%")
        st.write(f"**Skin Ratio (Human):** {result.get('max_skin_ratio', 0):.2f}")
        st.write(f"**Contains human:** {result.get('contains_human', '-')}")

        st.markdown("### 🧾 Raw result")
        st.json(result)

    except Exception as e:
        st.error(f"❌ An error occurred during analysis:\n\n{e}")

    os.remove(temp_path)
