from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

CREAM = (242, 242, 236)
INK = (16, 17, 16)
MID = (88, 94, 86)
SKIN = (190, 162, 143)
ROAD = (204, 207, 199)
GREEN = (116, 132, 92)
WHITE_CAP = (248, 248, 243)


def canvas(w=1200, h=900, bg=CREAM):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def add_grain(im, strength=8):
    overlay = Image.effect_noise(im.size, 18).convert("L")
    overlay = overlay.point(lambda p: int(128 + (p - 128) * strength / 18))
    color = Image.merge("RGB", (overlay, overlay, overlay))
    return Image.blend(im, color, 0.035)


def shadow(draw, box, fill=(0, 0, 0, 38), blur=18, base=None):
    if base is None:
        return
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_cap(draw, x, y, scale=1.0, color=INK, brim=True):
    w = int(250 * scale)
    h = int(118 * scale)
    draw.pieslice((x, y, x + w, y + h * 2), 180, 360, fill=color)
    draw.arc((x + 16 * scale, y + 8 * scale, x + w - 10 * scale, y + h * 1.9), 185, 355, fill=(55, 58, 55), width=max(2, int(4 * scale)))
    if brim:
        draw.rounded_rectangle((x - 75 * scale, y + 78 * scale, x + 92 * scale, y + 124 * scale), radius=int(24 * scale), fill=color)
        draw.arc((x - 65 * scale, y + 84 * scale, x + 92 * scale, y + 140 * scale), 180, 350, fill=(54, 56, 53), width=max(1, int(3 * scale)))
    for i in range(5):
        px = x + w * 0.58 + i * 19 * scale
        draw.line((px, y + 24 * scale, px + 16 * scale, y + h * 1.16), fill=(46, 49, 46), width=max(1, int(3 * scale)))


def text(draw, xy, value, size=30, fill=INK):
    # Default bitmap font keeps the generator dependency-light; visual page uses HTML text.
    draw.text(xy, value, fill=fill)


def wearing_hero():
    im, draw = canvas(1200, 900, (232, 234, 226))
    # background running path
    draw.polygon([(0, 760), (1200, 650), (1200, 900), (0, 900)], fill=(194, 198, 188))
    draw.polygon([(720, 640), (1200, 610), (1200, 690), (730, 720)], fill=(221, 222, 216))
    draw.rectangle((0, 0, 1200, 250), fill=(218, 225, 214))
    # person
    draw.ellipse((472, 210, 728, 466), fill=SKIN)
    draw.rounded_rectangle((420, 455, 780, 920), radius=130, fill=(48, 55, 52))
    draw.polygon([(510, 476), (600, 560), (690, 476)], fill=(226, 214, 201))
    draw_cap(draw, 442, 176, 1.26, INK)
    draw.rounded_rectangle((792, 530, 1070, 610), radius=38, fill=(48, 55, 52))
    draw.rounded_rectangle((168, 545, 428, 620), radius=38, fill=(48, 55, 52))
    return add_grain(im)


def detail_feature():
    im, draw = canvas(1200, 760, (229, 229, 223))
    draw.rounded_rectangle((110, 130, 1090, 610), radius=36, fill=(26, 28, 27))
    # mesh panel
    for row in range(10):
        for col in range(28):
            cx = 210 + col * 30 + (row % 2) * 14
            cy = 195 + row * 34
            draw.ellipse((cx, cy, cx + 16, cy + 22), fill=(78, 84, 78))
    draw.rounded_rectangle((100, 520, 1100, 610), radius=32, fill=(43, 45, 42))
    for x in range(170, 1040, 36):
        draw.line((x, 540, x + 22, 588), fill=(112, 118, 111), width=3)
    draw.line((130, 500, 1070, 500), fill=(130, 133, 125), width=4)
    return add_grain(im)


