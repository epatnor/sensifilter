# test_ui.py

import streamlit as st
from sensifilter import analyze_image
import os

st.set_page_config(page_title="Sensifilter Test UI", layout="centered")
st.title("🧪 Sensifilter Image Analyzer")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(temp_path, caption="Selected image", use_column_width=True)
    st.markdown("### Analyzing...")

    # 🔧 Standardinställningar för Sensifilter
    default_settings = {
        "confidence_threshold": 0.5,
        "min_skin_percent": 15,
        "min_people": 1,
        "enable_scene_filter": True,
        "enable_keyword_filter": True,
        "enable_caption_filter": True,
    }

    try:
        result = analyze_image(temp_path, settings=default_settings)

        st.markdown("### 🔍 Analysis Result")
        st.write(f"**Label:** `{result.get('label', '-')}`")
        st.write(f"**Caption:** {result.get('caption', '-')}")        
        st.write(f"**Scene:** {result.get('scene', '-')}")
        st.write(f"**Pose:** {result.get('pose', '-')}")
        st.write(f"**Skin %:** {result.get('skin_percent', '-')}%")
        st.write(f"**Contains human:** {result.get('contains_human', '-')}")

        st.markdown("### 🧾 Raw result")
        st.json(result)

    except Exception as e:
        st.error(f"❌ An error occurred during analysis:\n\n{e}")

    # Valfritt: rensa temp
    os.remove(temp_path)
