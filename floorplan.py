def generate_auto_scaled_plan(total_width, total_height, room_aspect_ratio, corridor_width):
    room_width, room_depth = room_aspect_ratio

    cols = int(total_width // room_width)
    corridor_y = (total_height - corridor_width) / 2
    lobby_width = 6
    lobby_depth = corridor_width  # treat lobby as part of corridor
    lift_width = 2
    lift_depth = 2

    units = []

    # Shared lobby (centered)
    lobby_x = (total_width - lobby_width) / 2
    lobby_y = corridor_y
    units.append(Room(lobby_x, lobby_y, lobby_width, lobby_depth, "Lobby"))

    # Lifts above lobby
    lift1_x = lobby_x + 0.5
    lift2_x = lobby_x + lobby_width - lift_width - 0.5
    lift_y = lobby_y + lobby_depth
    units.append(Room(lift1_x, lift_y, lift_width, lift_depth, "Lift-1"))
    units.append(Room(lift2_x, lift_y, lift_width, lift_depth, "Lift-2"))

    # Corridor spans full width (including over the lobby)
    units.append(Room(0, corridor_y, total_width, corridor_width, "Corridor"))

    # Place one room per side per column, excluding lobby/lift zone
    for j in range(cols):
        x = j * room_width

        # Skip overlapping the lift/lobby zone
        overlaps_lobby = x + room_width > lobby_x and x < lobby_x + lobby_width

        if not overlaps_lobby:
            # Room below corridor
            y_lower = corridor_y - room_depth
            units.append(Room(x, y_lower, room_width, room_depth, f"Room-L-0-{j}"))

            # Room above corridor
            y_upper = corridor_y + corridor_width
            units.append(Room(x, y_upper, room_width, room_depth, f"Room-U-0-{j}"))

    return units, room_width, room_depth
