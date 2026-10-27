"""
=============================================================================
SACRED NUMBER BLUEPRINT · COHORT B & COHORT C HUMAN B-ROLL VIDEO GENERATOR
generate_broll_story_tiktoks.py
-----------------------------------------------------------------------------
Supports two high-converting formats:
- Cohort B (38–47s Story + Product Reveal):
  0–15s Human B-roll -> 15s–End Calculator + Dossier Reveal + Final 5s CTA pill.
- Cohort C (12–14s Hyper-Specific Birthday Shorts for 80%+ Completion Rate):
  0.0–4.0s: Moving Human B-roll Clip A + Native TikTok White Hook Box (0–4.5s)
  4.0–7.5s: Moving Human B-roll Clip B + Dynamic CapCut Center Captions
  7.5s–End: Fast Zoom Reveal of Dossier Mandala / Lo Shu Grid / 15-Point Ledger
            + Closing CTA Pill in the final 3.5 seconds (0.5s tail hold, <14.5s).
=============================================================================
"""

import argparse
import asyncio
import io
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import edge_tts
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BROLL_DIR = os.path.join(BASE_DIR, "broll_library")
SCENES_DIR = os.path.join(BASE_DIR, "scenes_cache")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
ARTIFACTS_DIR = r"C:\Users\User\.gemini\antigravity\brain\5be548e1-0bfd-4f21-b5d4-67c12098b05e"

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SEMI = r"C:\Windows\Fonts\seguisb.ttf"
if not os.path.exists(FONT_SEMI):
    FONT_SEMI = FONT_BOLD

POWER_WORDS = {
    "exhausting", "relationship", "patterns", "dynamics", "western", "millions",
    "birthday", "ignores", "grid", "vibration", "five", "ancient", "systems",
    "chinese", "lo", "shu", "missing", "six", "fifteen", "three", "overlap",
    "numbers", "repeating", "love", "wealth", "wall", "calculator", "profile",
    "twice", "hard", "stuck", "lazy", "52-day", "cycle", "cycles", "rosicrucian",
    "planetary", "second", "engine", "saturn", "preservation", "eight", "burnout",
    "stopped", "window", "today", "name",
    # Cohort C power words
    "eighth", "seventeenth", "twenty-sixth", "finances", "nothing", "conflict",
    "frequency", "fighting", "five-system", "seventh", "sixteenth", "twenty-fifth",
    "connection", "disappear", "seven", "clash", "vedic", "collides", "book",
    "breakthrough", "agree", "fight", "first", "tenth", "nineteenth", "twenty-eighth",
    "fourth", "thirteenth", "twenty-second", "thirty-first", "second", "eleventh",
    "twentieth", "twenty-ninth", "third", "twelfth", "twenty-first", "thirtieth",
    "fifth", "fourteenth", "twenty-third", "sixth", "fifteenth", "twenty-fourth",
    "ninth", "eighteenth", "twenty-seventh", "hundred", "brilliant", "jupiter",
    "routine", "mercury", "healing", "venus", "mars",
}

