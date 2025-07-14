import streamlit as st
from PIL import Image
from io import BytesIO
import base64

from floorplan import generate_auto_scaled_plan, render_svg
from room_configurator import configure_room_image

st.set_page_config(layout="wide")
st.title("Floor Plan Generator")

# Floorplan dimensions and room size
total_width = st.sidebar.number_input("Total Floor Width (m)", value=30)
total_height = st.sidebar.number_input("Total Floor Height (m)", value=30)
room_w = st.sidebar.number_input("Room Width (m)", value=3)
room_d = st.sidebar.number_input("Room Depth (m)", value=5)
corridor_width = st.sidebar.number_input("Corridor Width (m)", value=2)

# Configure room image and metadata
config = configure_room_image(room_w, room_d)
image_url = config["image_url"]
room_metadata = {
    "door_wall": config["door_wall"],
    "window_wall": config["window_wall"],
    "rotation": config["rotation"]
}

if config["image_preview"]:
    st.image(config["image_preview"], caption="Configured Room Image", use_container_width=True)

# Generate button
if st.button("Generate Floor Plan"):
    with st.spinner("Generating layout..."):
        units, room_width, room_depth = generate_auto_scaled_plan(
            total_width,
            total_height,
            (room_w, room_d),
            corridor_width,
            room_metadata=room_metadata
        )

        svg = render_svg(units, total_width, total_height, image_url, room_width, room_depth)

        # Embed SVG in HTML
        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        st.components.v1.html(f'<embed type="image/svg+xml" src="data:image/svg+xml;base64,{b64}" width="100%" height="800px"/>', height=800)
