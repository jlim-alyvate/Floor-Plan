# app.py
import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64

st.set_page_config(layout="wide")
st.title("Modular Floor Plan Generator")

# Sidebar inputs
with st.sidebar:
    st.header("Floor Settings")
    total_width = st.number_input("Total Floor Width (m)", min_value=10.0, value=30.0)
    total_height = st.number_input("Total Floor Height (m)", min_value=10.0, value=30.0)

    st.header("Room Settings")
    room_width = st.number_input("Room Width (m)", min_value=2.0, value=3.0)
    room_depth = st.number_input("Room Depth (m)", min_value=2.0, value=5.0)

    st.header("Corridor Settings")
    corridor_width = st.number_input("Corridor Width (m)", min_value=1.0, value=2.0)

    st.header("Upload Room Template")
    room_image = st.file_uploader("Upload room image (PNG or JPEG)", type=["png", "jpg", "jpeg"])

# Image conversion to base64
image_url = None
if room_image is not None:
    image_data = room_image.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    image_format = "jpeg" if room_image.type == "image/jpeg" else "png"
    image_url = f"data:image/{image_format};base64,{image_base64}"

# Generate layout
st.subheader("Generated Floor Plan")
with st.spinner("Generating floor plan..."):
    units, w, d = generate_auto_scaled_plan(total_width, total_height, (room_width, room_depth), corridor_width)
    svg = render_svg(units, total_width, total_height, image_url, w, d)
    st.image(svg, use_container_width=True)

    with st.expander("Show SVG Output"):
        st.code(svg)
