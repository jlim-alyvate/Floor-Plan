# floorplan.py
import numpy as np
from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation

def generate_optimized_layout(total_width, total_height, room_w, room_d, corridor_w, progress_callback=None):
    grid_w = int(total_width // room_w)
    grid_h = int(total_height // room_d)
    layout = [[None for _ in range(grid_w)] for _ in range(grid_h)]
    units = []

    center_x = grid_w // 2
    center_y = grid_h // 2
    layout[center_y][center_x] = 'Lobby'
    units.append(Room(center_x * room_w, center_y * room_d, corridor_w, corridor_w, "Lobby"))

    corridors = [(center_y, center_x)]
    visited = set(corridors)
    room_id = 0
    max_rooms = int(grid_w * grid_h * 0.8)

    while corridors and room_id < max_rooms:
        y, x = corridors.pop(0)
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < grid_h and 0 <= nx < grid_w and (ny, nx) not in visited:
                layout[ny][nx] = 'Corridor'
                visited.add((ny, nx))
                corridors.append((ny, nx))
                units.append(Room(nx * room_w, ny * room_d, corridor_w, corridor_w, f"Corridor-{room_id}"))
                room_id += 1

                # attempt room placement
                for rdy, rdx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ry, rx = ny + rdy, nx + rdx
                    by, bx = ry + rdy, rx + rdx
                    if 0 <= ry < grid_h and 0 <= rx < grid_w and layout[ry][rx] is None:
                        if not (0 <= by < grid_h and 0 <= bx < grid_w and layout[by][bx] is not None):
                            layout[ry][rx] = f"Room-{room_id}"
                            units.append(Room(rx * room_w, ry * room_d, room_w, room_d, f"Room-{room_id}"))
                            room_id += 1

        if progress_callback:
            progress_callback(room_id / max_rooms)

    return units

def render_svg(units, total_width, total_height):
    scale = 20
    dwg = svgwrite.Drawing(size=(f"{total_width*scale}px", f"{total_height*scale}px"))

    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width = x2 - x
        height = y2 - y
        x_px = x * scale
        y_px = (total_height - y2) * scale

        fill = "#ADD8E6" if "Room" in unit.name else ("orange" if "Lobby" in unit.name else "#ccc")

        dwg.add(dwg.rect(insert=(x_px, y_px),
                         size=(width * scale, height * scale),
                         fill=fill,
                         stroke="black",
                         stroke_width=1))

        dwg.add(dwg.text(unit.name,
                         insert=(x_px + width * scale / 2, y_px + height * scale / 2),
                         text_anchor="middle",
                         font_size="8px",
                         fill="black"))

    return dwg.tostring()
