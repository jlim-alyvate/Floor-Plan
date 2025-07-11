def render_svg(units, total_width, total_height, room_image_url=None):
    import svgwrite
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
                         size=(width*scale, height*scale),
                         fill=color,
                         stroke="black",
                         stroke_width=1))
        dwg.add(dwg.text(unit.name,
                         insert=((x + width/2)*scale, (total_height - y2 + height/2)*scale),
                         text_anchor="middle",
                         font_size="8px",
                         fill="black"))

    return dwg.tostring()
