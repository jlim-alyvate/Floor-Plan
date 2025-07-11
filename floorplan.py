def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width):
    room_width, room_depth = room_aspect_ratio

    # Ensure only one row of rooms directly above and below corridor
    rows_per_side = 1
    cols = int(total_width // room_width)

    actual_room_depth = room_depth
    corridor_y = (total_height - corridor_width) / 2

    units = []

    # Lower row — flush against bottom of corridor
    for j in range(cols):
        x = j * room_width
        y = corridor_y - actual_room_depth
        units.append(Room(x, y, room_width, actual_room_depth, f"Room-L-0-{j}"))

    # Upper row — flush against top of corridor
    for j in range(cols):
        x = j * room_width
        y = corridor_y + corridor_width
        units.append(Room(x, y, room_width, actual_room_depth, f"Room-U-0-{j}"))

    # Central corridor
    corridor = Room(0, corridor_y, total_width, corridor_width, "Corridor")
    units.append(corridor)
