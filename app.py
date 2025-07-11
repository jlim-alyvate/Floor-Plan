# app.py

import streamlit as st

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
except ModuleNotFoundError:
    st.error("matplotlib is not installed. Please run `pip install matplotlib` or add it to requirements.txt.")
    st.stop()

import uuid
import io

class SpaceUnit:
    def __init__(self, name, x, y, width, depth, height=3, type="room"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.position = (x, y)
        self.dimensions = (width, depth, height)
        self.type = type
        self.access_points = []

def optimize_floorplan(total_width, total_depth, room_width, room_depth, corridor_width):
    units = []

    # Compute number of rooms per side of the corridor
    half_depth = (total_depth - corridor_width) / 2
    rows_per_side = int(half_depth // room_depth)
    cols = int(total_width // room_width)

    # Lower side rooms
    for i in range(rows_per_side):
        for j in range(cols):
            x = j * room_width
            y = i * room_depth
            units.append(SpaceUnit(f"Room-L-{i}-{j}", x, y, room_width, room_depth))

    # Upper side rooms
    for i in range(rows_per_side):
        for j in range(cols):
            x = j * room_width
            y = total_depth - ((i + 1) * room_depth)
            units.append(SpaceUnit(f"Room-U-{i}-{j}", x, y, room_width, room_depth))

    # Central corridor
    corridor_y = (total_depth - corridor_width) / 2
    units.append(SpaceUnit("Corridor", 0, corridor_y, total_width, corridor_width, type="corridor"))

    # Lift and stairwell in the middle
    core_width, core_depth = 3, corridor_width
    mid_x = total_width / 2
    lift_x = mid_x - core_width - 0.5
    stair_x = mid_x + 0.5
    units.append(SpaceUnit("Lift", lift_x, corridor_y, core_width, core_depth, type="lift"))
    units.append(SpaceUnit("Stairwell", stair_x, corridor_y, core_width, core_depth, type="stairwell"))

    return units

def draw_floorplan(units):
    fig, ax = plt.subplots(figsize=(12, 8))
    for unit in units:
        x, y = unit.position
        w, d, _ = unit.dimensions
        color = {
            "room": "skyblue",
            "corridor": "gray",
            "lift": "orange",
            "stairwell": "red",
        }.get(unit.type, "white")
        ax.add_patch(Rectangle((x, y), w, d, edgecolor='black', facecolor=color, linewidth=1))
        ax.text(x + w/2, y + d/2, unit.name, ha='center', va='center', fontsize=6)

    ax.set_xlim(0, max([u.position[0] + u.dimensions[0] for u in units]))
    ax.set_ylim(0, max([u.position[1] + u.dimensions[1] for u in units]))
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

def main():
    st.title("Modular Hotel Floor Plan Generator")

    with st.sidebar:
        total_width = st.number_input("Total Floor Width (m)", 10.0, 100.0, 30.0)
        total_depth = st.number_input("Total Floor Depth (m)", 10.0, 100.0, 20.0)
        room_width = st.number_input("Room Width (m)", 2.0, 10.0, 3.5)
        room_depth = st.number_input("Room Depth (m)", 2.0, 10.0, 5.0)
        corridor_width = st.number_input("Corridor Width (m)", 1.0, 5.0, 2.0)

    if st.button("Generate Floor Plan"):
        units = optimize_floorplan(total_width, total_depth, room_width, room_depth, corridor_width)
        fig = draw_floorplan(units)
        st.pyplot(fig)
        st.download_button("Download PNG", data=fig_to_bytes(fig), file_name="floorplan.png", mime="image/png")
        st.session_state["layout_units"] = units

if __name__ == "__main__":
    main()

