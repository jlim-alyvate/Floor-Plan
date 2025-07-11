# floorplan.py

from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name):
        self.rect = box(x, y, x + width, y + height)
        self.name = name

def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width):
    room_width, room_depth = room_aspect_ratio

    # Layout: 1 row of rooms above corridor, 1 row below
    cols = int(total_width // room_width)
    corridor_y = (total_height - corridor_width) / 2

    units = []

    # Lower row (flush with bottom edge of corridor)
    for j in range(cols):
        x = j * room_width
        y = corridor_y - room_depth
        units.append(Room(x, y, room_width, room_depth, f"Room-L-0-{j}"))

    # Upper row (flush with top edge of corridor)
    for j in range(cols):
        x = j * room_width
        y = corridor_y + corridor_width
        units.append(Room(x, y, room_width, room_depth, f"Room-U-0-{j}"))

    # Corridor (centered vertically)
    corridor = Room(0, corridor_y, total_width, corridor_width, "Corridor")
    units.append(corridor)

    return units, room_width, room_depth

def render_svg(units, total_width, total_height, room_image_url=None, room_w=3, room_d=5):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20  # 1m = 20px

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
                              preserveAspectRatio="xMidYMid slice"))

        color = "none" if "Room" in unit.name and room_image_url else ("lightblue" if "Room" in unit.name else "#ccc")
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
