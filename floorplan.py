# floorplan.py

from shapely.geometry import box
import svgwrite

class Room:
    def __init__(self, x, y, width, height, name):
        self.rect = box(x, y, x + width, y + height)
        self.name = name

def generate_double_corridor_plan(total_width, total_height, room_width, room_depth, corridor_width):
    upper_rooms = []
    lower_rooms = []
    units = []

    corridor_y = (total_height - corridor_width) / 2
    cols = int(total_width // room_width)

    # Lower rooms
    for i in range(cols):
        x = i * room_width
        y = corridor_y - room_depth
        lower_rooms.append(Room(x, y, room_width, room_depth, f"Room-L-{i}"))

    # Upper rooms
    for i in range(cols):
        x = i * room_width
        y = corridor_y + corridor_width
        upper_rooms.append(Room(x, y, room_width, room_depth, f"Room-U-{i}"))

    # Corridor
    corridor = Room(0, corridor_y, total_width, corridor_width, "Corridor")

    units = lower_rooms + upper_rooms + [corridor]
    return units

def render_svg(units, total_width, total_height, room_image_url=None):
    dwg = svgwrite.Drawing(size=(f"{total_width*20}px", f"{total_height*20}px"))
    scale = 20  # 1 meter = 20px

    for unit in units:
        x, y, x2, y2 = unit.rect.bounds
        width = x2 - x
        height = y2 - y
        x_px = x * scale
        y_px = (total_height - y2) * scale

        # Add background image if available and room
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
