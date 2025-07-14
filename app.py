import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64
import io

st.set_page_config(layout="wide")
st.title("🛠️ Room Layout Planner")

# Sidebar Inputs
st.sidebar.header("Layout Settings")
total_width = st.sidebar.number_input("Total Floor Width (m)", min_value=10, max_value=100, value=40)
total_height = st.sidebar.number_input("Total Floor Height (m)", min_value=10, max_value=100, value=30)
room_width = st.sidebar.number_input("Room Width (m)", min_value=2.0, max_value=10.0, value=3.0)
room_depth = st.sidebar.number_input("Room Depth (m)", min_value=2.0, max_value=10.0, value=5.0)
corridor_width = st.sidebar.number_input("Corridor Width (m)", min_value=1.0, max_value=10.0, value=2.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Room Image & Metadata")

uploaded_image = st.sidebar.file_uploader("Upload Room Image (PNG/JPEG)", type=["png", "jpg", "jpeg"])

door_wall = st.sidebar.selectbox("Door Wall (faces corridor)", ["Bottom", "Top", "Left", "Right"], index=0)
window_wall = st.sidebar.selectbox("Window Wall (must face outwards)", ["Top", "Bottom", "Left", "Right"], index=1)

# Build floorplan when button is clicked
if st.button("Generate Floorplan"):
    with st.spinner("Building floorplan..."):

        # Convert uploaded image to base64
        image_url = None
        if uploaded_image:
            image_bytes = uploaded_image.read()
            base64_image = base64.b64encode(image_bytes).decode()
            mime = "image/png" if uploaded_image.type == "image/png" else "image/jpeg"
            image_url = f"data:{mime};base64,{base64_image}"

        # Metadata
        room_metadata = {
            "door_wall": door_wall,
            "window_wall": window_wall
        }

        # Generate layout
        units, room_w, room_d = generate_auto_scaled_plan(
            total_width,
            total_height,
            (room_width, room_depth),
            corridor_width,
            room_metadata=room_metadata
        )

        # Generate SVG
        svg = render_svg(units, total_width, total_height, image_url, room_w, room_d)

        # Display SVG
        st.subheader("📐 Generated Floor Plan")
        st.components.v1.html(svg, height=int(total_height * 22), scrolling=True)

        # Optional: Download SVG
        st.download_button("Download SVG", svg, file_name="floorplan.svg", mime="image/svg+xml")
