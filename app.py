# app.py
import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64
from PIL import Image
import io

st.set_page_config(layout="wide")
st.title("Floor Plan Generator with Door/Window Orientation")

# Sidebar inputs
st.sidebar.header("Layout Settings")
total_width = st.sidebar.slider("Total Width (m)", 20, 100, 50)
total_height = st.sidebar.slider("Total Height (m)", 20, 100, 50)
room_width = st.sidebar.slider("Room Width (m)", 2, 10, 3)
room_depth = st.sidebar.slider("Room Depth (m)", 2, 10, 5)
corridor_width = st.sidebar.slider("Corridor Width (m)", 1, 5, 2)

st.sidebar.header("Room Orientation")
door_wall = st.sidebar.selectbox("Select the wall for the DOOR", ["Top", "Bottom", "Left", "Right"])
window_wall = st.sidebar.selectbox("Select the wall for the WINDOW", ["Top", "Bottom", "Left", "Right"])

room_image = st.sidebar.file_uploader("Upload Room Template Image (JPEG or PNG)", type=["jpg", "jpeg", "png"])

room_image_url = None
if room_image:
    image = Image.open(room_image)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    room_image_url = f"data:image/png;base64,{encoded}"

if st.button("Generate Floor Plan"):
    with st.spinner("Generating layout..."):
        room_metadata = {"door_wall": door_wall, "window_wall": window_wall}
        units, rw, rd = generate_auto_scaled_plan(total_width, total_height, (room_width, room_depth), corridor_width, room_metadata)
        svg = render_svg(units, total_width, total_height, room_image_url, room_width, room_depth)
        st.image(svg, use_column_width=True)

    st.success("Floor plan generated!")
