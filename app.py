import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
from room_configurator import configure_room
import io
import base64

st.set_page_config(layout="wide")
st.title("Floor Plan Generator")

# Sidebar Inputs
with st.sidebar:
    st.header("Upload Room Template")
    uploaded_image = st.file_uploader("Upload room image (JPEG or PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Room Template", use_container_width=True)

    st.markdown("---")
    st.header("Room Configuration")
    with st.expander("Click to configure door and window"):
        room_metadata = configure_room(uploaded_image)

    st.markdown("---")
    st.header("Room Dimensions")
    room_w = st.number_input("Room Width (m)", min_value=1.0, max_value=20.0, value=3.0)
    room_d = st.number_input("Room Depth (m)", min_value=1.0, max_value=20.0, value=5.0)
    corridor_w = st.number_input("Corridor Width (m)", min_value=1.0, max_value=10.0, value=2.0)
    total_width = st.number_input("Total Floor Width (m)", min_value=10.0, max_value=100.0, value=30.0)
    total_height = st.number_input("Total Floor Height (m)", min_value=10.0, max_value=100.0, value=30.0)

# Validate user input
if uploaded_image is None:
    st.warning("Please upload a room template image to proceed.")
else:
    # Prepare image URL
    image_bytes = uploaded_image.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/png;base64,{image_base64}"

    # Generate floor plan
    units, room_w_used, room_d_used = generate_auto_scaled_plan(
        total_width, total_height, (room_w, room_d), corridor_w, room_metadata
    )

    # Render SVG
    svg = render_svg(units, total_width, total_height, image_url, room_w_used, room_d_used)
    st.components.v1.html(svg, height=int(total_height * 20) + 50, scrolling=True)