COHORT_B_SPECS: List[Dict[str, Any]] = [
    {
        "id": "broll_01",
        "cohort": "Cohort B",
        "format_type": "cohort_b_story",
        "filename": "tiktok_broll_01_relationship_patterns.mp4",
        "hook_box_text": "Why you keep attracting the exact same exhausting relationship patterns",
        "voice": "en-US-AvaNeural",
        "rate": "+10%",
        "spoken_script": (
            "If you keep attracting the exact same exhausting relationship dynamics, stop looking at your "
            "Western Life Path number. Millions of people born on your birthday get that exact same reading, "
            "and it completely ignores your relationship grid. When I ran my birth date and the sound vibration "
            "of my full name through all five ancient numerology systems at once, it showed me the Chinese Lo Shu "
            "grid—and I realized I was completely missing the numbers five and six. Even crazier, out of fifteen "
            "calculations across all five cultures, three specific overlap numbers kept repeating. Those three "
            "numbers explained how I love, how I build wealth, and why I kept hitting the same wall. I linked "
            "the five-system calculator on my profile—go type in your name and birthday to see your three overlap "
            "numbers and which numbers are missing from your grid."
        ),
        "broll_clips": [
            (0.0, 5.0, "broll_01_window_reflection.mp4"),
            (5.0, 10.0, "broll_02_late_night_phone.mp4"),
            (10.0, 15.0, "broll_07_journaling_ritual.mp4"),
        ],
        "product_scenes": [
            ("video_calc", "tiktok_promo_1.mp4", 0.0, 4.5),
            ("image", "scenes_cache/scene_loshu.png", 7.5),
            ("image", "scenes_cache/scene_mandala.png", 7.0),
            ("image", "scenes_cache/scene_anchors.png", 99.0),
        ],
        "tiktok_caption": (
            "Why you keep attracting the exact same exhausting relationship patterns (and what the missing "
            "numbers in your Chinese Lo Shu grid reveal) 💔✨ #numerology #relationships #loshugrid "
            "#spiritualawakening #datingadvice #karmicrelationships #lifepath #chaldean #healingjourney"
        ),
        "first_comment": "Which numbers from 1 to 9 are missing from your birthday—and have you noticed that same pattern in relationships? 👇",
        "hashtags": [
            "#numerology", "#relationships", "#loshugrid", "#spiritualawakening",
            "#datingadvice", "#karmicrelationships", "#lifepath", "#chaldean", "#healingjourney"
        ],
    },
    {
        "id": "broll_02",
        "cohort": "Cohort B",
        "format_type": "cohort_b_story",
        "filename": "tiktok_broll_02_career_burnout_timing.mp4",
        "hook_box_text": "Working twice as hard this month but feeling completely stuck? Read this.",
        "voice": "en-US-AvaNeural",
        "rate": "+10%",
        "spoken_script": (
            "If you've been working twice as hard this month but feel like you're fighting an invisible wall, "
            "you are not lazy—you're probably pushing during the wrong 52-day cycle. Most people only know their "
            "Western Life Path number, which treats the entire year like a flat line. When I ran my name and birth "
            "date through the five-system calculator, it mapped my Rosicrucian 52-day planetary cycles and unlocked "
            "my second overlap number—my Wealth Engine. I realized I was trying to force major financial moves in "
            "the middle of a Saturn preservation window, while completely ignoring my number eight wealth channel. "
            "The moment I aligned my schedule with my active 52-day window and my three overlap numbers, the "
            "burnout stopped. I linked the five-system calculator on my profile—go enter your name and birthday "
            "to see which 52-day cycle you're in today."
        ),
        "broll_clips": [
            (0.0, 5.0, "broll_04_stressed_temples.mp4"),
            (5.0, 10.0, "broll_05_working_late.mp4"),
            (10.0, 15.0, "broll_08_phone_discovery.mp4"),
        ],
        "product_scenes": [
            ("video_calc", "tiktok_promo_1.mp4", 0.0, 4.5),
            ("image", "scenes_cache/scene_cycles.png", 7.5),
            ("image", "scenes_cache/scene_mandala.png", 7.0),
            ("image", "scenes_cache/scene_somatic.png", 99.0),
        ],
        "tiktok_caption": (
            "Working twice as hard this month but feeling completely stuck? You might be pushing during the "
            "wrong 52-day planetary cycle ⏳⚡ #burnout #wealthtiming #numerology #biorhythm #rosicrucian "
            "#lifepath8 #entrepreneurmindset #spiritualgrowth #nervoussystem"
        ),
        "first_comment": "Which 52-day planetary cycle are you in right now—and what is your Life Path number? Drop your birth month and day below 👇",
        "hashtags": [
            "#burnout", "#wealthtiming", "#numerology", "#biorhythm", "#rosicrucian",
            "#lifepath8", "#entrepreneurmindset", "#spiritualgrowth", "#nervoussystem"
        ],
    },
]

