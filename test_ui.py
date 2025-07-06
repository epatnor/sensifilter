import streamlit as st
from sensifilter.analyze import analyze_image

st.set_page_config(page_title="Sensifilter Test UI", layout="centered")
st.title("🧪 Sensifilter")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image("temp.jpg", caption="Selected image", use_column_width=True)
    st.write("Analyzing...")

    result = analyze_image("temp.jpg")
    st.write(f"**Label:** `{result['label']}`")
    st.write(f"**Caption:** {result['caption']}")
    st.write(f"**Scene:** {result.get('scene')}")
    st.write(f"**Skin %:** {result.get('skin_percent')}")

