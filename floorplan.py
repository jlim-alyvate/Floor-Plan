# floorplan.py

from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name):
        self.rect = box(x, y, x + width, y + height)
        self.name = name

def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width):
    room_width, room_depth = room_aspect_ratio

    cols = int(total_width // room_width)
    corridor_y = (total_height - corridor_width) / 2
    lobby_width = 6
    lobby_depth = 4
    lift_width = 2
    lift_depth = 2

    units = []

    # Central lobby and lifts
    lobby_x = (total_width - lobby_width) / 2
    lobby_y = corridor_y
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))

    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Corridor extending full width from lobby
    units.append(Room(0, corridor_y, total_width, corridor_width, "Corridor"))

    # Place one row of rooms above and below corridor
    for j in range(cols):
        x = j * room_width

        # Ensure rooms do not overlap with lifts/lobby
        if x + room_width <= lobby_x or x >= lobby_x + lobby_width:
            # Lower row
            y_lower = corridor_y - room_depth
            units.append(Room(x, y_lower, room_width, room_depth, f"Room-L-0-{j}"))

            # Upper row
            y_upper = corridor_y + corridor_width
            units.append(Room(x, y_upper, room_width, room_depth, f"Room-U-0-{j}"))

    return units, room_width, room_depth

def render_svg(units, total_width, total_height, room_image_url=None, room_w=3, room_d=5):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20  # 1 meter = 20px

    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width = x2 - x
        height = y2 - y
        x_px = x * scale
        y_px = (total_height - y2) * scale

        if "Room" in unit.name and room_image_url:
            dwg.add(dwg.image(href=room_image_url,
                              insert=(x_px, y_px),
                              size=(width * scale, height * scale),
                              preserveAspectRatio="none"))

        color = "none" if "Room" in unit.name and room_image_url else (
            "lightblue" if "Room" in unit.name else
            "#ccc" if "Corridor" in unit.name else
            "orange" if "Lobby" in unit.name else
            "red" if "Lift" in unit.name else
            "white")

        dwg.add(dwg.rect(insert=(x_px, y_px),
                         size=(width * scale, height * scale),
                         fill=color,
                         stroke="black",
                         stroke_width=1))

        dwg.add(dwg.text(unit.name,
                         insert=((x + width / 2) * scale, (total_height - y2 + height / 2) * scale),
                         text_anchor="middle",
                         font_size="8px",
                         fill="black"))

    return dwg.tostring()
