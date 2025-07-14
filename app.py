# app.py
import streamlit as st
from PIL import Image
import tempfile
import os
from floorplan import generate_auto_scaled_plan, render_svg
import base64

# App title and sidebar
st.set_page_config(layout="wide")
st.title("Modular Floor Plan Generator")

# Sidebar inputs
st.sidebar.header("1. Floor Dimensions")
total_width = st.sidebar.number_input("Total Floor Width (m)", value=30.0)
total_height = st.sidebar.number_input("Total Floor Height (m)", value=20.0)

st.sidebar.header("2. Room Dimensions")
room_width = st.sidebar.number_input("Room Width (m)", value=3.0)
room_depth = st.sidebar.number_input("Room Depth (m)", value=5.0)

st.sidebar.header("3. Corridor Width")
corridor_width = st.sidebar.number_input("Corridor Width (m)", value=2.0)

st.sidebar.header("4. Door & Window Configuration")
door_wall = st.sidebar.selectbox("Select Door Wall", ["Top", "Bottom", "Left", "Right"])
window_wall = st.sidebar.selectbox("Select Window Wall", ["Top", "Bottom", "Left", "Right"])

st.sidebar.header("5. Room Template Image")
image_file = st.sidebar.file_uploader("Upload Room Template Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

# Room metadata dictionary
room_metadata = {
    "door_wall": door_wall,
    "window_wall": window_wall
}

# Process image if uploaded
image_url = None
if image_file is not None:
    img = Image.open(image_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        img.save(tmp_file.name)
        image_url = f"data:image/png;base64,{base64.b64encode(tmp_file.read()).decode()}"

# Main output
if st.button("Generate Floor Plan"):
    units, room_w, room_d = generate_auto_scaled_plan(
        total_width,
        total_height,
        (room_width, room_depth),
        corridor_width,
        room_metadata=room_metadata
    )
    svg = render_svg(units, total_width, total_height, image_url, room_w, room_d)
    st.components.v1.html(svg, height=int(total_height*20)+100, scrolling=True)
    os.unlink(tmp_file.name) if image_file else None
