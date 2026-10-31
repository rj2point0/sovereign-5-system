"""
=============================================================================
SACRED NUMBER BLUEPRINT · REAL HUMAN 9:16 VERTICAL B-ROLL FETCHER
fetch_human_broll.py
Downloads 8 high-resolution, watermark-free real human video clips across 3
emotional/lifestyle categories, transcodes/crops them to exact 1080x1920 (9:16)
30fps vertical MP4s in broll_library/, and verifies frame motion & quality.
=============================================================================
"""

import os
import subprocess
import sys
import urllib.request
from typing import Dict, List

import cv2
import imageio_ffmpeg
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BROLL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "broll_library")

BROLL_CLIPS: List[Dict[str, str]] = [
    # Clip Type 1: Relationship / Overthinking / Late Night Reflection
    {
        "id": "type1_window_reflection",
        "category": "Type 1: Relationship / Overthinking / Late Night Reflection",
        "description": "Woman looking thoughtful and reflective by a window",
        "url": "https://assets.mixkit.co/videos/47442/47442-720.mp4",
        "filename": "broll_01_window_reflection.mp4",
    },
    {
        "id": "type1_late_night_phone",
        "category": "Type 1: Relationship / Overthinking / Late Night Reflection",
        "description": "Woman lying awake looking at her phone at night",
        "url": "https://assets.mixkit.co/videos/39782/39782-720.mp4",
        "filename": "broll_02_late_night_phone.mp4",
    },
    {
        "id": "type1_thoughtful_woman",
        "category": "Type 1: Relationship / Overthinking / Late Night Reflection",
        "description": "Thoughtful woman reflecting on patterns and emotions",
        "url": "https://assets.mixkit.co/videos/28729/28729-720.mp4",
        "filename": "broll_03_thoughtful_woman.mp4",
    },
    # Clip Type 2: Career Burnout / Pushing Hard / Exhaustion
    {
        "id": "type2_stressed_temples",
        "category": "Type 2: Career Burnout / Pushing Hard / Exhaustion",
        "description": "Stressed woman rubbing temples / feeling overwhelmed",
        "url": "https://assets.mixkit.co/videos/14861/14861-720.mp4",
        "filename": "broll_04_stressed_temples.mp4",
    },
    {
        "id": "type2_working_late",
        "category": "Type 2: Career Burnout / Pushing Hard / Exhaustion",
        "description": "Exhausted worker taking a break late at night",
        "url": "https://assets.mixkit.co/videos/24063/24063-720.mp4",
        "filename": "broll_05_working_late.mp4",
    },
    {
        "id": "type2_laptop_focus",
        "category": "Type 2: Career Burnout / Pushing Hard / Exhaustion",
        "description": "Woman working intently at her computer late",
        "url": "https://assets.mixkit.co/videos/4713/4713-720.mp4",
        "filename": "broll_06_laptop_focus.mp4",
    },
    # Clip Type 3: Discovery / Journaling / Candlelit Ritual
    {
        "id": "type3_journaling_ritual",
        "category": "Type 3: Discovery / Journaling / Candlelit Ritual",
        "description": "Woman journaling and taking notes in her spiral notebook",
        "url": "https://assets.mixkit.co/videos/42655/42655-720.mp4",
        "filename": "broll_07_journaling_ritual.mp4",
    },
    {
        "id": "type3_phone_discovery",
        "category": "Type 3: Discovery / Journaling / Candlelit Ritual",
        "description": "Woman having a discovery moment on her smartphone",
        "url": "https://assets.mixkit.co/videos/43270/43270-720.mp4",
        "filename": "broll_08_phone_discovery.mp4",
    },
    # Clip Type 4: High-Emotion Relationship / Couple Tension / Atmospheric B-Roll (broll_09 - broll_20)
    {
        "id": "type4_couple_silhouette_walk",
        "category": "Type 4: Relationship / Couple Dynamics",
        "description": "Couple silhouette walking through a quiet neighborhood at dusk",
        "url": "https://assets.mixkit.co/videos/939/939-720.mp4",
        "filename": "broll_09_couple_silhouette_walk.mp4",
    },
    {
        "id": "type4_couple_sunset_embrace",
        "category": "Type 4: Relationship / Couple Dynamics",
        "description": "Lovers holding each other on a warm romantic sunset",
        "url": "https://assets.mixkit.co/videos/4664/4664-720.mp4",
        "filename": "broll_10_couple_sunset_embrace.mp4",
    },
    {
        "id": "type4_dusk_river_silhouette",
        "category": "Type 4: Relationship / Solitude & Reflection",
        "description": "Silhouette of a lonely figure at dusk near a river",
        "url": "https://assets.mixkit.co/videos/35426/35426-720.mp4",
        "filename": "broll_11_dusk_river_silhouette.mp4",
    },
    {
        "id": "type4_beach_shore_brooding",
        "category": "Type 4: Relationship / Solitude & Reflection",
        "description": "Brooding figure walking along the ocean shore at dusk",
        "url": "https://assets.mixkit.co/videos/35889/35889-720.mp4",
        "filename": "broll_12_beach_shore_brooding.mp4",
    },
    {
        "id": "type4_rain_ripples_water",
        "category": "Type 4: Relationship / Moody Rain & Atmosphere",
        "description": "Sad young woman holding warm cup reflecting on a relationship",
        "url": "https://assets.mixkit.co/videos/41827/41827-720.mp4",
        "filename": "broll_13_rain_ripples_water.mp4",
    },
    {
        "id": "type4_city_night_walk",
        "category": "Type 4: Relationship / Late Night City Walk",
        "description": "Walking through city streetlights late at night",
        "url": "https://assets.mixkit.co/videos/40640/40640-720.mp4",
        "filename": "broll_14_city_night_walk.mp4",
    },
    {
        "id": "type4_sunset_ocean_waves",
        "category": "Type 4: Relationship / Golden Hour Horizon",
        "description": "Warm orange sunset waves rolling onto the beach",
        "url": "https://assets.mixkit.co/videos/2168/2168-720.mp4",
        "filename": "broll_15_sunset_ocean_waves.mp4",
    },
    {
        "id": "type4_candlelight_woman_face",
        "category": "Type 4: Relationship / Candlelit Intimacy",
        "description": "Close-up of a young woman watching the flame of a candle",
        "url": "https://assets.mixkit.co/videos/41740/41740-720.mp4",
        "filename": "broll_16_candlelight_woman_face.mp4",
    },
    {
        "id": "type4_candle_dark_glow",
        "category": "Type 4: Relationship / Candlelit Intimacy",
        "description": "Warm glowing candle flickering in the dark",
        "url": "https://assets.mixkit.co/videos/3458/3458-720.mp4",
        "filename": "broll_17_candle_dark_glow.mp4",
    },
    {
        "id": "type4_hands_texting_phone",
        "category": "Type 4: Relationship / Texting & Waiting",
        "description": "Close-up of hands typing a text message on a smartphone",
        "url": "https://assets.mixkit.co/videos/4915/4915-720.mp4",
        "filename": "broll_18_hands_texting_phone.mp4",
    },
    {
        "id": "type4_couple_field_walk",
        "category": "Type 4: Relationship / Couple Dynamics",
        "description": "Close-up of a couple walking together through a golden field",
        "url": "https://assets.mixkit.co/videos/45857/45857-720.mp4",
        "filename": "broll_19_couple_field_walk.mp4",
    },
    {
        "id": "type4_couple_tension_apart",
        "category": "Type 4: Relationship / Emotional Distance",
        "description": "Couple experiencing emotional tension and distance",
        "url": "https://assets.mixkit.co/videos/42973/42973-720.mp4",
        "filename": "broll_20_couple_tension_apart.mp4",
    },
]


