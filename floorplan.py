import numpy as np
from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation

def generate_connected_layout(total_width, total_height, room_size, corridor_width, progress_callback=None):
    room_w, room_d = room_size
    cell_size = min(room_w, room_d)
    grid_w = int(total_width / cell_size)
    grid_h = int(total_height / cell_size)
    grid = np.zeros((grid_h, grid_w))

    scale = cell_size
    def cells_for_rect(x, y, w, h):
        return (int(y / scale), int(x / scale), int((y + h) / scale), int((x + w) / scale))

    def place_room(x, y, w, h, name):
        top, left, bottom, right = cells_for_rect(x, y, w, h)
        if bottom >= grid.shape[0] or right >= grid.shape[1]:
            return None
        if grid[top:bottom, left:right].shape != (bottom - top, right - left):
            return None
        if np.any(grid[top:bottom, left:right]):
            return None
        grid[top:bottom, left:right] = 1
        return Room(x, y, w, h, name)

    rooms = []
    center_x = total_width / 2
    center_y = total_height / 2
    lobby_w, lobby_d = 6, corridor_width
    lobby = place_room(center_x - lobby_w/2, center_y - lobby_d/2, lobby_w, lobby_d, "Lobby")
    if lobby: rooms.append(lobby)

    frontier = [(lobby.rect.bounds[0], lobby.rect.bounds[1])]
    visited = set(frontier)
    room_id = 0
    steps = 0
    max_steps = 1000

    while frontier and steps < max_steps:
        new_frontier = []
        for fx, fy in frontier:
            for dx, dy in [(-corridor_width, 0), (corridor_width, 0), (0, -corridor_width), (0, corridor_width)]:
                cx, cy = fx + dx, fy + dy
                key = (round(cx, 1), round(cy, 1))
                if key in visited:
                    continue
                visited.add(key)

                corridor = place_room(cx, cy, corridor_width, corridor_width, f"Corridor-{room_id}")
                if corridor:
                    rooms.append(corridor)
                    room_id += 1
                    new_frontier.append((cx, cy))

                    for rdx, rdy in [(-room_w, 0), (room_w, 0), (0, -room_d), (0, room_d)]:
                        rx, ry = cx + rdx, cy + rdy
                        room_box = box(rx, ry, rx + room_w, ry + room_d)
                        corridor_box = box(cx, cy, cx + corridor_width, cy + corridor_width)

                        if room_box.touches(corridor_box):
                            back_offset = 0.01
                            back_x = rx + (room_w if rdx < 0 else -back_offset if rdx > 0 else rx)
                            back_y = ry + (room_d if rdy < 0 else -back_offset if rdy > 0 else ry)
                            back_box = box(back_x, back_y, back_x + back_offset, back_y + back_offset)
                            obstructed = any(r.rect.intersects(back_box) for r in rooms if "Room" in r.name)
                            boundary_touch = (
                                abs(rx) < 0.01 or abs(ry) < 0.01 or
                                abs((rx + room_w) - total_width) < 0.01 or
                                abs((ry + room_d) - total_height) < 0.01
                            )

                            if not obstructed and boundary_touch:
                                placed = place_room(rx, ry, room_w, room_d, f"Room-{room_id}")
                                if placed:
                                    rooms.append(placed)
                                    room_id += 1

        frontier = new_frontier
        steps += 1
        if progress_callback:
            progress_callback(min(steps / max_steps, 1.0))

    return rooms, room_w, room_d

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
                            insert=(x_px, y_px),
                            size=(width * scale, height * scale),
                            preserveAspectRatio="none")
            dwg.add(img)

        color = "none" if "Room" in unit.name and room_image_url else (
            "lightblue" if "Room" in unit.name else
            "#ccc" if "Corridor" in unit.name else
            "orange" if "Lobby" in unit.name else
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
