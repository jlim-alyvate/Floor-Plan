import streamlit as st
from PIL import Image
import io
import floorplan
from room_configurator import configure_room

st.set_page_config(layout="wide")

st.title("Auto-Generated Floor Plan")
st.sidebar.header("Floor Plan Parameters")

# Inputs
total_width = st.sidebar.slider("Total Floor Width (m)", 20, 100, 40)
total_height = st.sidebar.slider("Total Floor Height (m)", 20, 100, 30)
room_width = st.sidebar.slider("Room Width (m)", 2, 10, 3)
room_depth = st.sidebar.slider("Room Depth (m)", 2, 10, 5)
corridor_width = st.sidebar.slider("Corridor Width (m)", 1, 5, 2)

# Room Configuration (Image, Door/Window wall, Rotation)
st.sidebar.header("Room Template Setup")
image_url, door_wall, window_wall, rotation_angle = configure_room()

if st.sidebar.button("Generate Floor Plan"):
    if not image_url:
        st.error("Please upload a room image and configure door/window walls.")
    else:
        room_metadata = {
            "door_wall": door_wall,
            "window_wall": window_wall,
            "rotation_angle": rotation_angle
        }

        with st.spinner("Generating layout..."):
            units, room_w, room_d = floorplan.generate_auto_scaled_plan(
                total_width,
                total_height,
                (room_width, room_depth),
                corridor_width,
                room_metadata
            )

            svg = floorplan.render_svg(
                units,
                total_width,
                total_height,
                image_url,
                room_w,
                room_d
            )

            st.subheader("Generated Floor Plan")
            st.image(svg, use_container_width=True)
