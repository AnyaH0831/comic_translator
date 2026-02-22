from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import shutil

mode = "RGB"
size = (200, 100) 
# color = "white"
FONTS = [
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/comic.ttf",
    "C:/Windows/Fonts/arialbd.ttf"
]


def generate_training_image(text):

    bg_color = random.choice(["white", (240, 240, 240), (250, 250, 250)])

    img = Image.new(mode, size, color=bg_color)
    draw = ImageDraw.Draw(img)

    font_path = random.choice(FONTS)
    font_size = random.randint(18,28)
    font = ImageFont.truetype(font_path, font_size)

    text_size_x = random.randint(8,20)
    text_size_y = random.randint(8,20)


    draw.text((text_size_x, text_size_y), text.upper(), fill="black", font=font)

    angle = random.uniform(-3,3)
    img = img.rotate(angle, fillcolor=bg_color if isinstance(bg_color, tuple) else(255,255,255))

    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    # img.save(f"training_{1}.png")

    # img.show()
    return img

TEXTS = [
    "WHAT?!",
    "LOOK OUT!",
    "THAT'S THE...",
    "WAIT",
    "LOOK OUT",
    "How can it be",
    "Huh?",
    "AH",
    "IT FEELS WRONG",
    "HAPPY ENDING",
    "VILLANESS",
    "MALE LEAD",
    "FEMALE LEAD",
    "ROMANCE NOVEL",
    "MAGIC",
    "SWORDSMANSHIP",
    "KINGDOM",
    "THE PRINCESS",
    "THE DUKE OF"
]


if os.path.exists("training_data"):
    shutil.rmtree("training_data")
os.makedirs("training_data")

for i in range(1000):


    text = random.choice(TEXTS)
    img_name = f"training_{i}.png"

    img = generate_training_image(text)

    img.save(f"training_data/{img_name}")

    file_path = "training_data/labels.txt"
    content = f"{img_name}\t{text}\n"

    with open(file_path, 'a') as file:
        file.write(content)

