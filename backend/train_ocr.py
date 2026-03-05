from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import shutil
import paddle
from textwrap import wrap
# print(paddle.device.get_device())
   
mode = "RGB"
# size = (400, 48) 
size = (320, 48)
# color = "white"
FONTS = [
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/comic.ttf",
    "C:/Windows/Fonts/arialbd.ttf"
]

base_path = os.path.dirname(os.path.abspath(__file__))

FONTS_DIR = os.path.join(base_path, "Fonts")

KOREAN_FONTS = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/malgunbd.ttf",
    "C:/Windows/Fonts/malgunsl.ttf",

    os.path.join(FONTS_DIR, "Dongdong.ttf"),
    os.path.join(FONTS_DIR, "Syongsyong.ttf"),
    os.path.join(FONTS_DIR, "YEONSUNG.ttf")

]
 

# KOREAN_FONTS = [f for f in ALL_KOREAN_FONTS if os.path.exists(f)]

# if not KOREAN_FONTS:
#     raise RuntimeError("No Korean fonts found in C:/Windows/Fonts. Please install a Korean font.")


def generate_training_image(text):

    bg_color = random.choice(["white", (240, 240, 240), (250, 250, 250)])

    img = Image.new(mode, size, color=bg_color)
    draw = ImageDraw.Draw(img)

    font_path = random.choice(KOREAN_FONTS)
    # font_size = random.randint(14,22)
    font_size = random.randint(16, 26)
    font = ImageFont.truetype(font_path, font_size)

    max_chars_per_line = 30
    lines = wrap(text, width=max_chars_per_line)

    line_height = font_size + 2
    total_height = line_height * len(lines)

    y_offset = (size[1] - total_height) // 2
    x_start = random.randint(5,15)

    for line in lines:
        draw.text((x_start, y_offset), line, fill="black", font=font)
        y_offset += line_height

    # text_size_x = random.randint(8,20)
    # text_size_y = random.randint(8,20)


    angle = random.uniform(-3,3)
    img = img.rotate(angle, fillcolor=bg_color if isinstance(bg_color, tuple) else(255,255,255))

    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    # img.save(f"training_{1}.png")

    # img.show()
    return img

