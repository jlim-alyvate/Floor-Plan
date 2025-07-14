import streamlit as st
from PIL import Image
import io

def configure_room():
    st.sidebar.subheader("Room Configuration")

    uploaded_file = st.sidebar.file_uploader("Upload Room Template (JPEG or PNG)", type=["jpg", "jpeg", "png"])
    if not uploaded_file:
        return None, None, None, None

    door_wall = st.sidebar.radio("Select Door Wall", ["Top", "Bottom", "Left", "Right"], index=1)
    window_wall = st.sidebar.radio("Select Window Wall", ["Top", "Bottom", "Left", "Right"], index=0)

    rotation_angle = st.sidebar.slider("Rotate Room Image (°)", min_value=0, max_value=270, step=90, value=0)

    try:
        image = Image.open(uploaded_file)
        if rotation_angle != 0:
            image = image.rotate(-rotation_angle, expand=True)

        st.sidebar.image(image, caption=f"Rotated Room ({rotation_angle}°)", use_container_width=True)

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_url = "data:image/png;base64," + image_bytes.getvalue().hex()

        return image_url, door_wall, window_wall, rotation_angle
    except Exception as e:
        st.sidebar.error(f"Error loading image: {str(e)}")
        return None, None, None, None
