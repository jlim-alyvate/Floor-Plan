import streamlit as st
from floorplan import generate_optimized_layout, render_svg

st.set_page_config(layout="wide")
st.title("Hotel Room Layout Optimizer")

col1, col2 = st.columns([1, 3])

with col1:
    total_width = st.number_input("Total Floor Width (m)", min_value=10.0, value=30.0)
    total_height = st.number_input("Total Floor Depth (m)", min_value=10.0, value=20.0)
    room_w = st.number_input("Room Width (m)", min_value=2.0, value=3.5)
    room_d = st.number_input("Room Depth (m)", min_value=2.0, value=5.0)
    corridor_w = st.number_input("Corridor Width (m)", min_value=1.0, value=2.0)
    generate = st.button("Generate Floor Plan")

with col2:
    if generate:
        status = st.sidebar.empty()
        progress = st.sidebar.progress(0.0)

        def update_progress(val):
            status.text(f"Progress: {int(val*100)}%")
            progress.progress(val)

        with st.spinner("Generating layout..."):
            units = generate_optimized_layout(total_width, total_height, room_w, room_d, corridor_w, update_progress)
            svg = render_svg(units, total_width, total_height)
            st.image(svg, use_container_width=True)
            status.text("✅ Done")
