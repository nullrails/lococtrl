from PIL import Image, ImageFont, ImageDraw

width = 128
height = 160

def genShutdownScreen():
    image = Image.new('RGB', (width, height), color=(60,60,60))
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.load_default()

    # Define text and text color
    text = "Shutting down. Please wait for the screen to whiteout before removing power."
    text_color = (255, 255, 0)

    # Define max width for text wrapping
    max_width = width - 15  # Leave some margin

    # Wrap text
    lines = []
    line = ""
    for word in text.split():
        if draw.textsize(line + word, font=font)[0] <= max_width:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Calculate total text height
    total_text_height = sum(draw.textsize(line, font=font)[1] for line in lines)

    # Calculate text start y position
    text_start_y = (height - total_text_height) // 2

    # Draw wrapped text
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        text_x = (width - text_width) // 2
        draw.text((text_x, text_start_y), line, fill=text_color, font=font)
        text_start_y += text_height

    return image

def genMsgScreen(msg, bg=(60,60,60),fg=(255,255,0)):
    image = Image.new('RGB', (width, height), color=bg)
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.load_default()

    # Define text and text color
    text = msg
    text_color = fg

    # Define max width for text wrapping
    max_width = width - 15  # Leave some margin

    # Wrap text
    lines = []
    line = ""
    for word in text.split():
        if draw.textsize(line + word, font=font)[0] <= max_width:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Calculate total text height
    total_text_height = sum(draw.textsize(line, font=font)[1] for line in lines)

    # Calculate text start y position
    text_start_y = (height - total_text_height) // 2

    # Draw wrapped text
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        text_x = (width - text_width) // 2
        draw.text((text_x, text_start_y), line, fill=text_color, font=font)
        text_start_y += text_height

    return image
