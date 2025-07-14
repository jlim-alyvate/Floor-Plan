# floorplan.py
from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation

    def center(self):
        return self.rect.centroid.x, self.rect.centroid.y

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
    occupied = []

    # Add lobby
    lobby_x = center_x - lobby_width / 2
    lobby_y = center_y - lobby_depth / 2
    lobby = Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby")
    units.append(lobby)

    # Add lifts
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Add corridors
    corridor_y = center_y - corridor_width / 2
    corridor_x = center_x - corridor_width / 2
    units.extend([
        Room(0, corridor_y, lobby_x, corridor_width, "Corridor-Left"),
        Room(lobby_x + lobby_width, corridor_y, total_width - (lobby_x + lobby_width), corridor_width, "Corridor-Right"),
        Room(corridor_x, 0, corridor_width, lobby_y, "Corridor-Down"),
        Room(corridor_x, lobby_y + lobby_depth, corridor_width, total_height - (lobby_y + lobby_depth), "Corridor-Up"),
    ])

    corridors = [u.rect for u in units if "Corridor" in u.name or "Lobby" in u.name]

    def is_valid_room(room):
        return not any(room.rect.intersects(u.rect) for u in units)

    def corridor_touches(rect):
        return any(rect.touches(c) for c in corridors)

    room_id = 0

    # Grid-based placement
    step_x = 0.5
    step_y = 0.5
    y = 0
    while y + room_depth <= total_height:
        x = 0
        while x + room_width <= total_width:
            for rot in [0, 90]:
                rw, rd = (room_width, room_depth) if rot == 0 else (room_depth, room_width)
                room = Room(x, y, rw, rd, f"Room-{room_id}", rot)
                back = get_window_wall(room, window_wall)
                front = get_door_wall(room, door_wall)
                if (room.rect.bounds[2] <= total_width and
                    room.rect.bounds[3] <= total_height and
                    is_valid_room(room) and
                    corridor_touches(front) and
                    not any(room.rect.touches(u.rect) for u in units if "Room" in u.name) and
                    not any(back.touches(u.rect) for u in units if "Room" in u.name)):
                    units.append(room)
                    occupied.append(room)
                    room_id += 1
                    break
            x += step_x
        y += step_y

    return units, room_width, room_depth

def get_door_wall(room, wall):
    minx, miny, maxx, maxy = room.rect.bounds
    if wall == "Bottom":
        return box(minx, miny - 0.01, maxx, miny)
    elif wall == "Top":
        return box(minx, maxy, maxx, maxy + 0.01)
    elif wall == "Left":
        return box(minx - 0.01, miny, minx, maxy)
    elif wall == "Right":
        return box(maxx, miny, maxx + 0.01, maxy)

def get_window_wall(room, wall):
    return get_door_wall(room, wall)

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
                img = dwg.image(href=room_image_url, insert=(0, 0), size=(height * scale, width * scale), preserveAspectRatio="none")
                group = dwg.g(transform=(f"translate({x_px + width*scale/2},{y_px + height*scale/2}) rotate(90) translate({-height*scale/2},{-width*scale/2})"))
                group.add(img)
                dwg.add(group)
            else:
                img = dwg.image(href=room_image_url, insert=(x_px, y_px), size=(width * scale, height * scale), preserveAspectRatio="none")
                dwg.add(img)

        color = "none" if "Room" in unit.name and room_image_url else (
            "lightblue" if "Room" in unit.name else
            "#ccc" if "Corridor" in unit.name else
            "orange" if "Lobby" in unit.name else
            "red" if "Lift" in unit.name else "white")

        dwg.add(dwg.rect(insert=(x_px, y_px), size=(width * scale, height * scale), fill=color, stroke="black", stroke_width=1))
        dwg.add(dwg.text(unit.name, insert=((x + width / 2) * scale, (total_height - y2 + height / 2) * scale), text_anchor="middle", font_size="8px", fill="black"))
    return dwg.tostring()