def product_solo():
    im, draw = canvas(1200, 900, (239, 239, 234))
    rgba = im.convert("RGBA")
    shadow(ImageDraw.Draw(rgba), (255, 650, 980, 780), base=rgba)
    im = rgba.convert("RGB")
    draw = ImageDraw.Draw(im)
    draw_cap(draw, 395, 285, 2.0, INK)
    draw.rounded_rectangle((690, 520, 940, 590), radius=35, fill=(24, 25, 24))
    for i in range(10):
        draw.ellipse((730 + i * 18, 545, 738 + i * 18, 553), fill=(91, 96, 90))
    return add_grain(im)


def wearing_run():
    im, draw = canvas(1200, 820, (235, 236, 228))
    draw.rectangle((0, 0, 1200, 290), fill=(210, 222, 210))
    draw.polygon([(0, 660), (1200, 560), (1200, 820), (0, 820)], fill=ROAD)
    draw.line((0, 700, 1200, 600), fill=(236, 236, 229), width=8)
    draw.ellipse((490, 180, 690, 380), fill=SKIN)
    draw_cap(draw, 430, 150, 1.0, INK)
    draw.polygon([(520, 380), (760, 780), (360, 780)], fill=(42, 48, 46))
    draw.line((495, 455, 220, 620), fill=(42, 48, 46), width=58)
    draw.line((650, 460, 920, 590), fill=(42, 48, 46), width=58)
    return add_grain(im)


def strap_detail():
    im, draw = canvas(1200, 760, (231, 231, 225))
    draw.rounded_rectangle((190, 150, 1010, 560), radius=80, fill=INK)
    draw.rectangle((360, 400, 840, 530), fill=(33, 35, 33))
    draw.rounded_rectangle((450, 430, 750, 505), radius=34, fill=(60, 62, 58))
    draw.rounded_rectangle((760, 420, 890, 520), radius=24, outline=(120, 124, 116), width=14)
    for x in range(480, 735, 40):
        draw.ellipse((x, 455, x + 15, 470), fill=(132, 137, 129))
    draw.arc((210, 120, 990, 700), 205, 335, fill=(78, 81, 76), width=5)
    return add_grain(im)


def color_option():
    im, draw = canvas(1200, 760, (239, 239, 234))
    draw.rectangle((0, 0, 600, 760), fill=(235, 235, 229))
    draw.rectangle((600, 0, 1200, 760), fill=(226, 228, 224))
    draw_cap(draw, 205, 260, 1.32, INK)
    draw_cap(draw, 805, 260, 1.32, WHITE_CAP)
    draw.line((600, 90, 600, 670), fill=(200, 202, 196), width=3)
    draw.text((260, 650), "BLACK", fill=INK)
    draw.text((865, 650), "WHITE", fill=INK)
    return add_grain(im)


def lifestyle():
    im, draw = canvas(1200, 900, (226, 230, 220))
    draw.rectangle((0, 0, 1200, 360), fill=(195, 214, 190))
    draw.rectangle((0, 650, 1200, 900), fill=(188, 190, 181))
    draw.ellipse((510, 230, 700, 420), fill=SKIN)
    draw_cap(draw, 458, 200, 0.96, WHITE_CAP)
    draw.rounded_rectangle((430, 420, 790, 880), radius=140, fill=(53, 65, 58))
    draw.rectangle((100, 610, 1100, 660), fill=(214, 215, 208))
    for x in (145, 275, 905, 1030):
        draw.rectangle((x, 330, x + 40, 650), fill=(130, 143, 122))
    return add_grain(im)


assets = {
    "runnerwin-running-cap-01-wearing-hero.png": wearing_hero(),
    "runnerwin-running-cap-02-detail-feature.png": detail_feature(),
    "runnerwin-running-cap-03-product-solo.png": product_solo(),
    "runnerwin-running-cap-04-wearing-run.png": wearing_run(),
    "runnerwin-running-cap-05-strap-detail.png": strap_detail(),
    "runnerwin-running-cap-06-color-option.png": color_option(),
    "runnerwin-running-cap-07-wearing-lifestyle.png": lifestyle(),
}

for name, image in assets.items():
    image.save(OUT / name, quality=94)

