from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0, door_wall="Bottom", window_wall="Top"):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation
        self.door_wall = door_wall
        self.window_wall = window_wall

def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width, room_metadata=None):
    room_width, room_depth = room_aspect_ratio
    door_wall = room_metadata.get("door_wall", "Bottom") if room_metadata else "Bottom"
    window_wall = room_metadata.get("window_wall", "Top") if room_metadata else "Top"

    center_x = total_width / 2
    center_y = total_height / 2
    lobby_width = 6
    lobby_depth = corridor_width
    lift_width = 2
    lift_depth = 2
    units = []

    # Lobby
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

    occupied = [r.rect for r in units]
    room_id = 0

    def is_clear_back(candidate_rect):
        return not any(candidate_rect.touches(other) for other in occupied)

    # Add rooms along corridors
    for arm in ["Left", "Right", "Up", "Down"]:
        if arm in ["Left", "Right"]:
            arm_x_start = 0 if arm == "Left" else lobby_x + lobby_width
            arm_width = lobby_x if arm == "Left" else total_width - (lobby_x + lobby_width)
            room_w = room_depth if arm == "Left" else room_width
            room_h = room_width if arm == "Left" else room_depth
            rotation = 90 if arm == "Left" else 0
            corridor_y_top = corridor_y + corridor_width
            corridor_y_bottom = corridor_y - room_h
            cols = int(arm_width // room_w)

            for i in range(cols):
                x = arm_x_start + i * room_w
                for y, suffix in [(corridor_y_bottom, "T"), (corridor_y_top, "B")]:
                    room_rect = box(x, y, x + room_w, y + room_h)
                    back_rect = box(x, y + room_h, x + room_w, y + room_h + 0.01) if suffix == "T" else box(x, y - 0.01, x + room_w, y)
                    if room_rect.bounds[1] >= 0 and is_clear_back(back_rect):
                        units.append(Room(x, y, room_w, room_h, f"Room-{arm}-{suffix}-{room_id}", rotation, door_wall, window_wall))
                        occupied.append(room_rect)
                        room_id += 1
        else:
            arm_y_start = 0 if arm == "Down" else lobby_y + lobby_depth
            arm_height = lobby_y if arm == "Down" else total_height - (lobby_y + lobby_depth)
            rows = int(arm_height // room_depth)
            for i in range(rows):
                y = arm_y_start + i * room_depth
                for x, suffix in [(corridor_x - room_width, "L"), (corridor_x + corridor_width, "R")]:
                    room_rect = box(x, y, x + room_width, y + room_depth)
                    back_rect = box(x - 0.01, y, x, y + room_depth) if suffix == "L" else box(x + room_width, y, x + room_width + 0.01, y + room_depth)
                    if x >= 0 and is_clear_back(back_rect):
                        units.append(Room(x, y, room_width, room_depth, f"Room-{arm}-{suffix}-{room_id}", 0, door_wall, window_wall))
                        occupied.append(room_rect)
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

        # Room Image
        if "Room" in unit.name and room_image_url:
            if unit.rotation == 90:
                img = dwg.image(href=room_image_url, insert=(0, 0),
                                size=(height * scale, width * scale),
                                preserveAspectRatio="none")
                g = dwg.g(transform=(
                    f"translate({x_px + width * scale / 2},{y_px + height * scale / 2}) "
                    f"rotate(90) translate({-height * scale / 2},{-width * scale / 2})"))
                g.add(img)
                dwg.add(g)
            else:
                img = dwg.image(href=room_image_url, insert=(x_px, y_px),
                                size=(width * scale, height * scale),
                                preserveAspectRatio="none")
                dwg.add(img)

        # Rectangles
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
