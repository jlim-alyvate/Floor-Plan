# app.py
import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64

st.set_page_config(page_title="Hotel Floor Plan Generator", layout="wide")

st.sidebar.title("📐 Floor Plan Settings")
total_width = st.sidebar.number_input("Total Width (m)", min_value=10.0, value=40.0)
total_height = st.sidebar.number_input("Total Height (m)", min_value=10.0, value=30.0)
room_width = st.sidebar.number_input("Room Width (m)", min_value=2.0, value=4.0)
room_depth = st.sidebar.number_input("Room Depth (m)", min_value=2.0, value=6.0)
corridor_width = st.sidebar.number_input("Corridor Width (m)", min_value=1.5, value=2.5)

st.sidebar.markdown("---")
st.sidebar.subheader("🚪 Room Metadata")
door_wall = st.sidebar.selectbox("Door Facing Wall", ["Top", "Bottom", "Left", "Right"])
window_wall = st.sidebar.selectbox("Window Wall (Must face outside)", ["Top", "Bottom", "Left", "Right"])

st.sidebar.markdown("---")
st.sidebar.subheader("🖼️ Upload Room Template Image")
image_file = st.sidebar.file_uploader("Upload PNG or JPEG", type=["png", "jpeg", "jpg"])

image_url = None
if image_file:
    image_bytes = image_file.read()
    encoded = base64.b64encode(image_bytes).decode()
    mime_type = "image/png" if image_file.type == "image/png" else "image/jpeg"
    image_url = f"data:{mime_type};base64,{encoded}"

if st.button("Generate Floor Plan"):
    with st.spinner("Generating layout..."):
        room_metadata = {
            "door_wall": door_wall,
            "window_wall": window_wall
        }
        units, rw, rd = generate_auto_scaled_plan(
            total_width, total_height, (room_width, room_depth), corridor_width, room_metadata
        )
        svg = render_svg(units, total_width, total_height, image_url, rw, rd)
        
        st.success("✅ Floor plan generated!")
        st.image(image_url, caption="Room Template Preview", use_container_width=True)
        st.components.v1.html(svg, height=int(total_height * 22), scrolling=True)
