# room_configurator.py

import streamlit as st
from PIL import Image
import io

def configure_room_image(room_w, room_d):
    st.sidebar.header("Room Configuration")

    uploaded_file = st.sidebar.file_uploader("Upload Room Template (JPG or PNG)", type=["jpg", "jpeg", "png"])
    door_wall = st.sidebar.selectbox("Select Door Wall", ["Top", "Bottom", "Left", "Right"])
    window_wall = st.sidebar.selectbox("Select Window Wall (Opposite of Door)", ["Top", "Bottom", "Left", "Right"])

    rotation = st.sidebar.slider("Rotate Room Image (degrees)", 0, 270, 0, step=90)

    image_url = None
    preview = None

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGBA")
        image = image.rotate(rotation, expand=True)

        # Resize to fit room dimensions
        display_w, display_h = room_w * 100, room_d * 100
        image = image.resize((int(display_w), int(display_h)))
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        image_url = "data:image/png;base64," + io.BytesIO(byte_im).getvalue().hex()
        preview = image

    return {
        "image_url": image_url,
        "door_wall": door_wall,
        "window_wall": window_wall,
        "rotation": rotation,
        "image_preview": preview,
        "uploaded_file": uploaded_file
    }
