# app.py

import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import io
import base64
from PIL import Image

st.title("Hotel Floor Plan Generator (Room Image-Controlled Layout)")

with st.sidebar:
    st.header("Floor Parameters")
    total_width = st.number_input("Total Floor Width (m)", 10.0, 100.0, 30.0)
    total_height = st.number_input("Total Floor Height (m)", 10.0, 100.0, 20.0)
    corridor_width = st.number_input("Corridor Width (m)", 1.0, 5.0, 2.0)

    st.header("Room Template Image")
    uploaded_img = st.file_uploader("Upload Room Plan Image", type=["png", "jpg", "jpeg"])

    manual_entry = st.checkbox("Manually specify room dimensions", value=True)

    if manual_entry:
        room_width = st.number_input("Room Width (m)", 2.0, 10.0, 3.0)
        room_depth = st.number_input("Room Depth (m)", 2.0, 10.0, 5.0)
    else:
        scale_factor = st.number_input("Scale factor (1 = 1m per pixel)", 0.01, 100.0, 0.05)

room_img_url = None
room_aspect_ratio = (3.0, 5.0)  # fallback

if uploaded_img:
    if not manual_entry:
        img = Image.open(uploaded_img)
        width_px, height_px = img.size
        room_width = width_px * scale_factor
        room_depth = height_px * scale_factor

    room_aspect_ratio = (room_width, room_depth)

    room_img_bytes = uploaded_img.read()
    encoded_img = base64.b64encode(room_img_bytes).decode()
    mime_type = uploaded_img.type
    room_img_url = f"data:{mime_type};base64,{encoded_img}"

if st.button("Generate Floor Plan"):
    units, room_w, room_d = generate_auto_scaled_plan(
        total_width, total_height, room_aspect_ratio, corridor_width
    )
    svg_output = render_svg(units, total_width, total_height, room_image_url=room_img_url, room_w=room_w, room_d=room_d)

    st.components.v1.html(svg_output, height=600, scrolling=True)
    svg_bytes = svg_output.encode('utf-8')
    st.download_button("Download SVG", data=svg_bytes, file_name="floorplan.svg", mime="image/svg+xml")
