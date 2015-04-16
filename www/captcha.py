from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

params = [1 - float(random.randint(1, 2)) / 100, 0, 0, 0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500, 0.001,
              float(random.randint(1, 2)) / 500]


def rnd_char():
    return chr(random.randint(65, 90))


def rnd_color():
    return random.randint(127, 255), random.randint(127, 255), random.randint(127, 255)


def rndcolor_background():
    return random.randint(0, 127), random.randint(0, 127), random.randint(0, 127)


def generate_captcha():
    global params
    height = 34
    width = 120
    image = Image.new('RGB', (width, height))
    font = ImageFont.truetype('static/fonts/arial.ttf', 28)
    draw = ImageDraw.Draw(image)
    # Fill the background with random color
    for x in range(width):
        for y in range(height):
            draw.point((x,y), fill=rndcolor_background())
    # Generate 4-letter captcha code
    cap = rnd_char() + rnd_char() + rnd_char() + rnd_char()
    draw.text((10, 0), cap, fill=rnd_color(), font=font)
    # Blur out
    image = image.transform((width, height), Image.PERSPECTIVE, params)
    image = image.filter(ImageFilter.GaussianBlur)
    # Get Image Stream Object
    stream = StringIO.StringIO()
    image.save(stream, format="GIF")
    return cap, stream
