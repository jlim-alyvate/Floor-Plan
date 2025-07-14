import streamlit as st
from floorplan import generate_auto_scaled_plan, render_svg
import base64

st.set_page_config(layout="wide")
st.title("Modular Floor Plan Generator")

# Sidebar inputs
with st.sidebar:
    st.header("1. Floor Dimensions")
    total_width = st.number_input("Total Width (meters)", value=30)
    total_height = st.number_input("Total Height (meters)", value=20)

    st.header("2. Room Settings")
    room_width = st.number_input("Room Width (meters)", value=3.0)
    room_depth = st.number_input("Room Depth (meters)", value=5.0)
    corridor_width = st.number_input("Corridor Width (meters)", value=2.5)

    st.header("3. Room Template Image")
    uploaded_file = st.file_uploader("Upload Room Template (PNG or JPEG)", type=["png", "jpg", "jpeg"])
    image_url = None
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

    st.header("4. Door and Window Selection")
    st.markdown("**Click a side of the rectangle to indicate door and window location**")

    selection_area = st.empty()

    import streamlit_drawable_canvas as st_canvas

    canvas_result = st_canvas.st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        update_streamlit=True,
        height=150,
        width=300,
        drawing_mode="line",
        key="canvas",
    )

    door_wall = st.selectbox("Door Wall", ["Bottom", "Top", "Left", "Right"])
    window_wall = st.selectbox("Window Wall", ["Top", "Bottom", "Left", "Right"])

# Floorplan generation
if st.button("Generate Floor Plan"):
    with st.spinner("Generating layout..."):
        metadata = {
            "door_wall": door_wall,
            "window_wall": window_wall,
        }
        units, rw, rd = generate_auto_scaled_plan(
            total_width,
            total_height,
            (room_width, room_depth),
            corridor_width,
            room_metadata=metadata,
        )
        svg = render_svg(units, total_width, total_height, image_url, room_width, room_depth)
        st.success("Floor plan generated!")
        st.image(svg, use_container_width=True)

        # Optional: SVG download
        b64 = base64.b64encode(svg.encode()).decode()
        href = f'<a href="data:image/svg+xml;base64,{b64}" download="floorplan.svg">Download SVG</a>'
        st.markdown(href, unsafe_allow_html=True)
