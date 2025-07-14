from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation

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
    lobby_x = center_x - lobby_width / 2
    lobby_y = center_y - lobby_depth / 2
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    corridor_length_x = total_width / 2 - lobby_width / 2
    corridor_y = center_y - corridor_width / 2
    units.append(Room(0, corridor_y, lobby_x, corridor_width, "Corridor-Left"))
    units.append(Room(lobby_x + lobby_width, corridor_y, corridor_length_x, corridor_width, "Corridor-Right"))

    corridor_length_y = total_height / 2 - lobby_depth / 2
    corridor_x = center_x - corridor_width / 2
    units.append(Room(corridor_x, 0, corridor_width, lobby_y, "Corridor-Down"))
    units.append(Room(corridor_x, lobby_y + lobby_depth, corridor_width, corridor_length_y, "Corridor-Up"))

    occupied = []
    def is_back_clear(candidate):
        for other in occupied:
            if candidate.rect.touches(other.rect):
                return False
        return True

    room_id = 0

    # Horizontal Arms
    for direction, start_x, arm_width in [("L", 0, lobby_x), ("R", lobby_x + lobby_width, total_width - (lobby_x + lobby_width))]:
        cols_default = int(arm_width // room_width)
        cols_rotated = int(arm_width // room_depth)
        use_rotated = cols_rotated > cols_default
        room_w, room_h = (room_depth, room_width) if use_rotated else (room_width, room_depth)
        rotation = 90 if use_rotated else 0

        for i in range(int(arm_width // room_w)):
            x = start_x + i * room_w
            y_below = corridor_y - room_h
            y_above = corridor_y + corridor_width

            below = Room(x, y_below, room_w, room_h, f"Room-{direction}-B-{room_id}", rotation)
            if y_below > 0 and is_back_clear(Room(x, y_below - 0.01, room_w, 0.01, "", 0)):
                occupied.append(below)
                units.append(below)

            above = Room(x, y_above, room_w, room_h, f"Room-{direction}-T-{room_id}", rotation)
            if y_above + room_h < total_height and is_back_clear(Room(x, y_above + room_h, room_w, 0.01, "", 0)):
                occupied.append(above)
                units.append(above)

            room_id += 1

    # Vertical Arms
    for direction, start_y, arm_height in [("U", lobby_y + lobby_depth, total_height - (lobby_y + lobby_depth)), ("D", 0, lobby_y)]:
        rows = int(arm_height // room_depth)
        for i in range(rows):
            y = start_y + i * room_depth
            x_left = corridor_x - room_width
            x_right = corridor_x + corridor_width

            left = Room(x_left, y, room_width, room_depth, f"Room-{direction}-L-{room_id}", 0)
            if x_left > 0 and is_back_clear(Room(x_left - 0.01, y, 0.01, room_depth, "", 0)):
                occupied.append(left)
                units.append(left)

            right = Room(x_right, y, room_width, room_depth, f"Room-{direction}-R-{room_id}", 0)
            if x_right + room_width < total_width and is_back_clear(Room(x_right + room_width, y, 0.01, room_depth, "", 0)):
                occupied.append(right)
                units.append(right)

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
            if unit.rotation == 90:
                img = dwg.image(href=room_image_url,
                                insert=(0, 0),
                                size=(height * scale, width * scale),
                                preserveAspectRatio="none")
                group = dwg.g(transform=(
                    f"translate({x_px + width*scale/2},{y_px + height*scale/2}) "
                    f"rotate(90) "
                    f"translate({-height*scale/2},{-width*scale/2})"
                ))
                group.add(img)
                dwg.add(group)
            else:
                img = dwg.image(href=room_image_url,
                                insert=(x_px, y_px),
                                size=(width * scale, height * scale),
                                preserveAspectRatio="none")
                dwg.add(img)

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
