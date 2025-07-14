import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64
import io
from PIL import Image

st.set_page_config(layout="wide")
st.title("Hotel Room Layout Generator")

col1, col2 = st.sidebar.columns(2)
total_width = col1.number_input("Total Floor Width (m)", 10, 100, 40)
total_height = col2.number_input("Total Floor Depth (m)", 10, 100, 30)

room_col1, room_col2 = st.sidebar.columns(2)
room_width = room_col1.number_input("Room Width (m)", 2, 10, 3)
room_depth = room_col2.number_input("Room Depth (m)", 2, 10, 5)

corridor_width = st.sidebar.slider("Corridor Width (m)", 1, 5, 2)

door_wall = st.sidebar.selectbox("Door Wall", ["Top", "Bottom", "Left", "Right"], index=1)
window_wall = st.sidebar.selectbox("Window Wall", ["Top", "Bottom", "Left", "Right"], index=0)

room_image = st.file_uploader("Upload Room Template Image (PNG or JPEG)", type=["png", "jpg", "jpeg"])
image_url = None
if room_image:
    image_bytes = room_image.read()
    encoded = base64.b64encode(image_bytes).decode()
    mime = "image/png" if room_image.name.lower().endswith("png") else "image/jpeg"
    image_url = f"data:{mime};base64,{encoded}"
    st.image(image_bytes, caption="Uploaded Room Template", use_container_width=True)

if st.button("Generate Floor Plan"):
    room_metadata = {"door_wall": door_wall, "window_wall": window_wall}
    units, room_w, room_d = generate_auto_scaled_plan(total_width, total_height, (room_width, room_depth), corridor_width, room_metadata)
    svg = render_svg(units, total_width, total_height, image_url, room_w, room_d)
    st.components.v1.html(svg, height=700, scrolling=True)
