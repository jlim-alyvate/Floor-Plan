import streamlit as st
import numpy as np
from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name, rotation=0):
        self.rect = box(x, y, x + width, y + height)
        self.name = name
        self.rotation = rotation

def generate_optimized_layout(total_width, total_height, room_w, room_d, corridor_w, progress_callback=None):
    grid_size = 0.5  # meters per grid cell for precision
    cols = int(total_width / grid_size)
    rows = int(total_height / grid_size)
    grid = np.zeros((rows, cols))

    def coords_to_index(x, y):
        return int(y / grid_size), int(x / grid_size)

    def can_place(x, y, w, h):
        top, left = coords_to_index(x, y)
        bottom, right = coords_to_index(x + w, y + h)
        if bottom >= rows or right >= cols:
            return False
        return np.all(grid[top:bottom, left:right] == 0)

    def mark_grid(x, y, w, h):
        top, left = coords_to_index(x, y)
        bottom, right = coords_to_index(x + w, y + h)
        grid[top:bottom, left:right] = 1

    rooms = []
    corridors = []

    # Place central lobby
    cx = (total_width - corridor_w) / 2
    cy = (total_height - corridor_w) / 2
    lobby = Room(cx, cy, corridor_w, corridor_w, "Lobby")
    mark_grid(cx, cy, corridor_w, corridor_w)
    corridors.append(lobby)

    # Expand corridors and place rooms
    frontier = [(cx, cy)]
    room_count = 0
    max_rooms = int((total_width * total_height * 0.8) / (room_w * room_d))

    while frontier and room_count < max_rooms:
        next_frontier = []
        for fx, fy in frontier:
            for dx, dy in [(room_w + corridor_w, 0), (-room_w - corridor_w, 0), (0, room_d + corridor_w), (0, -room_d - corridor_w)]:
                cx_new, cy_new = fx + dx, fy + dy
                if not can_place(cx_new, cy_new, corridor_w, corridor_w):
                    continue
                corridor = Room(cx_new, cy_new, corridor_w, corridor_w, f"Corridor-{len(corridors)}")
                mark_grid(cx_new, cy_new, corridor_w, corridor_w)
                corridors.append(corridor)
                next_frontier.append((cx_new, cy_new))

                # Place room beside corridor
                for rdx, rdy in [(room_w, 0), (-room_w, 0), (0, room_d), (0, -room_d)]:
                    rx, ry = cx_new + rdx, cy_new + rdy
                    if not can_place(rx, ry, room_w, room_d):
                        continue

                    # Ensure room has one side on corridor, one side on building boundary
                    room_rect = box(rx, ry, rx + room_w, ry + room_d)
                    corridor_rect = box(cx_new, cy_new, cx_new + corridor_w, cy_new + corridor_w)
                    if not room_rect.touches(corridor_rect):
                        continue
                    # Check room faces building boundary
                    if not (rx <= 0 or ry <= 0 or rx + room_w >= total_width or ry + room_d >= total_height):
                        continue

                    room = Room(rx, ry, room_w, room_d, f"Room-{room_count}")
                    mark_grid(rx, ry, room_w, room_d)
                    rooms.append(room)
                    room_count += 1
                    break  # place one room per corridor

        frontier = next_frontier
        if progress_callback:
            progress_callback(min(room_count / max_rooms, 1.0))

    return rooms + corridors

def render_svg(units, total_width, total_height):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20
    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width = x2 - x
        height = y2 - y
        x_px = x * scale
        y_px = (total_height - y2) * scale
        fill = "#ccc" if "Corridor" in unit.name else ("orange" if "Lobby" in unit.name else "lightblue")
        dwg.add(dwg.rect(insert=(x_px, y_px), size=(width * scale, height * scale), fill=fill, stroke="black"))
        dwg.add(dwg.text(unit.name, insert=((x + width / 2) * scale, (total_height - y2 + height / 2) * scale),
                         text_anchor="middle", font_size="8px", fill="black"))
    return dwg.tostring()

    return dwg.tostring()
