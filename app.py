import streamlit as st
from floorplan import generate_expanding_layout, render_svg
import base64

# Streamlit App Setup
st.set_page_config(layout="wide")
st.title("Hotel Floor Plan Optimizer")

# Sidebar Inputs
st.sidebar.header("Floor Plan Inputs")
floor_width = st.sidebar.number_input("Total Floor Width (m)", value=30.0, min_value=10.0)
floor_height = st.sidebar.number_input("Total Floor Height (m)", value=20.0, min_value=10.0)

room_width = st.sidebar.number_input("Room Width (m)", value=3.0, min_value=2.0)
room_depth = st.sidebar.number_input("Room Depth (m)", value=5.0, min_value=3.0)

corridor_width = st.sidebar.number_input("Corridor Width (m)", value=2.0, min_value=1.0)

st.sidebar.markdown("---")
room_image = st.sidebar.file_uploader("Upload Template Room Image (Optional)", type=["png", "jpg", "jpeg"])

# Generate Floor Plan Button
if st.button("Generate Floor Plan"):
    # Progress UI in Sidebar
    percent_text = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0)

    def update_progress(progress):
        percent = int(progress * 100)
        percent_text.markdown(f"**Progress: {percent}%**")
        progress_bar.progress(progress)

    # Handle Room Image Upload
    room_image_url = None
    if room_image:
        room_image_bytes = room_image.read()
        room_image_b64 = base64.b64encode(room_image_bytes).decode("utf-8")
        mime = "image/png" if room_image.type == "image/png" else "image/jpeg"
        room_image_url = f"data:{mime};base64,{room_image_b64}"

    # Generate Layout
    units, rw, rd = generate_expanding_layout(
        total_width=floor_width,
        total_height=floor_height,
        room_size=(room_width, room_depth),
        corridor_width=corridor_width,
        progress_callback=update_progress
    )

    # Clear progress bar after completion
    progress_bar.empty()
    percent_text.empty()

    # Render Output
    svg = render_svg(units, floor_width, floor_height, room_image_url, room_width, room_depth)

    st.subheader("Generated Floor Plan")
    st.image(svg, use_container_width=True)

    st.subheader("Generated Floor Plan")
    st.image(svg, use_column_width=True)
