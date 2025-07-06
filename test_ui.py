import streamlit as st
from sensifilter.analyze import analyze_image
import os

st.set_page_config(page_title="Sensifilter Test UI", layout="centered")
st.title("🧪 Sensifilter Image Analyzer")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    temp_path = "temp_uploaded.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(temp_path, caption="Selected Image", use_column_width=True)
    st.write("Analyzing...")

    result = analyze_image(temp_path)

    st.markdown("### 🔍 Analysis Result")
    st.write(f"**Label:** `{result.get('label', '-')}`")
    st.write(f"**Caption:** {result.get('caption', '-')}")
    st.write(f"**Scene:** {result.get('scene', '-')}")
    st.write(f"**Pose:** {result.get('pose', '-')}")
    st.write(f"**Skin %:** {result.get('skin_percent', '-')}%")
    st.write(f"**Contains human:** {result.get('contains_human', '-')}")

    st.markdown("### 🧾 Raw result")
    st.json(result)

    os.remove(temp_path)
