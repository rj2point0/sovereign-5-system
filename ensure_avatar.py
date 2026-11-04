#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sacred_avatar_512.png")

def build_avatar():
    if os.path.exists(OUT_PATH):
        return OUT_PATH
    size = 512
    img = Image.new("RGBA", (size, size), (10, 8, 18, 255))
    draw = ImageDraw.Draw(img)
    # Outer gold ring
    draw.ellipse((16, 16, size - 16, size - 16), outline=(212, 175, 55, 255), width=10)
    draw.ellipse((34, 34, size - 34, size - 34), outline=(255, 92, 138, 220), width=4)
    # Sacred geometry diamond
    cx, cy = size // 2, size // 2
    r = 175
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=(212, 175, 55, 180), width=4)
    try:
        f_big = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 140)
        f_sub = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
    except Exception:
        f_big = ImageFont.load_default()
        f_sub = ImageFont.load_default()
    draw.text((cx, cy - 28), "19×23", fill=(255, 240, 200, 255), font=f_big, anchor="mm")
    draw.text((cx, cy + 88), "96% MATCH", fill=(255, 92, 138, 255), font=f_sub, anchor="mm")
    img.save(OUT_PATH, "PNG")
    return OUT_PATH

if __name__ == "__main__":
    print("Saved avatar:", build_avatar())