COHORT_C_SPECS: List[Dict[str, Any]] = [
    {
        "id": "short_01",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_01_born_8_17_26.mp4",
        "hook_box_text": "Born on the 8th, 17th, or 26th of any month? (Or a Life Path 8?)",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the eighth, seventeenth, or twenty-sixth, your finances probably feel all or nothing. "
            "That’s not bad luck—it’s a conflict between your birth number and your name frequency. "
            "Check the five-system calculator on my profile to see where your numbers are fighting."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_04_stressed_temples.mp4"),
            (4.0, 7.5, "broll_05_working_late.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_mandala.png", 2.8),
            ("image", "scenes_cache/scene_ledger.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 8th, 17th, or 26th of any month? Why your finances feel all-or-nothing "
            "(and where your birth number & name frequency clash) ⚡👁️ #numerology #lifepath8 "
            "#bornonthe8th #chaldean #wealthtiming #spiritualawakening #manifestation #astrology"
        ),
        "first_comment": "Were you born on the 8th, 17th, or 26th—or is 8 your Life Path number? Drop your birthday month and day below 👇",
        "hashtags": [
            "#numerology", "#lifepath8", "#bornonthe8th", "#chaldean",
            "#wealthtiming", "#spiritualawakening", "#manifestation", "#astrology"
        ],
    },
    {
        "id": "short_02",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_02_born_7_16_25.mp4",
        "hook_box_text": "Born on the 7th, 16th, or 25th? Why standard numerology gets you wrong:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 13.0,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the seventh, sixteenth, or twenty-fifth and feel pulled between deep connection "
            "and wanting to disappear, it’s not a seven problem. It’s a clash between your Vedic number and your "
            "Chinese Lo Shu grid. Run all five systems in my bio to see where your chart collides."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_01_window_reflection.mp4"),
            (4.0, 7.5, "broll_07_journaling_ritual.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_loshu.png", 3.0),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 7th, 16th, or 25th? It’s not a '7 problem'—it’s a clash between your Vedic lens "
            "and your Chinese Lo Shu grid 🔮✨ #numerology #lifepath7 #loshugrid #vedicnumerology "
            "#overthinking #relationships #spiritualtiktok #introvertlife"
        ),
        "first_comment": "Are you a 7th, 16th, or 25th birthday—and do you feel that tug-of-war between connection and solitude? 👇",
        "hashtags": [
            "#numerology", "#lifepath7", "#loshugrid", "#vedicnumerology",
            "#overthinking", "#relationships", "#spiritualtiktok", "#introvertlife"
        ],
    },
    {
        "id": "short_03",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_03_systems_fighting.mp4",
        "hook_box_text": "Why your Life Path number feels like reading 1 page of a 20-page book",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Reading your Life Path number alone is like reading one page of a book. "
            "The real breakthrough happens when you see where all five ancient systems agree—and where they fight "
            "each other in your name and birthday. Try the five-system overlap calculator on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_03_thoughtful_woman.mp4"),
            (4.0, 7.5, "broll_08_phone_discovery.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_mandala.png", 2.8),
            ("image", "scenes_cache/scene_ledger.png", 99.0),
        ],
        "tiktok_caption": (
            "Why reading your Western Life Path number alone feels like reading 1 page of a 20-page book "
            "(see where your 5 systems agree vs. fight) 📖✨ #numerology #lifepath #chaldean #kabbalah "
            "#loshugrid #spiritualawakening #selfdiscovery #sacredgeometry"
        ),
        "first_comment": "Which two numbers feel like they are constantly fighting each other in your personality? Drop your birthday below 👇",
        "hashtags": [
            "#numerology", "#lifepath", "#chaldean", "#kabbalah",
            "#loshugrid", "#spiritualawakening", "#selfdiscovery", "#sacredgeometry"
        ],
    },
    {
        "id": "short_04",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_04_born_1_10_19_28.mp4",
        "hook_box_text": "Born on the 1st, 10th, 19th, or 28th? (The Lone Wolf Leader Paradox)",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the first, tenth, nineteenth, or twenty-eighth, everyone leans on you, "
            "yet you feel completely alone at the top. That’s not a number one curse—it’s a clash between "
            "your Vedic Sun number and your Chaldean name frequency. Check the five-system calculator on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_06_laptop_focus.mp4"),
            (4.0, 7.5, "broll_05_working_late.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_mandala.png", 2.8),
            ("image", "scenes_cache/scene_anchors.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 1st, 10th, 19th, or 28th of any month? Why everyone leans on you yet you feel "
            "like a lone wolf (Vedic Sun vs. Chaldean Name frequency) ☀️🐺 #numerology #lifepath1 "
            "#bornonthe1st #bornonthe19th #chaldean #vedicnumerology #leadership #spiritualtiktok"
        ),
        "first_comment": "Were you born on the 1st, 10th, 19th, or 28th—and do you always end up leading on your own? 👇",
        "hashtags": [
            "#numerology", "#lifepath1", "#bornonthe1st", "#bornonthe19th",
            "#chaldean", "#vedicnumerology", "#leadership", "#spiritualtiktok"
        ],
    },
    {
        "id": "short_05",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_05_born_4_13_22_31.mp4",
        "hook_box_text": "Born on the 4th, 13th, 22nd, or 31st? Why you carry everyone else's weight:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the fourth, thirteenth, twenty-second, or thirty-first, you build the "
            "foundation for everyone else while carrying invisible stress. That’s a friction point between "
            "your Rahu birth number and your missing Lo Shu grid numbers. Try the five-system calculator on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_04_stressed_temples.mp4"),
            (4.0, 7.5, "broll_02_late_night_phone.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_loshu.png", 2.8),
            ("image", "scenes_cache/scene_ledger.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 4th, 13th, 22nd, or 31st? Why you always end up carrying everyone else's weight "
            "(Rahu 4 vs. Chinese Lo Shu Grid) 🏛️⚡ #numerology #lifepath4 #masternumber22 #loshugrid "
            "#vedicnumerology #burnout #spiritualawakening #overachiever"
        ),
        "first_comment": "Are you a 4th, 13th, 22nd, or 31st birthday—and do you feel like the builder everyone relies on? 👇",
        "hashtags": [
            "#numerology", "#lifepath4", "#masternumber22", "#loshugrid",
            "#vedicnumerology", "#burnout", "#spiritualawakening", "#overachiever"
        ],
    },
    {
        "id": "short_06",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_06_born_2_11_20_29.mp4",
        "hook_box_text": "Born on the 2nd, 11th, 20th, or 29th? Why you absorb everyone's energy:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the second, eleventh, twentieth, or twenty-ninth, you sense everyone’s "
            "emotions before they even speak. Standard numerology calls you overly sensitive, but five-system "
            "math shows where your Moon number and Kabbalistic tree collide. Test your chart on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_01_window_reflection.mp4"),
            (4.0, 7.5, "broll_03_thoughtful_woman.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_tree.png", 2.8),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 2nd, 11th, 20th, or 29th? Why you absorb everyone else's emotions before they "
            "even speak (Vedic Moon vs. Kabbalistic Tree of Life) 🌙✨ #numerology #masternumber11 "
            "#lifepath2 #empath #kabbalah #intuition #spiritualtiktok #energyhealing"
        ),
        "first_comment": "Were you born on the 2nd, 11th, 20th, or 29th—and can you read a room before anyone speaks? 👇",
        "hashtags": [
            "#numerology", "#masternumber11", "#lifepath2", "#empath",
            "#kabbalah", "#intuition", "#spiritualtiktok", "#energyhealing"
        ],
    },
    {
        "id": "short_07",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_07_born_3_12_21_30.mp4",
        "hook_box_text": "Born on the 3rd, 12th, 21st, or 30th? Why you have 100 ideas but feel scattered:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the third, twelfth, twenty-first, or thirtieth, your mind generates "
            "a hundred brilliant ideas at once, yet finishing one feels impossible. That’s a clash between "
            "your Vedic Jupiter number and your Chaldean name frequency. Test your chart on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_07_journaling_ritual.mp4"),
            (4.0, 7.5, "broll_06_laptop_focus.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_mandala.png", 2.8),
            ("image", "scenes_cache/scene_anchors.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 3rd, 12th, 21st, or 30th? Why you have 100 brilliant ideas at once but feel "
            "scattered (Vedic Jupiter 3 vs. Chaldean Name frequency) ⚡🧠 #numerology #lifepath3 "
            "#bornonthe3rd #bornonthe21st #creativeburnout #chaldean #vedicnumerology #spiritualtiktok"
        ),
        "first_comment": "Were you born on the 3rd, 12th, 21st, or 30th—and how many unfinished projects do you have open right now? 👇",
        "hashtags": [
            "#numerology", "#lifepath3", "#bornonthe3rd", "#bornonthe21st",
            "#creativeburnout", "#chaldean", "#vedicnumerology", "#spiritualtiktok"
        ],
    },
    {
        "id": "short_08",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_08_born_5_14_23.mp4",
        "hook_box_text": "Born on the 5th, 14th, or 23rd? Why normal 9-to-5 routine drains your spirit:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the fifth, fourteenth, or twenty-third, normal nine-to-five routine slowly drains "
            "your spirit, yet chaos exhausts your nervous system. That’s a tug-of-war between your Mercury "
            "birth number and your Chinese Lo Shu center. Run the five-system calculator on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_02_late_night_phone.mp4"),
            (4.0, 7.5, "broll_08_phone_discovery.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_loshu.png", 2.8),
            ("image", "scenes_cache/scene_somatic.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 5th, 14th, or 23rd of any month? Why normal 9-to-5 routine slowly drains your spirit "
            "(Vedic Mercury 5 vs. Chinese Lo Shu Center) 🌪️✨ #numerology #lifepath5 "
            "#bornonthe5th #bornonthe23rd #loshugrid #restlesssoul #spiritualawakening #nervoussystem"
        ),
        "first_comment": "Are you a 5th, 14th, or 23rd birthday—and do you instantly rebel whenever someone tries to box you in? 👇",
        "hashtags": [
            "#numerology", "#lifepath5", "#bornonthe5th", "#bornonthe23rd",
            "#loshugrid", "#restlesssoul", "#spiritualawakening", "#nervoussystem"
        ],
    },
    {
        "id": "short_09",
        "cohort": "Cohort C",
        "format_type": "cohort_c_short",
        "filename": "tiktok_short_09_born_6_15_24_9_18_27.mp4",
        "hook_box_text": "Born on the 6th, 15th, 24th—or 9th, 18th, 27th? Why you carry everyone's emotional weight:",
        "hook_end_sec": 4.5,
        "cta_tail_sec": 3.5,
        "tail_hold_sec": 0.5,
        "target_voice_sec": 12.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on the sixth, fifteenth, twenty-fourth—or the ninth, eighteenth, or twenty-seventh—"
            "you always end up carrying everyone else’s emotional weight while nobody checks on you. That’s where your Venus and Mars "
            "numbers collide across five systems. Check the calculator on my profile."
        ),
        "broll_clips": [
            (0.0, 4.0, "broll_01_window_reflection.mp4"),
            (4.0, 7.5, "broll_03_thoughtful_woman.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_mandala.png", 2.8),
            ("image", "scenes_cache/scene_ledger.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 6th, 15th, 24th—or the 9th, 18th, 27th? Why you always end up carrying everyone "
            "else's emotional weight (Venus 6 & Mars 9 across 5 systems) 💛🔥 #numerology #lifepath6 "
            "#lifepath9 #healer #peoplepleaser #empath #spiritualtiktok #relationships"
        ),
        "first_comment": "Were you born on the 6th, 15th, 24th (or 9th, 18th, 27th)—and are you always the therapist friend in your circle? 👇",
        "hashtags": [
            "#numerology", "#lifepath6", "#lifepath9", "#healer",
            "#peoplepleaser", "#empath", "#spiritualtiktok", "#relationships"
        ],
    },
]


