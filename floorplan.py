from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0, door_wall=None, window_wall=None):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation
        self.door_wall = door_wall
        self.window_wall = window_wall

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

    # Lobby and lifts
    lobby_x = center_x - lobby_width / 2
    lobby_y = center_y - lobby_depth / 2
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Corridors
    corridor_x = center_x - corridor_width / 2
    corridor_y = center_y - corridor_width / 2
    units += [
        Room(0, corridor_y, lobby_x, corridor_width, "Corridor-Left"),
        Room(lobby_x + lobby_width, corridor_y, total_width - (lobby_x + lobby_width), corridor_width, "Corridor-Right"),
        Room(corridor_x, 0, corridor_width, lobby_y, "Corridor-Down"),
        Room(corridor_x, lobby_y + lobby_depth, corridor_width, total_height - (lobby_y + lobby_depth), "Corridor-Up")
    ]

    occupied = []
    def is_back_clear(candidate):
        for other in occupied:
            if candidate.rect.touches(other.rect):
                return False
        return True

    room_id = 0
    directions = [("L", 0, lobby_x), ("R", lobby_x + lobby_width, total_width - (lobby_x + lobby_width))]
    for direction, start_x, arm_width in directions:
        use_rotated = (arm_width // room_depth) > (arm_width // room_width)
        rw, rh = (room_depth, room_width) if use_rotated else (room_width, room_depth)
        rotation = 90 if use_rotated else 0
        for i in range(int(arm_width // rw)):
            x = start_x + i * rw
            y_below = corridor_y - rh
            y_above = corridor_y + corridor_width
            below = Room(x, y_below, rw, rh, f"Room-{direction}-B-{room_id}", rotation, door_wall, window_wall)
            if y_below > 0 and is_back_clear(Room(x, y_below - 0.01, rw, 0.01, "")):
                units.append(below)
                occupied.append(below)
            above = Room(x, y_above, rw, rh, f"Room-{direction}-T-{room_id}", rotation, door_wall, window_wall)
            if y_above + rh < total_height and is_back_clear(Room(x, y_above + rh, rw, 0.01, "")):
                units.append(above)
                occupied.append(above)
            room_id += 1

    return units, room_width, room_depth

def render_svg(units, total_width, total_height, room_image_url=None, room_w=3, room_d=5):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20
    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width, height = x2 - x, y2 - y
        x_px, y_px = x * scale, (total_height - y2) * scale

        if "Room" in unit.name and room_image_url:
            if unit.rotation == 90:
                img = dwg.image(href=room_image_url, insert=(0, 0), size=(height*scale, width*scale), preserveAspectRatio="none")
                group = dwg.g(transform=f"translate({x_px + width*scale/2},{y_px + height*scale/2}) rotate(90) translate({-height*scale/2},{-width*scale/2})")
                group.add(img)
                dwg.add(group)
            else:
                dwg.add(dwg.image(href=room_image_url, insert=(x_px, y_px), size=(width*scale, height*scale), preserveAspectRatio="none"))

        color = "none" if "Room" in unit.name and room_image_url else (
            "lightblue" if "Room" in unit.name else "#ccc" if "Corridor" in unit.name else "orange" if "Lobby" in unit.name else "red" if "Lift" in unit.name else "white"
        )

        dwg.add(dwg.rect(insert=(x_px, y_px), size=(width * scale, height * scale), fill=color, stroke="black", stroke_width=1))
        dwg.add(dwg.text(unit.name, insert=((x + width/2) * scale, (total_height - y2 + height/2) * scale), text_anchor="middle", font_size="8px", fill="black"))
    return dwg.tostring()
