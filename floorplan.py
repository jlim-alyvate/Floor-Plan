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
    rows = int(total_height // room_depth)

    center_x = total_width / 2
    center_y = total_height / 2

    lobby_width = 6
    lobby_depth = corridor_width
    lift_width = 2
    lift_depth = 2

    units = []

    # Central lobby (acts as corridor hub)
    lobby_x = center_x - lobby_width / 2
    lobby_y = center_y - lobby_depth / 2
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))

    # Two lifts above lobby
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Horizontal corridor arm (left and right of lobby)
    corridor_length_x = int((total_width - lobby_width) / (2 * room_width)) * room_width
    corridor_left_x = lobby_x - corridor_length_x
    corridor_right_x = lobby_x + lobby_width
    corridor_y = lobby_y
    units.append(Room(corridor_left_x, corridor_y, corridor_length_x, corridor_width, "Corridor-Left"))
    units.append(Room(corridor_right_x, corridor_y, corridor_length_x, corridor_width, "Corridor-Right"))

    # Vertical corridor arm (above and below lobby)
    corridor_length_y = int((total_height - lobby_depth) / (2 * room_depth)) * room_depth
    corridor_top_y = lobby_y + lobby_depth
    corridor_bottom_y = lobby_y - corridor_length_y
    units.append(Room(center_x - corridor_width / 2, corridor_top_y, corridor_width, corridor_length_y, "Corridor-Up"))
    units.append(Room(center_x - corridor_width / 2, corridor_bottom_y, corridor_width, corridor_length_y, "Corridor-Down"))

    # Place rooms along corridor arms
    room_id = 0

    # Horizontal arms (left and right)
    for direction, base_x in [("L", corridor_left_x), ("R", corridor_right_x)]:
        for i in range(int(corridor_length_x // room_width)):
            x = base_x + i * room_width if direction == "L" else base_x + i * room_width
            y_below = corridor_y - room_depth
            y_above = corridor_y + corridor_width
            units.append(Room(x, y_below, room_width, room_depth, f"Room-{direction}-B-{room_id}"))
            units.append(Room(x, y_above, room_width, room_depth, f"Room-{direction}-T-{room_id}"))
            room_id += 1

    # Vertical arms (up and down)
    for direction, base_y in [("U", corridor_top_y), ("D", corridor_bottom_y)]:
        for i in range(int(corridor_length_y // room_depth)):
            y = base_y + i * room_depth if direction == "U" else base_y + i * room_depth
            x_left = center_x - corridor_width / 2 - room_width
            x_right = center_x + corridor_width / 2
            units.append(Room(x_left, y, room_width, room_depth, f"Room-{direction}-L-{room_id}"))
            units.append(Room(x_right, y, room_width, room_depth, f"Room-{direction}-R-{room_id}"))
            room_id += 1

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
