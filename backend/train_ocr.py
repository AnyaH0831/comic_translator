from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import shutil
import paddle
# print(paddle.device.get_device())

mode = "RGB"
size = (400, 48) 
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


    draw.text((text_size_x, text_size_y), text, fill="black", font=font)

    angle = random.uniform(-3,3)
    img = img.rotate(angle, fillcolor=bg_color if isinstance(bg_color, tuple) else(255,255,255))

    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    # img.save(f"training_{1}.png")

    # img.show()
    return img

TEXTS = [
    "WHAT?!",
    "WHAT?!",
    "LOOK OUT!",
    "WAIT",
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
    "THE DUKE OF",
    "HELP",
    "EMPIRE",
    "HANDSOME",
    "BEAUTIFUL",
    "STOP",
    "NO WAY",
    "YES",
    "NO",
    "WHY?",
    "OOPS",
    "YAY",
    "COME ON",
    "WATCH OUT",
    "GOTCHA",
    "I DID IT",
    "NOT AGAIN",
    "SO COOL",
    "PLEASE",
    "RIGHT NOW",
    "JUST A MINUTE",
    "WAIT HERE",
    "I'M SORRY",
    "THANK YOU",
    "GOOD LUCK",
    "SEE YOU",
    "WELCOME",
    "CONGRATS",
    "WHAT'S UP",
    "NO PROBLEM",
    "ALL DONE",
    "ALMOST THERE",
    "JUST IN TIME",
    "TO BE CONTINUED",
    "THE END",
    "NEXT TIME",
    "TO BE CONTINUED...",
    "IT'S OVER",
    "I'M HERE",
    "I'M READY",
    "BEGIN NOW",
    "TRY AGAIN",
    "FIGHT ON",
    "WE WIN",
    "RUN AWAY",
    "HIDE QUICKLY",
    "ESCAPE NOW",
    "EXPLORE MORE",
    "SEARCH HERE",
    "TIME TO EAT",
    "TAKE A REST",
    "GO TO SLEEP",
    "LET'S PLAY",
    "WORK HARD",
    "STUDY TIME",
    "READ THIS",
    "WRITE IT DOWN",
    "DRAW SOMETHING",
    "BUILD IT",
    "CREATE ART",
    "DESTROY IT",
    "SAVE US",
    "HELP OUT",
    "TALK NOW",
    "LISTEN UP",
    "WATCH THIS",
    "WAIT PATIENTLY",
    "GO HOME",
    "GO OUTSIDE",
    "COME INSIDE",
    "MOVE UP",
    "MOVE DOWN",
    "TURN LEFT",
    "TURN RIGHT",
    "GO FASTER",
    "SLOW DOWN",
    "START NOW",
    "GO SOON",
    "TRY LATER",
    "AGAIN PLEASE",
    "TOGETHER NOW",
    "GO ALONE",
    "GO BACK",
    "MOVE FORWARD",
    "STAY INSIDE",
    "GO FAR",
    "STAY CLOSE",
    "BE QUIET",
    "SPEAK UP",
    "ACT CAREFULLY",
    "MOVE QUICKLY",
    "STAY SAFE",
    "BE BRAVE",
    "FEEL HAPPY",
    "FEEL SAD",
    "GET ANGRY",
    "STAY CALM",
    "BE EAGER",
    "FEEL RELUCTANT",
    "ACT CONFIDENT",
    "FEEL NERVOUS",
    "GET EXCITED",
    "BE CURIOUS",
    "ACT SUSPICIOUS",
    "HOPE FOR BEST",
    "FEEL FEAR",
    "SHOW JOY",
    "MOVE GRACEFULLY",
    "STAY PEACEFUL",
    "FEEL ANXIOUS",
    "BE DETERMINED",
    "ACT CARELESS",
    "THINK DEEPLY",
    "PLAY AROUND",
    "BE SERIOUS",
    "STAY SILENT",
    "BE LOUD",
    "KEEP SECRETS",
    "BE OPEN",
    "FEEL FREE",
    "HURRY UP",
    "GO SLOWLY",
    "KEEP STEADY",
    "FEEL UNSTEADY",
    "ACT PURPOSEFUL",
    "BE AIMLESS",
    "ACT RANDOMLY",
    "WORK SYSTEMATICALLY",
    "THINK METHODICALLY",
    "ACT CHAOTICALLY",
    "STAY ORDERLY",
    "BE DISORDERLY",
    "MOVE ENERGETICALLY",
    "FEEL TIRED",
    "BE LAZY",
    "STAY BUSY",
    "BE QUIET",
    "MAKE NOISE",
    "STAY PEACEFUL",
    "ACT VIOLENTLY",
    "BE GENTLE",
    "ACT ROUGH",
    "SPEAK SOFTLY",
    "TALK HARSHLY",
    "BE SWEET",
    "ACT BITTERLY",
    "POSION",
    "DEMONIC",
    "ANGELIC",
    "OH MY GOD",
    "READERS",
    "VILLIAGERS",
    "OFFICIAL"
]



if os.path.exists("training_data"):
    shutil.rmtree("training_data")
os.makedirs("training_data/train")
os.makedirs("training_data/val")

for i in range(5000):


    text = random.choice(TEXTS)
    img_name = f"training_{i}.png"

    img = generate_training_image(text)
    content = f"{img_name}\t{text}\n"


    if i<4000:

        img.save(f"training_data/train/{img_name}")

        with open("training_data/train/labels.txt", 'a') as file:
            file.write(content)
    else:

        img.save(f"training_data/val/{img_name}")

        with open("training_data/val/labels.txt", 'a') as file:
            file.write(content)

