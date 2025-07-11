import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import uuid

# Define room and common space data structures
class SpaceUnit:
    def __init__(self, name, x, y, width, depth, height=3, type="room"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.position = (x, y)
        self.dimensions = (width, depth, height)
        self.type = type
        self.access_points = []

def optimize_floorplan(total_width, total_depth, room_width, room_depth, corridor_width):
    rooms = []
    corridor_y = 0

    cols = int(total_width // room_width)
    rows = int((total_depth - corridor_width) // room_depth)

    for i in range(rows):
        for j in range(cols):
            x = j * room_width
            y = i * room_depth + corridor_width
            if x + room_width <= total_width and y + room_depth <= total_depth:
                room = SpaceUnit(
                    name=f"Room-{i}-{j}",
                    x=x,
                    y=y,
                    width=room_width,
                    depth=room_depth,
                    type="room",
                )
                rooms.append(room)

    # Add corridor
    corridor = SpaceUnit("Corridor", 0, 0, total_width, corridor_width, type="corridor")
    rooms.append(corridor)

    # Add common elements
    lift = SpaceUnit("Lift", 0, total_depth - 3, 3, 3, type="lift")
    stair = SpaceUnit("Stairwell", total_width - 3, total_depth - 3, 3, 3, type="stairwell")
    rooms.extend([lift, stair])

    return rooms

def draw_floorplan(units):
    fig, ax = plt.subplots(figsize=(10, 6))
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

        st.session_state["layout_units"] = units  # For internal use by Module 2

def fig_to_bytes(fig):
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

if __name__ == "__main__":
    main()
