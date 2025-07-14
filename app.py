# app_v8.py
import streamlit as st
from floorplan_v8 import generate_auto_scaled_plan, render_svg

st.set_page_config(layout="wide")
st.title("🧱 Auto Floorplan Generator")

with st.sidebar:
    st.header("Settings")
    total_width = st.slider("Total Width (m)", 10, 60, 40)
    total_height = st.slider("Total Height (m)", 10, 60, 30)
    room_width = st.slider("Room Width (m)", 2, 10, 4)
    room_depth = st.slider("Room Depth (m)", 2, 10, 6)
    corridor_width = st.slider("Corridor Width (m)", 2, 6, 3)

    room_image = st.file_uploader("Upload Room Template (PNG/JPG)", type=["png", "jpg", "jpeg"])
    door_wall = st.selectbox("Door Wall", ["Top", "Bottom", "Left", "Right"])
    window_wall = st.selectbox("Window Wall", ["Top", "Bottom", "Left", "Right"])

if st.button("Generate Layout"):
    room_metadata = {"door_wall": door_wall, "window_wall": window_wall}
    room_aspect_ratio = (room_width, room_depth)
    units, room_w, room_d = generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width, room_metadata)

    image_url = None
    if room_image:
        import base64
        image_url = f"data:image/png;base64,{base64.b64encode(room_image.read()).decode()}"

    svg = render_svg(units, total_width, total_height, image_url, room_w, room_d)
    st.components.v1.html(svg, height=int(total_height * 20) + 50, scrolling=True)