# TEXTS = [
#     "WHAT?!",
#     "WHAT?!",
#     "LOOK OUT!",
#     "WAIT",
#     "Huh?",
#     "AH",
#     "IT FEELS WRONG",
#     "HAPPY ENDING",
#     "VILLANESS",
#     "MALE LEAD",
#     "FEMALE LEAD",
#     "ROMANCE NOVEL",
#     "MAGIC",
#     "SWORDSMANSHIP",
#     "KINGDOM",
#     "THE PRINCESS",
#     "THE DUKE OF",
#     "HELP",
#     "EMPIRE",
#     "HANDSOME",
#     "BEAUTIFUL",
#     "STOP",
#     "NO WAY",
#     "YES",
#     "NO",
#     "WHY?",
#     "OOPS",
#     "YAY",
#     "COME ON",
#     "WATCH OUT",
#     "GOTCHA",
#     "I DID IT",
#     "NOT AGAIN",
#     "SO COOL",
#     "PLEASE",
#     "RIGHT NOW",
#     "JUST A MINUTE",
#     "WAIT HERE",
#     "I'M SORRY",
#     "THANK YOU",
#     "GOOD LUCK",
#     "SEE YOU",
#     "WELCOME",
#     "CONGRATS",
#     "WHAT'S UP",
#     "NO PROBLEM",
#     "ALL DONE",
#     "ALMOST THERE",
#     "JUST IN TIME",
#     "TO BE CONTINUED",
#     "THE END",
#     "NEXT TIME",
#     "TO BE CONTINUED...",
#     "IT'S OVER",
#     "I'M HERE",
#     "I'M READY",
#     "BEGIN NOW",
#     "TRY AGAIN",
#     "FIGHT ON",
#     "WE WIN",
#     "RUN AWAY",
#     "HIDE QUICKLY",
#     "ESCAPE NOW",
#     "EXPLORE MORE",
#     "SEARCH HERE",
#     "TIME TO EAT",
#     "TAKE A REST",
#     "GO TO SLEEP",
#     "LET'S PLAY",
#     "WORK HARD",
#     "STUDY TIME",
#     "READ THIS",
#     "WRITE IT DOWN",
#     "DRAW SOMETHING",
#     "BUILD IT",
#     "CREATE ART",
#     "DESTROY IT",
#     "SAVE US",
#     "HELP OUT",
#     "TALK NOW",
#     "LISTEN UP",
#     "WATCH THIS",
#     "WAIT PATIENTLY",
#     "GO HOME",
#     "GO OUTSIDE",
#     "COME INSIDE",
#     "MOVE UP",
#     "MOVE DOWN",
#     "TURN LEFT",
#     "TURN RIGHT",
#     "GO FASTER",
#     "SLOW DOWN",
#     "START NOW",
#     "GO SOON",
#     "TRY LATER",
#     "AGAIN PLEASE",
#     "TOGETHER NOW",
#     "GO ALONE",
#     "GO BACK",
#     "MOVE FORWARD",
#     "STAY INSIDE",
#     "GO FAR",
#     "STAY CLOSE",
#     "BE QUIET",
#     "SPEAK UP",
#     "ACT CAREFULLY",
#     "MOVE QUICKLY",
#     "STAY SAFE",
#     "BE BRAVE",
#     "FEEL HAPPY",
#     "FEEL SAD",
#     "GET ANGRY",
#     "STAY CALM",
#     "BE EAGER",
#     "FEEL RELUCTANT",
#     "ACT CONFIDENT",
#     "FEEL NERVOUS",
#     "GET EXCITED",
#     "BE CURIOUS",
#     "ACT SUSPICIOUS",
#     "HOPE FOR BEST",
#     "FEEL FEAR",
#     "SHOW JOY",
#     "MOVE GRACEFULLY",
#     "STAY PEACEFUL",
#     "FEEL ANXIOUS",
#     "BE DETERMINED",
#     "ACT CARELESS",
#     "THINK DEEPLY",
#     "PLAY AROUND",
#     "BE SERIOUS",
#     "STAY SILENT",
#     "BE LOUD",
#     "KEEP SECRETS",
#     "BE OPEN",
#     "FEEL FREE",
#     "HURRY UP",
#     "GO SLOWLY",
#     "KEEP STEADY",
#     "FEEL UNSTEADY",
#     "ACT PURPOSEFUL",
#     "BE AIMLESS",
#     "ACT RANDOMLY",
#     "WORK SYSTEMATICALLY",
#     "THINK METHODICALLY",
#     "ACT CHAOTICALLY",
#     "STAY ORDERLY",
#     "BE DISORDERLY",
#     "MOVE ENERGETICALLY",
#     "FEEL TIRED",
#     "BE LAZY",
#     "STAY BUSY",
#     "BE QUIET",
#     "MAKE NOISE",
#     "STAY PEACEFUL",
#     "ACT VIOLENTLY",
#     "BE GENTLE",
#     "ACT ROUGH",
#     "SPEAK SOFTLY",
#     "TALK HARSHLY",
#     "BE SWEET",
#     "ACT BITTERLY",
#     "POISON",
#     "DEMONIC",
#     "ANGELIC",
#     "OH MY GOD",
#     "READERS",
#     "VILLAGERS",
#     "OFFICIAL"
# ]

