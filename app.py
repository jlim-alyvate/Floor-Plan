import streamlit as st
from PIL import Image
import io
import os

from floorplan import generate_auto_scaled_plan, render_svg
from room_configurator import configure_room

st.set_page_config(layout="wide")
st.title("🛏️ Floor Plan Generator")

# Sidebar inputs
with st.sidebar:
    st.header("Room Settings")
    uploaded_image = st.file_uploader("Upload Room Template (.png or .jpeg)", type=["png", "jpg", "jpeg"])

    total_width = st.number_input("Total Floor Width (m)", value=30)
    total_height = st.number_input("Total Floor Height (m)", value=20)
    room_width = st.number_input("Room Width (m)", value=3)
    room_depth = st.number_input("Room Depth (m)", value=5)
    corridor_width = st.number_input("Corridor Width (m)", value=2)

    proceed = st.button("Generate Layout")

# Get room metadata
room_metadata = configure_room(uploaded_image) if uploaded_image else {}

# Save uploaded image and set image_url
image_url = None
if uploaded_image:
    image_path = f"/mnt/data/{uploaded_image.name}"
    with open(image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())
    image_url = image_path

# Generate layout
if proceed:
    with st.spinner("Generating floor plan..."):
        units, room_w, room_d = generate_auto_scaled_plan(
            total_width,
            total_height,
            (room_width, room_depth),
            corridor_width,
            room_metadata
        )

        svg = render_svg(units, total_width, total_height, image_url, room_w, room_d)
        st.success("Floor plan generated!")

        # Display the SVG using st.image after converting to PNG for compatibility
        import cairosvg
        png_data = cairosvg.svg2png(bytestring=svg.encode("utf-8"))
        st.image(Image.open(io.BytesIO(png_data)), caption="Generated Floor Plan", use_container_width=True)
