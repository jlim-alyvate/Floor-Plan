# app.py

import streamlit as st
from floorplan import generate_double_corridor_plan, render_svg
import io
import base64

st.title("Professional Hotel Floor Plan Generator with Room Template")

with st.sidebar:
    st.header("Input Parameters")
    total_width = st.number_input("Floor Width (meters)", 10.0, 100.0, 30.0)
    total_height = st.number_input("Floor Height (meters)", 10.0, 100.0, 20.0)
    room_width = st.number_input("Room Width (meters)", 2.0, 10.0, 3.0)
    room_depth = st.number_input("Room Depth (meters)", 2.0, 10.0, 5.0)
    corridor_width = st.number_input("Corridor Width (meters)", 1.0, 5.0, 2.0)
    uploaded_img = st.file_uploader("Upload Template Room Image", type=["png", "jpg", "jpeg"])

# Convert uploaded image to base64 URI
room_img_url = None
if uploaded_img:
    room_img_bytes = uploaded_img.read()
    encoded_img = base64.b64encode(room_img_bytes).decode()
    mime_type = uploaded_img.type
    room_img_url = f"data:{mime_type};base64,{encoded_img}"

if st.button("Generate Floor Plan"):
    units = generate_double_corridor_plan(
        total_width, total_height, room_width, room_depth, corridor_width
    )
    svg_output = render_svg(units, total_width, total_height, room_image_url=room_img_url)

    st.components.v1.html(svg_output, height=600, scrolling=True)

    svg_bytes = svg_output.encode('utf-8')
    st.download_button("Download SVG", data=svg_bytes, file_name="floorplan.svg", mime="image/svg+xml")