TEXTS = [
    "WHAT DO YOU THINK YOU'RE DOING?!",
    "HOW COULD THIS HAVE HAPPENED?",
    "WHERE DID EVERYONE GO?",
    "WHY DIDN'T YOU TELL ME SOONER?",
    "WHEN DID YOU FIGURE IT OUT?",
    "WHO TOLD YOU ABOUT THIS?",
    "CAN YOU BELIEVE WHAT JUST HAPPENED?",
    "IS THIS REALLY HAPPENING RIGHT NOW?",
    "WHAT'S GOING ON OVER THERE?",
    "DID YOU SEE THAT JUST NOW?",
     "I CAN'T BELIEVE MY EYES!",
    "THIS IS ABSOLUTELY INCREDIBLE!",
    "YOU'VE GOT TO BE KIDDING ME!",
    "THERE'S NO WAY THAT'S POSSIBLE!",
    "I NEVER THOUGHT I'D SEE THIS DAY!",
    "THIS CHANGES EVERYTHING WE KNOW!",
    "WE'RE RUNNING OUT OF TIME!",
    "IT'S NOW OR NEVER!",
    "EVERYTHING DEPENDS ON THIS MOMENT!",
    "THE FATE OF THE KINGDOM IS AT STAKE!",
     "WE NEED TO GET OUT OF HERE NOW!",
    "HURRY UP BEFORE IT'S TOO LATE!",
    "MOVE FASTER OR WE'LL BE CAUGHT!",
    "SOMEONE HELP ME RIGHT NOW!",
    "GET AWAY FROM THERE IMMEDIATELY!",
    "RUN AS FAST AS YOU CAN!",
    "DON'T JUST STAND THERE, DO SOMETHING!",
    "QUICK, HIDE BEFORE THEY SEE US!",
    "WE HAVE TO STOP THEM SOMEHOW!",
    "GRAB ONTO SOMETHING QUICKLY!",
    "I HAVE SOMETHING IMPORTANT TO TELL YOU",
    "LISTEN CAREFULLY TO WHAT I'M SAYING",
    "LET ME EXPLAIN THE SITUATION",
    "YOU NEED TO HEAR THE WHOLE STORY",
    "THERE'S MORE TO IT THAN THAT",
    "IT'S NOT WHAT YOU THINK IT IS",
    "I KNOW EXACTLY WHAT YOU MEAN",
    "THAT'S EXACTLY WHAT I WAS THINKING",
    "I COMPLETELY AGREE WITH YOU",
    "YOU MAKE A VERY GOOD POINT",
    "I'M SO HAPPY I COULD CRY!",
    "THIS IS THE WORST DAY EVER!",
    "I'VE NEVER BEEN SO SCARED IN MY LIFE!",
    "MY HEART IS BEATING SO FAST!",
    "I FEEL LIKE I'M GOING TO FAINT!",
    "I'M COMPLETELY OVERWHELMED RIGHT NOW!",
    "THIS IS MORE THAN I CAN HANDLE!",
    "I DON'T KNOW WHAT TO DO ANYMORE!",
    "EVERYTHING IS FALLING APART!",
    "I CAN FINALLY BREATHE AGAIN!",
    "HERE'S WHAT WE'RE GOING TO DO",
    "I HAVE A PLAN THAT MIGHT WORK",
    "LET'S TRY A DIFFERENT APPROACH",
    "WE NEED TO THINK THIS THROUGH CAREFULLY",
    "THERE HAS TO BE ANOTHER WAY",
    "MAYBE WE SHOULD RECONSIDER THIS",
    "I THINK I KNOW HOW TO FIX THIS",
    "FOLLOW MY LEAD AND STAY CLOSE",
    "TRUST ME, I KNOW WHAT I'M DOING",
    "THIS IS OUR ONLY CHANCE LEFT",
    "I FINALLY UNDERSTAND EVERYTHING NOW!",
    "SO THAT'S WHAT WAS GOING ON!",
    "IT ALL MAKES SENSE NOW!",
    "I SHOULD HAVE REALIZED THIS SOONER!",
    "THE ANSWER WAS RIGHT IN FRONT OF US!",
    "I JUST FIGURED OUT THE TRUTH!",
    "THERE'S SOMETHING YOU NEED TO KNOW!",
    "I DISCOVERED SOMETHING INCREDIBLE!",
    "YOU WON'T BELIEVE WHAT I FOUND OUT!",
    "THE SECRET HAS FINALLY BEEN REVEALED!",
    "DON'T EVEN THINK ABOUT IT!",
    "YOU'LL REGRET THIS DECISION!",
    "STAY AWAY FROM ME RIGHT NOW!",
    "THIS IS YOUR LAST WARNING!",
    "YOU'RE MAKING A TERRIBLE MISTAKE!",
    "THERE WILL BE CONSEQUENCES FOR THIS!",
    "YOU HAVE NO IDEA WHAT YOU'RE DEALING WITH!",
    "BE CAREFUL WHAT YOU WISH FOR!",
    "YOU'RE PLAYING WITH FIRE HERE!",
    "MARK MY WORDS, YOU'LL SEE!",
    "MEANWHILE, IN ANOTHER PART OF TOWN...",
    "SEVERAL HOURS LATER...",
    "THE NEXT MORNING...",
    "BACK AT THE CASTLE...",
    "SOMEWHERE FAR AWAY...",
    "AT THAT VERY MOMENT...",
    "LITTLE DID THEY KNOW...",
    "UNBEKNOWNST TO THEM...",
    "AS IT TURNS OUT...",
    "TO BE CONTINUED IN THE NEXT CHAPTER...",
    "I REMEMBER IT LIKE IT WAS YESTERDAY",
    "IT ALL STARTED A LONG TIME AGO",
    "THAT TAKES ME BACK TO WHEN...",
    "I'LL NEVER FORGET THAT DAY",
    "IF ONLY I COULD GO BACK IN TIME",
    "THINGS WERE SO DIFFERENT BACK THEN",
    "I WISH I COULD CHANGE THE PAST",
    "THOSE WERE THE GOOD OLD DAYS",
    "EVERYTHING HAS CHANGED SINCE THEN",
    "I CAN BARELY REMEMBER ANYMORE",
    "YOU MEAN EVERYTHING TO ME!",
    "I COULD NEVER DO THIS WITHOUT YOU!",
    "YOU'RE THE BEST FRIEND I'VE EVER HAD!",
    "I'VE ALWAYS LOOKED UP TO YOU!",
    "YOU'RE THE ONLY ONE WHO UNDERSTANDS!",
    "I TRUST YOU WITH MY LIFE!",
    "WE MAKE A GREAT TEAM TOGETHER!",
    "I'LL ALWAYS BE HERE FOR YOU!",
    "YOU CAN COUNT ON ME NO MATTER WHAT!",
    "WE'VE BEEN THROUGH SO MUCH TOGETHER!",
    "I'M NOT SURE THIS IS A GOOD IDEA",
    "SOMETHING DOESN'T FEEL RIGHT ABOUT THIS",
    "I HAVE A BAD FEELING ABOUT THIS",
    "ARE WE REALLY DOING THE RIGHT THING?",
    "MAYBE WE SHOULD THINK ABOUT THIS MORE",
    "I'M STARTING TO HAVE SECOND THOUGHTS",
    "WHAT IF SOMETHING GOES WRONG?",
    "IS IT TOO LATE TO TURN BACK NOW?",
    "I DON'T KNOW IF I CAN DO THIS",
    "THERE'S TOO MUCH AT RISK HERE",
    "I WON'T GIVE UP NO MATTER WHAT!",
    "NOTHING CAN STOP ME NOW!",
    "I'LL DO WHATEVER IT TAKES!",
    "THIS IS WHAT I WAS MEANT TO DO!",
    "I'VE MADE UP MY MIND ALREADY!",
    "THERE'S NO TURNING BACK NOW!",
    "I'M READY TO FACE ANY CHALLENGE!",
    "BRING IT ON, I'M NOT AFRAID!",
    "I'LL PROVE EVERYONE WRONG!",
    "JUST WATCH ME AND SEE!",
    "I DON'T UNDERSTAND WHAT YOU MEAN",
    "THAT DOESN'T MAKE ANY SENSE TO ME",
    "CAN YOU EXPLAIN THAT AGAIN PLEASE?",
    "I THINK THERE'S BEEN A MISUNDERSTANDING",
    "THAT'S NOT WHAT I MEANT AT ALL!",
    "YOU'VE GOT IT ALL WRONG!",
    "LET ME CLARIFY WHAT I SAID",
    "I'M COMPLETELY LOST RIGHT NOW",
    "NONE OF THIS MAKES ANY SENSE!",
    "HOW DID WE GET TO THIS POINT?",
    "I'M SO SORRY FOR EVERYTHING!",
    "I DIDN'T MEAN FOR THIS TO HAPPEN!",
    "PLEASE FORGIVE ME FOR MY MISTAKES!",
    "I WISH I COULD TAKE IT ALL BACK!",
    "IF ONLY I HAD LISTENED TO YOU!",
    "I SHOULD HAVE KNOWN BETTER THAN THIS!",
    "IT'S ALL MY FAULT THIS HAPPENED!",
    "I'LL MAKE IT UP TO YOU SOMEHOW!",
    "GIVE ME ANOTHER CHANCE PLEASE!",
    "I PROMISE I'LL DO BETTER NEXT TIME!",
    "DON'T GIVE UP JUST YET!",
    "THERE'S STILL HOPE FOR US!",
    "WE CAN GET THROUGH THIS TOGETHER!",
    "THINGS WILL GET BETTER SOON!",
    "KEEP PUSHING FORWARD NO MATTER WHAT!",
    "BELIEVE IN YOURSELF MORE!",
    "YOU'RE STRONGER THAN YOU THINK!",
    "WE'VE OVERCOME WORSE THAN THIS BEFORE!",
    "THE BEST IS YET TO COME!",
    "NEVER LOSE FAITH IN YOURSELF!",
]

