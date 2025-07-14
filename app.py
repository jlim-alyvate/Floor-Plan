import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64

st.set_page_config(layout="wide")
st.title("Modular Floor Plan Generator")

# Sidebar: Room metadata uploader and clickable selector
with st.sidebar:
    st.header("Upload Room Template")
    uploaded_image = st.file_uploader("Upload Room Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

    door_wall = st.selectbox("Select Door Wall", ["Top", "Bottom", "Left", "Right"])
    window_wall = st.selectbox("Select Window Wall", ["Top", "Bottom", "Left", "Right"])

    st.header("Floor Settings")
    total_width = st.number_input("Total Floor Width (m)", min_value=10.0, value=30.0)
    total_height = st.number_input("Total Floor Height (m)", min_value=10.0, value=30.0)

    st.header("Room Settings")
    room_width = st.number_input("Room Width (m)", min_value=2.0, value=3.0)
    room_depth = st.number_input("Room Depth (m)", min_value=2.0, value=5.0)

    corridor_width = st.number_input("Corridor Width (m)", min_value=1.0, value=2.0)

# Convert uploaded image to base64
image_url = None
if uploaded_image is not None:
    image_bytes = uploaded_image.read()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    image_format = "jpeg" if uploaded_image.type == "image/jpeg" else "png"
    image_url = f"data:image/{image_format};base64,{encoded}"

# Store room metadata for floorplan.py
room_metadata = {
    "door_wall": door_wall,
    "window_wall": window_wall
}

# Generate layout
st.subheader("Generated Floor Plan")
with st.spinner("Generating floor plan..."):
    units, w, d = generate_auto_scaled_plan(
        total_width, total_height,
        (room_width, room_depth),
        corridor_width,
        room_metadata
    )
    svg = render_svg(units, total_width, total_height, image_url, w, d)
    st.image(svg, use_container_width=True)

    with st.expander("Show SVG Output"):
        st.code(svg)
