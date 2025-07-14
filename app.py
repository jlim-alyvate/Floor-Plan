import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
from PIL import Image
import base64
import io

st.set_page_config(layout="wide")
st.title("Floor Plan Optimizer")

# Sidebar inputs
with st.sidebar:
    st.header("Floor Plan Settings")
    total_width = st.number_input("Total Width (m)", min_value=10.0, value=30.0)
    total_height = st.number_input("Total Height (m)", min_value=10.0, value=30.0)
    room_w = st.number_input("Room Width (m)", min_value=1.0, value=3.0)
    room_d = st.number_input("Room Depth (m)", min_value=1.0, value=5.0)
    corridor_width = st.number_input("Corridor Width (m)", min_value=1.0, value=2.0)

    st.markdown("---")
    st.header("Room Template Image Upload")
    uploaded_file = st.file_uploader("Upload Room Template (PNG or JPEG)", type=["png", "jpg", "jpeg"])
    room_image_url = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        room_image_url = "data:image/png;base64," + base64.b64encode(img_bytes).decode()

    st.markdown("---")
    st.header("Room Orientation Settings")
    door_wall = st.selectbox("Which wall has the door?", ["Top", "Bottom", "Left", "Right"])
    window_wall = st.selectbox("Which wall has the window?", ["Top", "Bottom", "Left", "Right"])

# Generate floor plan
if st.button("Generate Floor Plan"):
    with st.spinner("Generating floor plan..."):
        room_metadata = {
            "door_wall": door_wall,
            "window_wall": window_wall,
        }
        units, rw, rd = generate_auto_scaled_plan(
            total_width,
            total_height,
            (room_w, room_d),
            corridor_width,
            room_metadata=room_metadata
        )
        svg = render_svg(units, total_width, total_height, room_image_url, room_w, room_d)
        st.image(Image.open(io.BytesIO(svg.encode())), caption="Generated Floor Plan", use_container_width=True)