# Completely AI generated texts (idk korean)
KOREAN_TEXTS = [
    # Basic exclamations
    "뭐야?!",
    "헉!",
    "어?",
    "아!",
    "와!",
    "에?!",
    "진짜?",
    "정말?",
    "거짓말!",
    "믿을 수 없어!",
    
    # Warnings/Actions
    "조심해!",
    "위험해!",
    "도망쳐!",
    "빨리!",
    "기다려!",
    "멈춰!",
    "가지마!",
    "도와줘!",
    "살려줘!",
    "이리와!",
    
    # Questions
    "뭐야?",
    "왜?",
    "어디?",
    "누구?",
    "언제?",
    "어떻게?",
    "뭐라고?",
    "무슨 일이야?",
    "괜찮아?",
    "정말이야?",
    
    # Casual responses
    "알았어",
    "몰라",
    "미안해",
    "고마워",
    "싫어",
    "좋아",
    "당연하지",
    "그래",
    "아니",
    "맞아",
    
    # Emotions
    "기뻐!",
    "슬퍼...",
    "화나!",
    "무서워...",
    "부끄러워",
    "설레",
    "짜증나",
    "힘들어",
    "외로워",
    "걱정돼",
    
    # Common phrases
    "알겠어",
    "괜찮아",
    "신경쓰지마",
    "잘했어",
    "수고했어",
    "힘내",
    "포기하지마",
    "할 수 있어",
    "믿어",
    "사랑해",
    
    # Webtoon-specific
    "그렇구나",
    "그럴리가",
    "말도 안돼",
    "당연하잖아",
    "그런 것 같아",
    "아무것도 아니야",
    "별일 아니야",
    "농담이야",
    "진심이야",
    "확실해?",
    
    # Longer dialogue
    "무슨 일이 있었던 거야?",
    "정말 믿을 수 없어",
    "어떻게 된 거야?",
    "내가 도와줄게",
    "걱정하지 않아도 돼",
    "괜찮을 거야",
    "너무 놀랐어",
    "예상하지 못했어",
    "생각해볼게",
    "나중에 얘기하자",
    
    # Formal speech
    "죄송합니다",
    "감사합니다",
    "괜찮으세요?",
    "도와드릴까요?",
    "실례합니다",
    "안녕하세요",
    "안녕히 가세요",
    "잘 부탁드립니다",
    "수고하셨습니다",
    "알겠습니다",
    
    # Character descriptions
    "주인공",
    "악당",
    "영웅",
    "공주",
    "왕자",
    "마법사",
    "전사",
    "도적",
    "성직자",
    "기사",
    
    # Fantasy terms
    "마법",
    "검술",
    "왕국",
    "제국",
    "성",
    "던전",
    "몬스터",
    "드래곤",
    "요정",
    "악마",
    
    # Romance
    "좋아해",
    "사랑해",
    "보고싶어",
    "그리워",
    "설레",
    "떨려",
    "행복해",
    "완벽해",
    "운명이야",
    "영원히",
    
    # Action scenes
    "공격해!",
    "방어해!",
    "피해!",
    "반격해!",
    "도망쳐!",
    "싸워!",
    "이겨!",
    "지켜!",
    "막아!",
    "던져!",
    
    # Time/Place
    "지금",
    "나중에",
    "여기",
    "저기",
    "어디든",
    "언제든",
    "항상",
    "절대",
    "때때로",
    "가끔",
    
    # Numbers/Counting
    "하나",
    "둘",
    "셋",
    "첫번째",
    "두번째",
    "마지막",
    "전부",
    "아무것도",
    "모두",
    "아무도",
    
    # Status/Condition
    "살았어",
    "죽었어",
    "다쳤어",
    "괜찮아",
    "아파",
    "건강해",
    "피곤해",
    "배고파",
    "목말라",
    "졸려",
    
    # Directions
    "앞으로",
    "뒤로",
    "왼쪽",
    "오른쪽",
    "위로",
    "아래로",
    "이쪽",
    "저쪽",
    "직진",
    "돌아",
    
    # Longer sentences
    "내가 널 지켜줄게",
    "함께 이겨내자",
    "포기하지 않을 거야",
    "너를 믿어",
    "우리가 할 수 있어",
    "이건 시작일 뿐이야",
    "끝까지 함께할게",
    "너 혼자가 아니야",
    "내 곁에 있어줘",
    "절대 잊지 않을게",
    "다시 한번 해보자",
    "이번엔 다를 거야",
    "모든 게 괜찮을 거야",
    "걱정하지 않아도 돼",
    "내가 책임질게",
    "약속할게",
    "진심으로 고마워",
    "미안하지만 안돼",
    "정말 대단해",
    "너무 멋있어",
]


# if os.path.exists("training_data"):
#     shutil.rmtree("training_data")

# # English training data
# os.makedirs("training_data/train", exist_ok=True)
# os.makedirs("training_data/val", exist_ok=True) 

# Korean training data
os.makedirs("korean_training_data/train", exist_ok=True)
os.makedirs("korean_training_data/val", exist_ok=True) 
  
for i in range(20000):

    text = random.choice(KOREAN_TEXTS)
    img_name = f"training_{i}.png"

    img = generate_training_image(text)
    content = f"{img_name}\t{text}\n"


    if i<16000:

        img.save(f"korean_training_data/train/{img_name}")

        with open("korean_training_data/train/labels.txt", 'a', encoding='utf-8') as file:
            file.write(content)
    else:

        img.save(f"korean_training_data/val/{img_name}")

        with open("korean_training_data/val/labels.txt", 'a', encoding='utf-8') as file:
            file.write(content)

