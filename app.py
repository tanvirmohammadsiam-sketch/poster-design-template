from flask import Flask, render_template, request, send_file
from rembg import remove
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import os
import uuid
import numpy as np
app = Flask(__name__)

# -------------------------
# PATHS
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH = os.path.join(BASE_DIR, "static", "template.jpeg")
FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "SolaimanLipi.ttf")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# -------------------------
# IMAGE PROCESS FUNCTION
# -------------------------
def process_image(input_path, name, designation):

    # 1. load user image
    img = Image.open(input_path).convert("RGB")

    # 2. remove background
    no_bg = remove(img).convert("RGBA")

    import numpy as np

    r, g, b, a = no_bg.split()

    alpha = np.array(a)

    height = alpha.shape[0]
    fade_height = 2000  # bottom feather strength

    for i in range(fade_height):
      fade_factor = (1 - (i / fade_height)) ** 1.5
      alpha[height - fade_height + i, :] = (
           alpha[height - fade_height + i, :] * fade_factor
      )

    a = Image.fromarray(alpha)

    no_bg.putalpha(a)

    # 4. load template
    template = Image.open(TEMPLATE_PATH).convert("RGBA")

    # -------------------------
    # 5. PLACE IMAGE (LEFT MIDDLE)
    # -------------------------
    no_bg = no_bg.resize((450, 450))

    img_x = 2
    img_y = int(template.height / 2 - 0)

    template.paste(no_bg, (img_x, img_y), no_bg)

    # -------------------------
    # 6. ADD BANGAL TEXT
    # -------------------------
    draw = ImageDraw.Draw(template)

    try:
        font_name = ImageFont.truetype(FONT_PATH, 60)
        font_des = ImageFont.truetype(FONT_PATH, 40)
    except:
        # fallback if font not found
        font_name = ImageFont.load_default()
        font_des = ImageFont.load_default()

    # LEFT TEXT FUNCTION
    def left_text(text, font, y, x=40, fill=(255, 255, 255)):
      draw.text((x, y), text, font=font, fill=fill)

# LEFT POSITION
    text_x = 40

# NAME
    left_text(
      name,
      font_name,
      template.height - 120,
      x=text_x
    )

# DESIGNATION
    left_text(
      designation,
      font_des,
      template.height - 60,
      x=text_x
    )

    # -------------------------
    # 7. SAVE OUTPUT
    # -------------------------
    output_name = str(uuid.uuid4()) + ".png"
    output_path = os.path.join(OUTPUT_FOLDER, output_name)

    template.save(output_path)

    return output_path


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["photo"]
    name = request.form["name"]
    designation = request.form["designation"]

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, file_id + ".jpg")

    file.save(input_path)

    output_path = process_image(input_path, name, designation)

    return send_file(output_path, as_attachment=True)


# -------------------------
# RUN SERVER
# -------------------------
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
