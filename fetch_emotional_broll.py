#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · EMOTIONAL RELATIONSHIP FACE & COUPLE B-ROLL FETCHER
fetch_emotional_broll.py
-----------------------------------------------------------------------------
Downloads and curates 12 distinct, high-resolution vertical (1080x1920) video
clips featuring real, expressive human faces & relationship tension.
Frames each clip so:
  1. Both partners' faces (or the close-up expressive face) fit cleanly inside
     the 1080px width without cutting faces in half on the left/right edges.
  2. Subjects' faces sit cleanly in the middle/lower-middle third (Y = 650..1620)
     so the Giant 120px Headline (Y = 250..660) never covers their eyes!
  3. Enforces warm/cinematic lighting (`mean_luma >= 65.0`).
=============================================================================
"""

import os
import subprocess
import sys
import urllib.request
from typing import Any, Dict, List

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BROLL_DIR = os.path.join(BASE_DIR, "broll_library")
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

EMOTIONAL_CLIPS: List[Dict[str, Any]] = [
    {
        "id": "emo_01_woman_phone_night",
        "filename": "emo_01_woman_phone_night.mp4",
        "url": "https://assets.mixkit.co/videos/39789/39789-720.mp4",
        "description": "Woman lying awake staring anxiously at her phone before sleeping",
        "scale_w": 2250,
        "x_bias": 0.88,
        "y_offset": 460,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_02_couple_bed_backs",
        "filename": "emo_02_couple_bed_backs.mp4",
        "url": "https://assets.mixkit.co/videos/46094/46094-720.mp4",
        "description": "Couple sitting on opposite sides of the bed in tense silence",
        "scale_w": 2050,
        "x_bias": 0.50,
        "y_offset": 480,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_03_couple_silence_apart",
        "filename": "emo_03_couple_silence_apart.mp4",
        "url": "https://assets.mixkit.co/videos/48038/48038-720.mp4",
        "description": "Young couple sitting back-to-back in cold emotional silence",
        "scale_w": 2100,
        "x_bias": 0.50,
        "y_offset": 480,
        "lift_brightness": 0.06,
    },
    {
        "id": "emo_04_guy_apologizing_upset_gf",
        "filename": "emo_04_guy_apologizing_upset_gf.mp4",
        "url": "https://assets.mixkit.co/videos/4715/4715-720.mp4",
        "description": "Man pulling away / trying to talk to his hurt upset girlfriend",
        "scale_w": 2150,
        "x_bias": 0.45,
        "y_offset": 460,
        "lift_brightness": 0.04,
    },
    {
        "id": "emo_05_couple_upset_disappointed",
        "filename": "emo_05_couple_upset_disappointed.mp4",
        "url": "https://assets.mixkit.co/videos/4731/4731-720.mp4",
        "description": "Hurt woman sitting upset and emotionally distant from partner",
        "scale_w": 2200,
        "x_bias": 0.52,
        "y_offset": 460,
        "lift_brightness": 0.04,
    },
    {
        "id": "emo_06_sofa_back_to_back",
        "filename": "emo_06_sofa_back_to_back.mp4",
        "url": "https://assets.mixkit.co/videos/4574/4574-720.mp4",
        "description": "Couple sitting on sofa with backs turned in cold silence",
        "scale_w": 2150,
        "x_bias": 0.52,
        "y_offset": 460,
        "lift_brightness": 0.24,
    },
    {
        "id": "emo_07_upset_after_argument",
        "filename": "emo_07_upset_after_argument.mp4",
        "url": "https://assets.mixkit.co/videos/4714/4714-720.mp4",
        "description": "Man and woman looking hurt and conflicted after an argument",
        "scale_w": 1950,
        "x_bias": 0.50,
        "y_offset": 480,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_08_couple_bedroom_tension",
        "filename": "emo_08_couple_bedroom_tension.mp4",
        "url": "https://assets.mixkit.co/videos/45555/45555-720.mp4",
        "description": "Couple sitting with backs turned in bedroom tension",
        "scale_w": 2050,
        "x_bias": 0.50,
        "y_offset": 480,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_09_couple_forgiveness_hug",
        "filename": "emo_09_couple_forgiveness_hug.mp4",
        "url": "https://assets.mixkit.co/videos/46095/46095-720.mp4",
        "description": "Intense emotional couple embrace after relationship conflict",
        "scale_w": 2250,
        "x_bias": 0.55,
        "y_offset": 460,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_10_loving_couple_close",
        "filename": "emo_10_loving_couple_close.mp4",
        "url": "https://assets.mixkit.co/videos/42255/42255-720.mp4",
        "description": "Intimate close-up of couple holding each other in bed",
        "scale_w": 2400,
        "x_bias": 0.50,
        "y_offset": 440,
        "lift_brightness": 0.0,
    },
    {
        "id": "emo_11_worried_sad_woman_closeup",
        "filename": "emo_11_worried_sad_woman_closeup.mp4",
        "url": "https://assets.mixkit.co/videos/8739/8739-720.mp4",
        "description": "Expressive close-up of worried sad woman in deep thought",
        "scale_w": 2400,
        "x_bias": 0.48,
        "y_offset": 440,
        "lift_brightness": 0.04,
    },
    {
        "id": "emo_12_upset_couple_closeup",
        "filename": "emo_12_upset_couple_closeup.mp4",
        "url": "https://assets.mixkit.co/videos/42979/42979-720.mp4",
        "description": "Emotional tension between man and woman in bedroom",
        "scale_w": 1950,
        "x_bias": 0.50,
        "y_offset": 480,
        "lift_brightness": 0.18,
        "start_frame": 12,
    },
]


def render_feathered_vertical_clip(
    raw_path: str,
    out_path: str,
    scale_w: int,
    x_bias: float,
    y_offset: int,
    lift: float,
    start_frame: int = 0,
):
    """
    Renders a 1080x1920 30fps vertical clip where the subject(s) are framed cleanly
    in the middle/lower-middle third (so the Giant 120px Headline at Y=250..660 never
    covers their eyes) with a seamless soft-blurred vertical extension top & bottom.
    """
    cap = cv2.VideoCapture(raw_path)
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    fps = 30
    max_frames = 180  # 6 seconds @ 30fps

    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        "1080x1920",
        "-pix_fmt",
        "bgr24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-an",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    scale_h = int(round(scale_w * 720.0 / 1280.0))
    # Build smooth vertical alpha mask (scale_h x 1080) with 180px feather top & bottom
    alpha = np.ones((scale_h, 1080, 1), dtype=np.float32)
    feather = 180
    ramp = np.linspace(0.0, 1.0, feather, dtype=np.float32).reshape((feather, 1, 1))
    alpha[:feather, :, :] = ramp
    alpha[-feather:, :, :] = ramp[::-1, :, :]

    frames_written = 0
    while frames_written < max_frames:
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret or frame is None:
                break

        if lift > 0.0:
            frame_f = frame.astype(np.float32) / 255.0
            frame_f = np.clip((frame_f ** 0.82) * 1.08 + lift, 0.0, 1.0)
            frame = (frame_f * 255.0).astype(np.uint8)

        # 1. Full-bleed blurred background (1080x1920) via fast 8x downscale-blur-upscale
        bg_small = cv2.resize(frame, (426, 240), interpolation=cv2.INTER_LINEAR)
        bg_sx0 = max(0, min(426 - 135, int((426 - 135) * x_bias)))
        bg_scrop = bg_small[:, bg_sx0 : bg_sx0 + 135]
        bg_sblur = cv2.GaussianBlur(bg_scrop, (9, 9), 4.0)
        bg_blur = cv2.resize(bg_sblur, (1080, 1920), interpolation=cv2.INTER_LINEAR)
        canvas = bg_blur.astype(np.float32)

        # 2. Sharp foreground subject framed at y_offset .. y_offset + scale_h
        fg_scaled = cv2.resize(frame, (scale_w, scale_h), interpolation=cv2.INTER_AREA)
        fg_x0 = max(0, min(scale_w - 1080, int((scale_w - 1080) * x_bias)))
        fg_crop = fg_scaled[:, fg_x0 : fg_x0 + 1080].astype(np.float32)

        y0 = max(0, min(1920 - scale_h, y_offset))
        y1 = y0 + scale_h
        region = canvas[y0:y1, :, :]
        canvas[y0:y1, :, :] = region * (1.0 - alpha) + fg_crop * alpha

        out_bgr = np.clip(canvas, 0, 255).astype(np.uint8)
        proc.stdin.write(out_bgr.tobytes())
        frames_written += 1

    cap.release()
    proc.stdin.close()
    proc.wait()


def download_and_prepare_emotional_clip(clip: Dict[str, Any], force_rebuild: bool = True) -> Dict[str, Any]:
    os.makedirs(BROLL_DIR, exist_ok=True)
    out_path = os.path.join(BROLL_DIR, clip["filename"])
    raw_tmp = os.path.join(BROLL_DIR, f"_raw_{clip['filename']}")

    if force_rebuild or not os.path.exists(out_path) or os.path.getsize(out_path) < 150_000:
        if not os.path.exists(raw_tmp):
            print(f"  ↓ Downloading {clip['filename']} ({clip['description']})...", flush=True)
            req = urllib.request.Request(
                clip["url"],
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = resp.read()
            with open(raw_tmp, "wb") as f:
                f.write(data)

        render_feathered_vertical_clip(
            raw_tmp,
            out_path,
            scale_w=int(clip.get("scale_w", 2100)),
            x_bias=float(clip.get("x_bias", 0.50)),
            y_offset=int(clip.get("y_offset", 460)),
            lift=float(clip.get("lift_brightness", 0.0)),
            start_frame=int(clip.get("start_frame", 0)),
        )
        if os.path.exists(raw_tmp):
            os.remove(raw_tmp)

    cap = cv2.VideoCapture(out_path)
    ret, f0 = cap.read()
    cap.release()
    luma = float(cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY).mean()) if ret and f0 is not None else 0.0
    assert luma >= 65.0, f"Brightness gate failed for {clip['filename']}: {luma:.1f} < 65.0"
    print(f"  ✓ Verified {clip['filename']} | mean_luma={luma:.1f} (>=65) | {clip['description']}", flush=True)
    return {"filename": clip["filename"], "path": out_path, "mean_luma": round(luma, 1), "description": clip["description"]}


def build_contact_sheet(results: List[Dict[str, Any]]):
    cols, rows = 4, 3
    thumb_w, thumb_h = 270, 480
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (15, 15, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    for idx, r in enumerate(results[:12]):
        cap = cv2.VideoCapture(r["path"])
        cap.set(cv2.CAP_PROP_POS_FRAMES, 10)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        cx = (idx % cols) * thumb_w
        cy = (idx // cols) * thumb_h
        sheet.paste(pil_img, (cx, cy))
        draw.rectangle([cx, cy + thumb_h - 36, cx + thumb_w, cy + thumb_h], fill=(0, 0, 0))
        draw.text((cx + 8, cy + thumb_h - 30), f"{r['filename'][:22]} (L={r['mean_luma']})", fill=(255, 225, 77), font=font)

    out_sheet = os.path.join(BASE_DIR, "emotional_broll_contact_sheet.jpg")
    sheet.save(out_sheet, quality=90)
    print(f"✓ Saved contact sheet -> {out_sheet}", flush=True)


def main():
    results = []
    for idx, clip in enumerate(EMOTIONAL_CLIPS):
        res = download_and_prepare_emotional_clip(clip, force_rebuild=(idx == 11))
        results.append(res)
    build_contact_sheet(results)


if __name__ == "__main__":
    main()