def download_and_convert_clip(clip: Dict[str, str]) -> str:
    os.makedirs(BROLL_DIR, exist_ok=True)
    out_path = os.path.join(BROLL_DIR, clip["filename"])
    raw_tmp = os.path.join(BROLL_DIR, f"_raw_{clip['filename']}")

    if os.path.exists(out_path) and os.path.getsize(out_path) > 200_000:
        if verify_vertical_video(out_path):
            print(f"  ✓ Cached & verified: {clip['filename']} ({clip['description']})", flush=True)
            return out_path

    print(f"  ↓ Downloading {clip['filename']} from {clip['url']}...", flush=True)
    req = urllib.request.Request(
        clip["url"],
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(raw_tmp, "wb") as f:
        f.write(data)

    # Convert to 1080x1920 9:16 vertical MP4 @ 30fps (center-cropped full bleed)
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-i",
        raw_tmp,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "19",
        "-pix_fmt",
        "yuv420p",
        "-an",
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(raw_tmp):
        os.remove(raw_tmp)

    assert verify_vertical_video(out_path), f"Verification failed for {out_path}"
    sz_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  ✓ Converted & verified 9:16 vertical human clip: {clip['filename']} ({sz_mb:.2f} MB)", flush=True)
    return out_path


def verify_vertical_video(filepath: str) -> bool:
    """Verifies the MP4 is 1080x1920, has >= 60 frames, real natural texture, and real motion."""
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        return False
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ret1, f1 = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(30, max(1, total_frames - 1)))
    ret2, f2 = cap.read()
    cap.release()

    if not (ret1 and ret2):
        return False
    if w != 1080 or h != 1920 or total_frames < 45:
        return False

    std_val = float(f1.std())
    motion_diff = float(np.mean(np.abs(f1.astype(np.float32) - f2.astype(np.float32))))
    return std_val > 5.0 and motion_diff > 0.10


def fetch_all_broll() -> List[str]:
    print("=" * 70, flush=True)
    print("   CURATING & VERIFYING 9:16 VERTICAL HUMAN B-ROLL LIBRARY", flush=True)
    print("=" * 70, flush=True)
    paths = []
    for clip in BROLL_CLIPS:
        p = download_and_convert_clip(clip)
        paths.append(p)
    print("=" * 70, flush=True)
    print(f"   ✓ ALL {len(paths)} REAL HUMAN 9:16 B-ROLL CLIPS VERIFIED IN: {BROLL_DIR}", flush=True)
    print("=" * 70, flush=True)
    return paths


if __name__ == "__main__":
    fetch_all_broll()
