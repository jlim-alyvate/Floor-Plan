# floorplan.py
from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation  # degrees

def calculate_rotation_from_door_wall(door_wall):
    return {
        "Bottom": 0,
        "Right": 90,
        "Top": 180,
        "Left": 270
    }.get(door_wall, 0)

def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width, room_metadata=None):
    room_width, room_depth = room_aspect_ratio
    door_wall = room_metadata.get("door_wall") if room_metadata else "Bottom"
    window_wall = room_metadata.get("window_wall") if room_metadata else "Top"

    center_x = total_width / 2
    center_y = total_height / 2

    lobby_width = 6
    lobby_depth = corridor_width
    lift_width = 2
    lift_depth = 2

    units = []
    rotation = calculate_rotation_from_door_wall(door_wall)

    # Central lobby
    lobby_x = center_x - lobby_width / 2
    lobby_y = center_y - lobby_depth / 2
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))

    # Lifts
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Horizontal corridors
    corridor_y = center_y - corridor_width / 2
    units.append(Room(0, corridor_y, lobby_x, corridor_width, "Corridor-Left"))
    units.append(Room(lobby_x + lobby_width, corridor_y, total_width - (lobby_x + lobby_width), corridor_width, "Corridor-Right"))

    # Vertical corridors
    corridor_x = center_x - corridor_width / 2
    units.append(Room(corridor_x, 0, corridor_width, lobby_y, "Corridor-Down"))
    units.append(Room(corridor_x, lobby_y + lobby_depth, corridor_width, total_height - (lobby_y + lobby_depth), "Corridor-Up"))

    room_id = 0
    occupied = []

    def is_back_clear(candidate):
        for other in occupied:
            if candidate.rect.touches(other.rect):
                return False
        return True

    room_w, room_d = room_width, room_depth

    for x_off, y_off, label in [
        (-room_w, 0, "Left"),
        (room_w + corridor_width, 0, "Right"),
        (0, -room_d, "Bottom"),
        (0, room_d + corridor_width, "Top")
    ]:
        for i in range(3):
            x = center_x + x_off
            y = center_y + y_off + i * (room_d + 0.2)
            candidate = Room(x, y, room_w, room_d, f"Room-{label}-{room_id}", rotation)
            if is_back_clear(candidate):
                units.append(candidate)
                occupied.append(candidate)
                room_id += 1

    return units, room_width, room_depth

def render_svg(units, total_width, total_height, room_image_url=None, room_w=3, room_d=5):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20

    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width = x2 - x
        height = y2 - y
        x_px = x * scale
        y_px = (total_height - y2) * scale

        if "Room" in unit.name and room_image_url:
            img = dwg.image(href=room_image_url,
                            insert=(0, 0),
                            size=(width * scale, height * scale),
                            preserveAspectRatio="none")
            group = dwg.g(transform=(
                f"translate({x_px + width * scale / 2},{y_px + height * scale / 2}) "
                f"rotate({unit.rotation}) "
                f"translate({-width * scale / 2},{-height * scale / 2})"
            ))
            group.add(img)
            dwg.add(group)
        else:
            color = (
                "lightblue" if "Room" in unit.name else
                "#ccc" if "Corridor" in unit.name else
                "orange" if "Lobby" in unit.name else
                "red" if "Lift" in unit.name else
                "white"
            )
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