class VideoFrameReader:
    """Memory-efficient streaming reader for 1080x1920 MP4 clips at 30fps."""

    def __init__(self, filepath: str, max_seconds: float = 6.0):
        self.filepath = filepath
        self.cap = cv2.VideoCapture(filepath)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video {filepath}")
        self.last_idx = -1
        self.last_img: Optional[Image.Image] = None

    def get_frame(self, local_t: float, darken_ratio: float = 0.85) -> Image.Image:
        target_idx = max(0, int(local_t * 30))
        if target_idx != self.last_idx or self.last_img is None:
            if target_idx < self.last_idx or target_idx > self.last_idx + 5:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.last_idx = -1
            ret, bgr = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, bgr = self.cap.read()
            self.last_idx = target_idx
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            if rgb.shape[1] != 1080 or rgb.shape[0] != 1920:
                rgb = cv2.resize(rgb, (1080, 1920), interpolation=cv2.INTER_LINEAR)
            if darken_ratio < 0.999:
                rgb = (rgb.astype(np.float32) * darken_ratio).clip(0, 255).astype(np.uint8)
            self.last_img = Image.fromarray(rgb)
        return self.last_img.copy()

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class BrollStoryGenerator:
    def __init__(self):
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        self.font_hook = ImageFont.truetype(FONT_BOLD, 42)
        self.font_cap = ImageFont.truetype(FONT_BOLD, 56)
        self.font_cta_top = ImageFont.truetype(FONT_BOLD, 28)
        self.font_cta_main = ImageFont.truetype(FONT_BOLD, 32)

    async def generate_voice_and_3word_cues(
        self, script_text: str, voice: str, rate: str, out_voice_path: str
    ) -> List[Dict[str, Any]]:
        print(f"   [TTS] Synthesizing story voiceover ({voice}, rate={rate})...", flush=True)
        comm = edge_tts.Communicate(script_text, voice, rate=rate)
        audio_chunks = bytearray()
        s_boundaries = []

        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.extend(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                s_boundaries.append(chunk)

        with open(out_voice_path, "wb") as f:
            f.write(audio_chunks)

        cues = []
        for sb in s_boundaries:
            start_sec = sb["offset"] / 10_000_000.0
            dur_sec = sb["duration"] / 10_000_000.0
            words = sb["text"].strip().split()
            if not words:
                continue

            # Split into punchy 2-3 word CapCut-style phrases
            phrases = []
            i = 0
            while i < len(words):
                rem = len(words) - i
                if rem <= 3:
                    phrases.append(" ".join(words[i:]))
                    break
                elif rem == 4:
                    phrases.append(" ".join(words[i : i + 2]))
                    phrases.append(" ".join(words[i + 2 :]))
                    break
                else:
                    phrases.append(" ".join(words[i : i + 3]))
                    i += 3

            tot_chars = sum(len(p) for p in phrases)
            curr_t = start_sec
            for p in phrases:
                p_dur = dur_sec * (len(p) / max(1, tot_chars))
                cues.append({"start": curr_t, "end": curr_t + p_dur, "text": p})
                curr_t += p_dur

        print(f"   [TTS] Built {len(cues)} 3-word CapCut-style caption cues.", flush=True)
        return cues

    def mix_audio_with_subtle_pad(
        self,
        voice_path: str,
        out_mixed_path: str,
        cues: List[Dict[str, Any]],
        tail_hold_sec: float = 1.2,
        target_voice_sec: Optional[float] = None,
    ) -> float:
        """
        Mixes the spoken story with a subtle 432Hz ambient pad and `tail_hold_sec` tail hold.
        If `target_voice_sec` is specified and raw voice exceeds it, gently speeds up voice & cues
        via FFmpeg `atempo` so Cohort C shorts stay strictly between 11.5s and 14.0s (<14.5s).
        """
        cmd_probe0 = [FFMPEG_EXE, "-i", voice_path]
        r0 = subprocess.run(cmd_probe0, capture_output=True, text=True)
        v_dur = 13.0
        for line in r0.stderr.splitlines():
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                v_dur = float(h) * 3600 + float(m) * 60 + float(s)
                break

        tempo = 1.0
        if target_voice_sec and v_dur > target_voice_sec:
            tempo = min(1.35, max(1.0, v_dur / target_voice_sec))
            for c in cues:
                c["start"] = c["start"] / tempo
                c["end"] = c["end"] / tempo
            v_dur = v_dur / tempo
            print(f"   [TTS] Applied pace tempo={tempo:.3f}x -> voice={v_dur:.2f}s (+{tail_hold_sec:.1f}s tail)", flush=True)

        amb_path = voice_path + "_amb.wav"
        cmd_amb = [
            FFMPEG_EXE, "-y", "-f", "lavfi",
            "-i", f"aevalsrc=0.25*sin(2*PI*108*t)+0.25*sin(2*PI*216*t)+0.25*sin(2*PI*324*t)+0.25*sin(2*PI*432*t):s=44100:d={v_dur + tail_hold_sec + 1.0:.2f}",
            "-af", "lowpass=f=420,volume=0.08",
            amb_path,
        ]
        subprocess.run(cmd_amb, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        atempo_filter = f"atempo={tempo:.4f}," if tempo > 1.001 else ""
        filter_complex = (
            f"[0:a]{atempo_filter}apad=pad_dur={tail_hold_sec:.2f}[vpad];"
            f"[vpad]volume=1.0[v];"
            f"[1:a]volume=0.09[bg];"
            f"[v][bg]amix=inputs=2:duration=first:dropout_transition=1"
        )
        cmd_mix = [
            FFMPEG_EXE, "-y",
            "-i", voice_path,
            "-i", amb_path,
            "-filter_complex", filter_complex,
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_mixed_path,
        ]
        subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(amb_path):
            os.remove(amb_path)

        res = subprocess.run([FFMPEG_EXE, "-i", out_mixed_path], capture_output=True, text=True)
        dur = v_dur + tail_hold_sec
        for line in res.stderr.splitlines():
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                dur = float(h) * 3600 + float(m) * 60 + float(s)
                break
        return dur

    def draw_native_tiktok_hook_box(self, draw: ImageDraw.ImageDraw, hook_text: str):
        """
        Draws an authentic native TikTok white rounded-rectangle text box sticker
        centered in the upper-middle safe zone (y ~ 360).
        """
        lines = textwrap.wrap(hook_text, width=28)
        line_bboxes = [draw.textbbox((0, 0), ln, font=self.font_hook) for ln in lines]
        line_widths = [b[2] - b[0] for b in line_bboxes]
        line_h = 56
        max_w = max(line_widths)
        total_h = len(lines) * line_h

        cx, cy = 540, 360
        pad_x, pad_y = 34, 24
        x0 = cx - max_w // 2 - pad_x
        y0 = cy - total_h // 2 - pad_y
        x1 = cx + max_w // 2 + pad_x
        y1 = cy + total_h // 2 + pad_y

        # Subtle drop shadow behind the white TikTok text sticker
        draw.rounded_rectangle(
            [x0 + 4, y0 + 6, x1 + 4, y1 + 6],
            radius=22,
            fill=(0, 0, 0),
        )
        # Crisp white rounded-rectangle box
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=22,
            fill=(255, 255, 255),
        )

        curr_y = y0 + pad_y + line_h // 2 - 4
        for ln in lines:
            draw.text((cx, curr_y), ln, fill=(14, 14, 18), font=self.font_hook, anchor="mm")
            curr_y += line_h

    def draw_capcut_caption(self, draw: ImageDraw.ImageDraw, cue_text: str):
        """
        Renders 56px bold white text with thick black stroke (width=5) and drop shadow
        at y=1320, highlighting at most 1 power word per phrase in warm gold (#FFD147).
        """
        words = cue_text.split()
        if not words:
            return

        gold_idx = -1
        for idx, w_str in enumerate(words):
            clean = w_str.lower().strip(".,!?;:—-()'\"")
            if clean in POWER_WORDS:
                gold_idx = idx
                break
        if gold_idx == -1 and len(words) >= 2:
            gold_idx = max(range(len(words)), key=lambda i: len(words[i]))

        font_use = self.font_cap
        for f_size in (56, 48, 42, 36):
            font_use = self.font_cap if f_size == 56 else ImageFont.truetype(FONT_BOLD, f_size)
            space_w = draw.textbbox((0, 0), " ", font=font_use)[2]
            w_widths = [draw.textbbox((0, 0), w, font=font_use)[2] for w in words]
            tot_w = sum(w_widths) + (len(words) - 1) * space_w
            if tot_w <= 940:
                break

        cx, cy = 540, 1320
        cur_x = cx - tot_w // 2
        for idx, (w_str, ww) in enumerate(zip(words, w_widths)):
            col = (255, 209, 71) if idx == gold_idx else (255, 255, 255)
            draw.text(
                (cur_x + 4, cy + 5),
                w_str,
                fill=(0, 0, 0),
                font=font_use,
                anchor="lm",
                stroke_width=6,
                stroke_fill=(0, 0, 0),
            )
            draw.text(
                (cur_x, cy),
                w_str,
                fill=col,
                font=font_use,
                anchor="lm",
                stroke_width=5,
                stroke_fill=(0, 0, 0),
            )
            cur_x += ww + space_w

    def draw_final_5s_cta_pill(self, draw: ImageDraw.ImageDraw):
        """
        Displays the clean organic Call-To-Action pill in the closing seconds:
        'Tap @sacrednumberblueprint → Try the 5-System Overlap Calculator in our bio'
        """
        line1 = "Tap @sacrednumberblueprint"
        line2 = "→ Try the 5-System Overlap Calculator in our bio"

        cx, cy = 540, 1620
        w_box, h_box = 940, 136
        x0, y0 = cx - w_box // 2, cy - h_box // 2
        x1, y1 = cx + w_box // 2, cy + h_box // 2

        draw.rounded_rectangle(
            [x0 + 4, y0 + 6, x1 + 4, y1 + 6],
            radius=28,
            fill=(0, 0, 0),
        )
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=28,
            fill=(16, 16, 22),
            outline=(255, 209, 71),
            width=3,
        )
        draw.text((cx, cy - 24), line1, fill=(255, 209, 71), font=self.font_cta_main, anchor="mm")
        draw.text((cx, cy + 24), line2, fill=(245, 245, 247), font=self.font_cta_top, anchor="mm")

    def render_video(
        self,
        spec: Dict[str, Any],
        cues: List[Dict[str, Any]],
        mixed_audio_path: str,
        total_dur: float,
        out_mp4: str,
    ):
        fps = 30
        total_frames = int(total_dur * fps)
        is_short = spec.get("format_type") == "cohort_c_short"
        hook_end_sec = spec.get("hook_end_sec", 4.5 if is_short else 4.2)
        cta_tail_sec = spec.get("cta_tail_sec", 3.5 if is_short else 5.0)
        broll_cutoff = 7.5 if is_short else 15.0

        print(
            f"\n[RENDER] Building {spec['filename']} ({total_dur:.2f}s, {total_frames} frames, format={spec.get('format_type')})...",
            flush=True,
        )

        # Preload human B-roll readers
        broll_readers = {}
        for _, _, b_fname in spec["broll_clips"]:
            b_path = os.path.join(BROLL_DIR, b_fname)
            if b_fname not in broll_readers:
                broll_readers[b_fname] = VideoFrameReader(b_path, max_seconds=6.0)

        calc_reader = None
        if not is_short:
            calc_reader = VideoFrameReader(os.path.join(BASE_DIR, "tiktok_promo_1.mp4"), max_seconds=5.5)

        prod_images = {}
        for item in spec["product_scenes"]:
            if item[0] == "image":
                img_path = os.path.join(BASE_DIR, item[1])
                prod_images[item[1]] = Image.open(img_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)

        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-r", str(fps),
            "-i", "-",
            "-i", mixed_audio_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            out_mp4,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        cue_idx = 0
        t0 = time.time()
        p_imgs = [item[1] for item in spec["product_scenes"] if item[0] == "image"]

        for f_idx in range(total_frames):
            t = f_idx / float(fps)

            # 1. Background visual selection
            if t < broll_cutoff:
                active_broll = spec["broll_clips"][-1][2]
                local_t = t
                for b_start, b_end, b_fname in spec["broll_clips"]:
                    if b_start <= t < b_end:
                        active_broll = b_fname
                        local_t = t - b_start
                        break
                frame = broll_readers[active_broll].get_frame(local_t, darken_ratio=0.84)
            elif is_short:
                # Cohort C (7.5s -> end): Fast dynamic zoom reveal across the 2 dossier scenes
                reveal_dur = max(1.0, total_dur - 7.5)
                mid_t = 7.5 + (reveal_dur * 0.48)
                if t < mid_t or len(p_imgs) == 1:
                    img_key = p_imgs[0]
                    u = max(0.0, min(1.0, (t - 7.5) / max(0.5, mid_t - 7.5)))
                    zoom = 1.0 + 0.065 * u
                else:
                    img_key = p_imgs[1]
                    u = max(0.0, min(1.0, (t - mid_t) / max(0.5, total_dur - mid_t)))
                    zoom = 1.055 - 0.045 * u

                base_img = prod_images[img_key]
                new_w, new_h = int(1080 / zoom), int(1920 / zoom)
                x0 = (1080 - new_w) // 2
                y0 = (1920 - new_h) // 2
                frame = base_img.crop((x0, y0, x0 + new_w, y0 + new_h)).resize((1080, 1920), Image.Resampling.BILINEAR)
            elif t < 19.5 and calc_reader is not None:
                frame = calc_reader.get_frame(t - 15.0, darken_ratio=0.96)
            else:
                if t < 27.0:
                    img_key = p_imgs[0]
                    u = (t - 19.5) / 7.5
                    zoom = 1.0 + 0.035 * u
                elif t < 34.0:
                    img_key = p_imgs[1]
                    u = (t - 27.0) / 7.0
                    zoom = 1.035 - 0.035 * u
                else:
                    img_key = p_imgs[2]
                    u = (t - 34.0) / max(1.0, total_dur - 34.0)
                    zoom = 1.0 + 0.03 * u

                base_img = prod_images[img_key]
                new_w, new_h = int(1080 / zoom), int(1920 / zoom)
                x0 = (1080 - new_w) // 2
                y0 = (1920 - new_h) // 2
                frame = base_img.crop((x0, y0, x0 + new_w, y0 + new_h)).resize((1080, 1920), Image.Resampling.BILINEAR)

            draw = ImageDraw.Draw(frame)

            # 2. Native TikTok White Rounded-Rectangle Hook Box (0.0s - hook_end_sec)
            if t <= hook_end_sec:
                self.draw_native_tiktok_hook_box(draw, spec["hook_box_text"])

            # 3. Center 3-Word CapCut-Style Captions Throughout
            active_cue_text = None
            while cue_idx < len(cues) and cues[cue_idx]["end"] < t:
                cue_idx += 1
            if cue_idx < len(cues) and cues[cue_idx]["start"] <= t <= cues[cue_idx]["end"]:
                active_cue_text = cues[cue_idx]["text"]

            if active_cue_text:
                self.draw_capcut_caption(draw, active_cue_text)

            # 4. Closing Call-to-Action Pill
            if t >= (total_dur - cta_tail_sec):
                self.draw_final_5s_cta_pill(draw)

            buf = io.BytesIO()
            frame.save(buf, format="JPEG", quality=92)
            proc.stdin.write(buf.getvalue())

            if (f_idx + 1) % 150 == 0 or (f_idx + 1) == total_frames:
                pct = (f_idx + 1) / total_frames * 100.0
                fps_spd = (f_idx + 1) / max(0.01, time.time() - t0)
                print(f"   Frame {f_idx + 1}/{total_frames} ({pct:.1f}%) | {fps_spd:.1f} fps", flush=True)

        proc.stdin.close()
        proc.wait()
        for rdr in broll_readers.values():
            rdr.close()
        if calc_reader is not None:
            calc_reader.close()

        sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
        print(f"✓ Rendered {out_mp4} ({sz_mb:.2f} MB in {time.time() - t0:.1f}s)", flush=True)

    def extract_audit_frames(self, mp4_path: str, prefix: str, is_short: bool = False) -> List[str]:
        """Extracts audit frames for visual verification and syncs to artifacts."""
        cap = cv2.VideoCapture(mp4_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        saved = []
        checkpoints = (
            [(2.0, "2s_hook"), (5.5, "5s_broll"), (10.5, "10s_reveal")]
            if is_short
            else [(2.0, "2s_hook"), (8.0, "8s_broll"), (20.0, "20s_reveal")]
        )
        for sec, tag in checkpoints:
            f_num = int(sec * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, f_num)
            ret, frame = cap.read()
            if ret:
                fname = f"audit_{prefix}_{tag}.png"
                local_p = os.path.join(BASE_DIR, fname)
                cv2.imwrite(local_p, frame)
                if os.path.exists(ARTIFACTS_DIR):
                    shutil.copy2(local_p, os.path.join(ARTIFACTS_DIR, fname))
                saved.append(local_p)
                print(f"   ✓ Extracted audit frame ({sec:.1f}s): {fname}", flush=True)
        cap.release()
        return saved

    def update_tiktok_scripts_json(self):
        """Registers Cohort-B and Cohort-C videos in tiktok_scripts.json with their captions & first_comments."""
        scripts_path = os.path.join(BASE_DIR, "tiktok_scripts.json")
        data = {"scripts": []}
        if os.path.exists(scripts_path):
            with open(scripts_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        by_fname = {s["filename"]: s for s in data.get("scripts", [])}
        for spec in COHORT_B_SPECS + COHORT_C_SPECS:
            entry = {
                "id": spec["id"],
                "cohort": spec.get("cohort", "Cohort B"),
                "filename": spec["filename"],
                "hook_name": spec["hook_box_text"],
                "lang": "en",
                "voice": spec["voice"],
                "rate": spec["rate"],
                "spoken_script": spec["spoken_script"],
                "tiktok_caption": spec["tiktok_caption"],
                "first_comment": spec.get("first_comment", ""),
                "hashtags": spec["hashtags"],
            }
            by_fname[spec["filename"]] = entry
        data["scripts"] = list(by_fname.values())
        with open(scripts_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if os.path.exists(GDRIVE_QUEUE_DIR):
            shutil.copy2(scripts_path, os.path.join(GDRIVE_QUEUE_DIR, "tiktok_scripts.json"))

    async def run(self, cohort: str = "C", only_ids: Optional[str] = None):
        target_specs = (
            COHORT_C_SPECS
            if cohort.upper() == "C"
            else (COHORT_B_SPECS if cohort.upper() == "B" else COHORT_B_SPECS + COHORT_C_SPECS)
        )
        if only_ids:
            allowed = {x.strip() for x in only_ids.split(",") if x.strip()}
            target_specs = [s for s in target_specs if s["id"] in allowed or s["filename"] in allowed]
        print("=" * 72, flush=True)
        print(f"   STARTING HUMAN B-ROLL + PRODUCT REVEAL GENERATOR (COHORT: {cohort.upper()})", flush=True)
        print("=" * 72, flush=True)

        self.update_tiktok_scripts_json()

        for spec in target_specs:
            vid_id = spec["id"]
            fname = spec["filename"]
            is_short = spec.get("format_type") == "cohort_c_short"
            out_mp4 = os.path.join(VIDEOS_DIR, fname)
            v_mp3 = os.path.join(BASE_DIR, f"_voice_{vid_id}.mp3")
            m_mp3 = os.path.join(BASE_DIR, f"_mixed_{vid_id}.mp3")

            print(f"\n▶ Generating [{spec.get('cohort', 'Video')}] [{vid_id}]: {fname}", flush=True)
            cues = await self.generate_voice_and_3word_cues(
                spec["spoken_script"], spec["voice"], spec["rate"], v_mp3
            )
            dur = self.mix_audio_with_subtle_pad(
                v_mp3,
                m_mp3,
                cues=cues,
                tail_hold_sec=spec.get("tail_hold_sec", 0.5 if is_short else 1.2),
                target_voice_sec=spec.get("target_voice_sec"),
            )
            self.render_video(spec, cues, m_mp3, dur, out_mp4)

            for tmp in (v_mp3, m_mp3):
                if os.path.exists(tmp):
                    os.remove(tmp)

            # Copy to root, Google Drive tiktok_queue, and Artifacts
            shutil.copy2(out_mp4, os.path.join(BASE_DIR, fname))
            if os.path.exists(GDRIVE_QUEUE_DIR):
                g_dst = os.path.join(GDRIVE_QUEUE_DIR, fname)
                shutil.copy2(out_mp4, g_dst)
                print(f"   ✓ Synced to Google Drive Queue: {g_dst}", flush=True)
            if os.path.exists(ARTIFACTS_DIR):
                shutil.copy2(out_mp4, os.path.join(ARTIFACTS_DIR, fname))

            self.extract_audit_frames(out_mp4, vid_id, is_short=is_short)

        print("\n" + "=" * 72, flush=True)
        print(f"   ✓ ALL COHORT-{cohort.upper()} VIDEOS RENDERED & SYNCED TO QUEUE!", flush=True)
        print("=" * 72, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Cohort B or Cohort C TikTok videos.")
    parser.add_argument("--cohort", type=str, default="C", help="Cohort to render: C, B, or ALL (default: C)")
    parser.add_argument("--only", type=str, default=None, help="Comma-separated video IDs to render (e.g., short_04,short_05,short_06)")
    args = parser.parse_args()
    gen = BrollStoryGenerator()
    asyncio.run(gen.run(cohort=args.cohort, only_ids=args.only))
