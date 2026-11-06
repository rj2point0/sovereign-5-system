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
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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
    {
        "id": "short_10",
        "cohort": "Cohort C · Jenny Hoyos Relationship",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_10_attract_unavailable.mp4",
        "grid_headline": "WHY THEY\nPULL AWAY",
        "grid_sub": "Born 2, 7, 11, 16, 20, 25, 29?",
        "hook_box_text": "Born on the 2nd, 7th, 11th, 16th, 20th, 25th, or 29th? Why you fall for people who pull away:",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Born on the second, seventh, sixteenth, or twenty-fifth? "
            "You always fall for people who pull away. "
            "Your birth day says who you fall for, but your full birth code says who can actually love you back. "
            "Tap my bio to test your love code now."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_02_late_night_phone.mp4"),
            (4.2, 8.0, "broll_11_dusk_river_silhouette.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 2nd, 7th, 11th, 16th, 20th, 25th, or 29th? Why you keep falling for people who pull away "
            "(your birth day says who you chase, but your full birth code shows who loves you back) 💔✨ "
            "#relationships #attachmentstyle #numerology #datingadvice #lifepath7 #lifepath2 #twinflame #lovecode"
        ),
        "first_comment": "Were you born on the 2nd, 7th, 11th, 16th, 20th, 25th, or 29th—and do you always fall for people who pull away? 👇",
        "hashtags": [
            "#relationships", "#attachmentstyle", "#numerology", "#datingadvice",
            "#lifepath7", "#lifepath2", "#twinflame", "#lovecode"
        ],
    },
    {
        "id": "short_11",
        "cohort": "Cohort C · Jenny Hoyos Relationship",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_11_overgiver_in_love.mp4",
        "grid_headline": "ALWAYS CARE\nMORE IN LOVE",
        "grid_sub": "Born 4, 6, 9, 13, 15, 18, 22, 27?",
        "hook_box_text": "Born on the 4th, 6th, 9th, 13th, 15th, 18th, 22nd, 24th, 27th, or 31st? Why you ALWAYS care more in love:",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on one of these days, you are always the one who cares more in love. "
            "You fix their whole life, but no one takes care of you. "
            "Therefore, your chart attracts takers until you know your real partner numbers. "
            "Tap my bio to see your love code."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_03_thoughtful_woman.mp4"),
            (4.2, 8.0, "broll_07_journaling_ritual.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 4th, 6th, 9th, 13th, 15th, 18th, 22nd, 24th, 27th, or 31st? Why you are ALWAYS the one "
            "who cares more in relationships (and how to find the birth numbers that give back) 💛✨ "
            "#relationships #overgiver #peoplepleaser #numerology #datingadvice #lifepath6 #lifepath4 #lovecode"
        ),
        "first_comment": "Were you born on the 4th, 6th, 9th, 13th, 15th, 18th, 22nd, 24th, 27th, or 31st—and are you tired of caring more than they do? 👇",
        "hashtags": [
            "#relationships", "#overgiver", "#peoplepleaser", "#numerology",
            "#datingadvice", "#lifepath6", "#lifepath4", "#lovecode"
        ],
    },
    {
        "id": "short_12",
        "cohort": "Cohort C · Jenny Hoyos Relationship",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_12_power_struggle_love.mp4",
        "grid_headline": "FIGHT FOR\nCONTROL IN LOVE",
        "grid_sub": "Born 1, 3, 5, 8, 10, 14, 19, 28?",
        "hook_box_text": "Born on the 1st, 3rd, 5th, 8th, 10th, 12th, 14th, 17th, 19th, 21st, 23rd, 26th, 28th, or 30th? Why you fight for control in love:",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you were born on one of these days, you want a strong partner. "
            "But the second they get close, you fight them for control. "
            "Your birth day wants to lead, yet your heart just wants to feel safe. "
            "Tap my bio to check your love code right now."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_08_phone_discovery.mp4"),
            (4.2, 8.0, "broll_15_sunset_ocean_waves.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_anchors.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 1st, 3rd, 5th, 8th, 10th, 12th, 14th, 17th, 19th, 21st, 23rd, 26th, 28th, or 30th? "
            "Why you want someone strong—but fight them for control the second they get close ⚡❤️‍🔥 "
            "#relationships #hyperindependence #numerology #datingadvice #lifepath1 #lifepath8 #attachmentstyle #lovecode"
        ),
        "first_comment": "Are you on this list (1, 3, 5, 8, 10, 12, 14, 17, 19, 21, 23, 26, 28, 30)—and do you struggle to let your guard down in love? 👇",
        "hashtags": [
            "#relationships", "#hyperindependence", "#numerology", "#datingadvice",
            "#lifepath1", "#lifepath8", "#attachmentstyle", "#lovecode"
        ],
    },
    {
        "id": "short_13",
        "cohort": "Cohort C · Outlier Batch 3",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_13_hot_then_cold_6weeks.mp4",
        "grid_headline": "HOT IN WEEK 2\nCOLD IN WEEK 6",
        "grid_sub": "Why Your Birth Day Pulls Runners",
        "hook_box_text": "Why do they act obsessed with you in week two, then go cold in week six?",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Why do they act obsessed with you in week two, then go cold in week six? "
            "You think they just lost feelings. But if you were born on the 2nd, 7th, 11th, 16th, 20th, 25th, or 29th, "
            "your birth day pulls in runners. Therefore, the moment you get close, they panic and pull back. "
            "Test your birthday and theirs at the link in bio to see your real love match."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_09_couple_silhouette_walk.mp4"),
            (4.2, 8.0, "broll_13_rain_ripples_water.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Why do they act obsessed with you in week two, then go cold in week six? "
            "(Born on the 2nd, 7th, 11th, 16th, 20th, 25th, or 29th—here is why your birth day pulls in runners) 💔✨ "
            "#relationships #attachmentstyle #avoidantattachment #numerology #datingadvice #situationship #lovecode #twinflame"
        ),
        "first_comment": "Have you ever had someone act obsessed in week 2 and go cold by week 6? Drop your birthday month & day below 👇",
        "hashtags": [
            "#relationships", "#attachmentstyle", "#avoidantattachment", "#numerology",
            "#datingadvice", "#situationship", "#lovecode", "#twinflame"
        ],
    },
    {
        "id": "short_14",
        "cohort": "Cohort C · Outlier Batch 3",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_14_test_crush_birthday.mp4",
        "grid_headline": "TEST CRUSH'S\nBIRTHDAY",
        "grid_sub": "If These Clash, One Always Chases",
        "hook_box_text": "Test your crush's birthday right now: if your birth days clash here, one of you will always chase.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Test your crush's birthday right now: if your birth days clash here, one of you will always chase. "
            "Most apps only check your zodiac sign. But your birth day number shows how you fight at 2 AM, "
            "while your Life Path shows how you love. Therefore, when those two numbers clash, one person begs while the other shuts down. "
            "Plug in both birthdays at the link in bio to see your compatibility score in 10 seconds."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_10_couple_sunset_embrace.mp4"),
            (4.2, 8.0, "broll_19_couple_field_walk.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Test your crush's birthday right now: if your birth days clash here, one of you will always chase "
            "(Birth Day = how you fight at 2 AM vs. Life Path = how you love) 🔮❤️‍🔥 "
            "#relationships #compatibility #crush #numerology #datingadvice #zodiaccompatibility #lovecode #soulmate"
        ),
        "first_comment": "What day of the month were you born, and what day was your partner or crush born? Drop both below 👇",
        "hashtags": [
            "#relationships", "#compatibility", "#crush", "#numerology",
            "#datingadvice", "#zodiaccompatibility", "#lovecode", "#soulmate"
        ],
    },
    {
        "id": "short_15",
        "cohort": "Cohort C · Outlier Batch 3",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_15_miss_fake_version.mp4",
        "grid_headline": "IN LOVE WITH\nPOTENTIAL",
        "grid_sub": "You Miss Who They Faked Day 1",
        "hook_box_text": "You don't actually miss your ex. You miss the person they faked for the first 30 days.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "You don't actually miss your ex. You miss the person they faked for the first 30 days. "
            "If you were born on the 1st, 4th, 6th, 8th, 9th, 13th, 15th, 18th, 22nd, or 27th, you fall in love with potential. "
            "But your Chinese birth grid is missing its boundary arrow. Therefore, you give ten chances to someone who only deserved one. "
            "Check your 5-system love code at the link in bio before you text them back."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_01_window_reflection.mp4"),
            (4.2, 8.0, "broll_12_beach_shore_brooding.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_loshu.png", 2.8),
            ("image", "scenes_cache/scene_relationships.png", 99.0),
        ],
        "tiktok_caption": (
            "You don't actually miss your ex. You miss the person they faked for the first 30 days "
            "(Born on the 1st, 4th, 6th, 8th, 9th, 13th, 15th, 18th, 22nd, or 27th—why you fall in love with potential) 💔🕯️ "
            "#relationships #breakupadvice #nocontact #numerology #loshugrid #datingadvice #overgiver #lovecode"
        ),
        "first_comment": "Do you fall in love with who someone actually is—or their potential? Drop your birth day below 👇",
        "hashtags": [
            "#relationships", "#breakupadvice", "#nocontact", "#numerology",
            "#loshugrid", "#datingadvice", "#overgiver", "#lovecode"
        ],
    },
    {
        "id": "short_16",
        "cohort": "Cohort C · Outlier Batch 4",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_16_last_text_crumbs.mp4",
        "grid_headline": "BEGGING FOR\nCRUMBS",
        "grid_sub": "Look At Your Last Text Sent",
        "hook_box_text": "Look at the last text you sent them. That isn't love—that's your birth code begging for crumbs.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Look at the last text you sent them. That isn't love—that's your birth code begging for crumbs. "
            "If you were born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, 25th, or 29th, you panic when someone goes quiet. "
            "But chasing them only triggers their runner number. Therefore, the harder you text, the faster they pull away. "
            "Check both of your birthdays at the link in bio to see how to flip the chase."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_18_hands_texting_phone.mp4"),
            (4.2, 8.0, "broll_14_city_night_walk.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Look at the last text you sent them. That isn't love—that's your birth code begging for crumbs "
            "(Born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, 25th, or 29th—here is how to flip the chase) 💔✨ "
            "#relationships #anxiousattachment #textingadvice #numerology #datingadvice #nocontact #lovecode #attachmentstyle"
        ),
        "first_comment": "Were you born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, 25th, or 29th—and do you panic when they go quiet? 👇",
        "hashtags": [
            "#relationships", "#anxiousattachment", "#textingadvice", "#numerology",
            "#datingadvice", "#nocontact", "#lovecode", "#attachmentstyle"
        ],
    },
    {
        "id": "short_17",
        "cohort": "Cohort C · Outlier Batch 4",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_17_three_months_situationship.mp4",
        "grid_headline": "3-MONTH\nSITUATIONSHIP",
        "grid_sub": "Their Birth Code Answered You",
        "hook_box_text": "If you have to ask what you are after three months, their birth code already gave you the answer.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "If you have to ask what you are after three months, their birth code already gave you the answer. "
            "You keep waiting for them to be ready. But when your Life Path craves commitment and their birth day number craves freedom: "
            "they will keep you in the gray zone forever. Therefore, waiting another month won't change their mind. "
            "Plug their birthday into the link in bio to see if they will ever commit."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_20_couple_tension_apart.mp4"),
            (4.2, 8.0, "broll_12_beach_shore_brooding.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "If you have to ask what you are after three months, their birth code already gave you the answer "
            "(when your Life Path craves commitment and their birth day craves freedom) 🥀🔮 "
            "#situationship #relationships #datingadvice #numerology #commitmentissues #compatibility #lovecode #heisnotthatintoyou"
        ),
        "first_comment": "Have you ever waited months for someone to be ready to commit? Drop both of your birth days below 👇",
        "hashtags": [
            "#situationship", "#relationships", "#datingadvice", "#numerology",
            "#commitmentissues", "#compatibility", "#lovecode", "#heisnotthatintoyou"
        ],
    },
    {
        "id": "short_18",
        "cohort": "Cohort C · Outlier Batch 4",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_18_cares_less_power.mp4",
        "grid_headline": "STOPPED ACCEPTING\nBARE MINIMUM",
        "grid_sub": "Your Boundary Reset Year",
        "hook_box_text": "They didn't suddenly lose feelings. You just stopped accepting bare minimum effort.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "They didn't suddenly lose feelings. You just stopped accepting bare minimum effort. "
            "If you were born on the 1st, 3rd, 4th, 8th, 9th, 10th, 13th, 17th, 18th, 19th, 22nd, 26th, 27th, 28th, or 31st, "
            "you carry the whole relationship on your back. But the second you match their energy, they call you cold. "
            "Therefore, your birth code is entering a boundary reset year. "
            "See your next 90 days of love timing at the link in bio right now."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_16_candlelight_woman_face.mp4"),
            (4.2, 8.0, "broll_17_candle_dark_glow.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_anchors.png", 2.8),
            ("image", "scenes_cache/scene_relationships.png", 99.0),
        ],
        "tiktok_caption": (
            "They didn't suddenly lose feelings. You just stopped accepting bare minimum effort "
            "(Born on the 1st, 3rd, 4th, 8th, 9th, 10th, 13th, 17th, 18th, 19th, 22nd, 26th, 27th, 28th, or 31st—your boundary reset year) ⚡👑 "
            "#relationships #bareminimum #highstandards #numerology #datingadvice #selfworth #lovecode #boundaries"
        ),
        "first_comment": "Were you born on the 1st, 3rd, 4th, 8th, 9th, 10th, 13th, 17th, 18th, 19th, 22nd, 26th, 27th, 28th, or 31st—and did you match their energy? 👇",
        "hashtags": [
            "#relationships", "#bareminimum", "#highstandards", "#numerology",
            "#datingadvice", "#selfworth", "#lovecode", "#boundaries"
        ],
    },
    {
        "id": "short_19",
        "cohort": "Cohort C · Outlier Batch 5",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_19_text_back_anxiety.mp4",
        "grid_headline": "WHY THEY LEAVE\nYOU ON READ",
        "grid_sub": "BIRTH CODE CLASH",
        "hook_box_text": "Why do you stare at your phone for hours waiting for a text back?",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Why do you stare at your phone for hours waiting for a text back? "
            "If you were born on the 2nd, 3rd, 5th, 6th, 11th, 14th, 15th, 20th, 23rd, 24th, or 29th, you bond fast. "
            "But your heart chases a distance number. Therefore, the closer you get, the more they pull back. "
            "Tap the link in bio to test both birthdays right now."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_02_late_night_phone.mp4"),
            (4.2, 8.0, "broll_18_hands_texting_phone.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Why do you stare at your phone waiting for a text back? "
            "(Born on the 2nd, 3rd, 5th, 6th, 11th, 14th, 15th, 20th, 23rd, 24th, or 29th—fast-bonding Birth Day vs. distance number) 📱💔 "
            "#relationships #texting #leftonread #anxiousattachment #numerology #datingadvice #lovecode #compatibility"
        ),
        "first_comment": "Were you born on the 2nd, 3rd, 5th, 6th, 11th, 14th, 15th, 20th, 23rd, 24th, or 29th—and do you hate waiting on a text back? 👇",
        "hashtags": [
            "#relationships", "#texting", "#leftonread", "#anxiousattachment",
            "#numerology", "#datingadvice", "#lovecode", "#compatibility"
        ],
    },
    {
        "id": "short_20",
        "cohort": "Cohort C · Outlier Batch 5",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_20_wrong_birthday_match.mp4",
        "grid_headline": "THE 3 BIRTHDAYS\nTO AVOID DATING",
        "grid_sub": "CHECK YOUR MATCH",
        "hook_box_text": "Every birthday has 3 natural soulmate dates and 3 dates that drain your energy.",
        "hook_end_sec": 4.2,
        "cta_tail_sec": 3.4,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 13.6,
        "voice": "en-US-AvaNeural",
        "rate": "+12%",
        "spoken_script": (
            "Every birth day has three soulmate dates, and three dates that drain you. "
            "Most apps only check your star sign. "
            "But your star sign misses your 2 AM heart number. Therefore, you keep dating the three dates that drain your peace. "
            "Check their birth day in five seconds at the link in bio."
        ),
        "broll_clips": [
            (0.0, 4.2, "broll_19_couple_field_walk.mp4"),
            (4.2, 8.0, "broll_20_couple_tension_apart.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 2.8),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Every birthday has 3 natural soulmate dates—and 3 dates that drain your energy "
            "(why checking only zodiac signs misses your 2 AM emotional number) 🔮❤️‍🔥 "
            "#relationships #soulmate #compatibility #numerology #datingadvice #zodiacsigns #lovecode #birthdaycompatibility"
        ),
        "first_comment": "What day of the month were you born—and what day was the person who drained your energy born? Drop both below 👇",
        "hashtags": [
            "#relationships", "#soulmate", "#compatibility", "#numerology",
            "#datingadvice", "#zodiacsigns", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_21",
        "cohort": "Cohort C · Outlier Batch 5 (7.5s Visual Demo)",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_21_november_love_shift.mp4",
        "grid_headline": "YOUR NOVEMBER\nLOVE SHIFT",
        "grid_sub": "NEXT 30 DAYS",
        "hook_box_text": "Born on the 1st, 4th, 7th, 8th, 9th, 10th, 13th, 16th, 17th, 18th, 19th, 22nd, 25th, 26th, 27th, 28th, or 31st? Your November love shift:",
        "hook_end_sec": 2.9,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "Born on the 1st, 4th, 7th, 8th, 9th, 19th, or 25th? "
            "The last three months felt heavy in love, "
            "but your November love shift starts this week. "
            "Test both birthdays in bio."
        ),
        "broll_clips": [
            (0.0, 2.3, "broll_11_dusk_river_silhouette.mp4"),
            (2.3, 4.6, "broll_15_sunset_ocean_waves.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_anchors.png", 1.5),
            ("image", "scenes_cache/scene_relationships.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 1st, 4th, 7th, 8th, 9th, 10th, 13th, 16th, 17th, 18th, 19th, 22nd, 25th, 26th, 27th, 28th, or 31st? "
            "Why the last 3 months felt heavy in love—and how your 52-day timing cycle shifts this week 🌙✨ "
            "#november #relationships #lovetiming #numerology #datingadvice #spiritualtiktok #lovecode #52daycycle"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#november", "#relationships", "#lovetiming", "#numerology",
            "#datingadvice", "#spiritualtiktok", "#lovecode", "#52daycycle"
        ],
    },
    {
        "id": "short_22",
        "cohort": "Cohort C · Outlier Batch 6 (7-Sec Retention)",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_22_7sec_ghost_days.mp4",
        "grid_headline": "DAYS THAT GO\nCOLD FAST",
        "grid_sub": "AVOIDANT BIRTH CODE",
        "hook_box_text": "Born on the 4th, 7th, 8th, 16th, 17th, 25th, or 26th? Why they go cold overnight:",
        "hook_end_sec": 2.9,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "spoken_script": (
            "Born on the 4th, 7th, 8th, 16th, or 25th? "
            "They act obsessed, then go cold fast. "
            "But closeness scares their birth code. "
            "Test both birthdays in bio."
        ),
        "broll_clips": [
            (0.0, 2.3, "broll_20_couple_tension_apart.mp4"),
            (2.3, 4.6, "broll_12_beach_shore_brooding.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 4th, 7th, 8th, 16th, 17th, 25th, or 26th? Why they act obsessed with you and then suddenly go cold overnight "
            "(it's an avoidant birth code reflex—test both birthdays in bio) 💔🔮 "
            "#relationships #avoidantattachment #situationship #numerology #datingadvice #ghosting #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Have you ever dated someone born on the 4th, 7th, 8th, 16th, 17th, 25th, or 26th who went cold fast? Drop both birth days below 👇",
        "hashtags": [
            "#relationships", "#avoidantattachment", "#situationship", "#numerology",
            "#datingadvice", "#ghosting", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_23",
        "cohort": "Cohort C · Outlier Batch 6 (7-Sec Retention)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("NEVER", "coral"),
            ("DOUBLE TEXT", "gold"),
            ("THIS BIRTH DAY", "white"),
        ],
        "giant_sub_pill": "BORN 2nd · 6th · 9th · 11th · 15th · 20th · 24th · 29th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_23_7sec_double_text.mp4",
        "grid_headline": "NEVER\nDOUBLE TEXT\nTHESE BIRTH DAYS",
        "grid_sub": "DO THIS INSTEAD",
        "hook_box_text": "Born on the 2nd, 6th, 9th, 11th, 15th, 20th, 24th, or 29th? Never double text them:",
        "hook_end_sec": 5.8,
        "cta_tail_sec": 1.8,
        "broll_cutoff": 5.8,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I really value our connection, so I'm...",
        "spoken_script": (
            "Born on the 2nd, 6th, 11th, 20th, or 29th? "
            "Stop double texting when they go quiet. "
            "But chasing makes them pull back more. "
            "Match their silence and check bio."
        ),
        "broll_clips": [
            (0.0, 2.9, "emo_07_upset_after_argument.mp4"),
            (2.9, 5.8, "emo_12_upset_couple_closeup.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 2nd, 6th, 9th, 11th, 15th, 20th, 24th, or 29th? Stop double texting when they go quiet—here is how to flip the chase 📱💔 "
            "#relationships #textingadvice #doubletext #anxiousattachment #numerology #datingadvice #nocontact #lovecode"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '14 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#textingadvice", "#doubletext", "#anxiousattachment",
            "#numerology", "#datingadvice", "#nocontact", "#lovecode"
        ],
    },
    {
        "id": "short_24",
        "cohort": "Cohort C · Outlier Batch 6 (7-Sec Retention)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("YOUR TRUE", "white"),
            ("SOULMATE", "gold"),
            ("BIRTH DAY", "coral"),
        ],
        "giant_sub_pill": "BORN 1st · 3rd · 5th · 10th · 12th · 14th · 19th · 23rd · 28th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_24_7sec_soulmate_day.mp4",
        "grid_headline": "YOUR TRUE\nSOULMATE\nBIRTH DAY",
        "grid_sub": "TEST BOTH BIRTHDAYS",
        "hook_box_text": "Born on the 1st, 3rd, 5th, 10th, 12th, 14th, 19th, 21st, 23rd, 28th, or 30th? Your soulmate day:",
        "hook_end_sec": 5.8,
        "cta_tail_sec": 1.8,
        "broll_cutoff": 5.8,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "Born on the 1st, 5th, 10th, 19th, or 23rd? "
            "Only one birth day can match your fire. "
            "But wrong dates drain your heart. "
            "Check your match in bio."
        ),
        "broll_clips": [
            (0.0, 2.9, "emo_10_loving_couple_close.mp4"),
            (2.9, 5.8, "emo_03_couple_silence_apart.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 1st, 3rd, 5th, 10th, 12th, 14th, 19th, 21st, 23rd, 28th, or 30th? "
            "Only one birth number can handle your fire without starting a power struggle 🔥❤️‍🔥 "
            "#relationships #soulmate #compatibility #numerology #datingadvice #lovecode #birthdaycompatibility #crush"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#soulmate", "#compatibility", "#numerology",
            "#datingadvice", "#lovecode", "#birthdaycompatibility", "#crush"
        ],
    },
    {
        "id": "short_25",
        "cohort": "Cohort C · Outlier Batch 6 (7.5s Visual Demo)",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_25_7sec_karmic_or_soulmate.mp4",
        "grid_headline": "SOULMATE OR\nKARMIC TRAP?",
        "grid_sub": "TEST BOTH BIRTHDAYS",
        "hook_box_text": "Born on the 1st, 5th, 10th, 14th, 19th, 23rd, or 28th? Soulmate or karmic trap:",
        "hook_end_sec": 2.9,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "Born on the 1st, 5th, 10th, 14th, 19th, 23rd, or 28th? "
            "Fast chemistry can be a karmic trap. "
            "So tap the bio link to test both birthdays free."
        ),
        "broll_clips": [
            (0.0, 2.3, "broll_09_couple_silhouette_walk.mp4"),
            (2.3, 4.6, "broll_16_candlelight_woman_face.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 1st, 5th, 10th, 14th, 19th, 23rd, or 28th? Intense chemistry can be a karmic trap—tap the bio link to test both birthdays free 💔🔮 "
            "#relationships #karmicrelationship #soulmate #numerology #datingadvice #lovecode #birthdaycompatibility #situationship"
        ),
        "first_comment": "Were you born on the 1st, 5th, 10th, 14th, 19th, 23rd, or 28th—and what day was your partner or crush born? Drop both below 👇",
        "hashtags": [
            "#relationships", "#karmicrelationship", "#soulmate", "#numerology",
            "#datingadvice", "#lovecode", "#birthdaycompatibility", "#situationship"
        ],
    },
    {
        "id": "short_26",
        "cohort": "Cohort C · Outlier Batch 6 (7.5s Visual Demo)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("DO THEY", "white"),
            ("MISS YOU", "gold"),
            ("IN NO CONTACT?", "coral"),
        ],
        "giant_sub_pill": "BORN 2nd · 6th · 7th · 11th · 15th · 16th · 20th · 24th · 25th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_26_7sec_no_contact_thoughts.mp4",
        "grid_headline": "DO THEY MISS YOU\nIN NO CONTACT?",
        "grid_sub": "CHECK THEIR BIRTH DAY",
        "hook_box_text": "If they were born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, or 25th:",
        "hook_end_sec": 5.8,
        "cta_tail_sec": 1.8,
        "broll_cutoff": 5.8,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“I'm taking a step back this week because...",
        "spoken_script": (
            "If they were born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, or 25th, "
            "silence does not mean they forgot you. "
            "So check their exact text script in our bio."
        ),
        "broll_clips": [
            (0.0, 2.9, "emo_11_worried_sad_woman_closeup.mp4"),
            (2.9, 5.8, "emo_01_woman_phone_night.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "If they were born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, or 25th, silence does not mean they forgot you "
            "(check their exact Flip The Chase text script in our bio) 📱💔 "
            "#nocontact #relationships #textingadvice #avoidantattachment #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '14 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#nocontact", "#relationships", "#textingadvice", "#avoidantattachment",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_27",
        "cohort": "Cohort C · Outlier Batch 6 (7.5s Visual Demo)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("WHY HE", "white"),
            ("PULLS AWAY", "coral"),
            ("BY BIRTH DAY", "gold"),
        ],
        "giant_sub_pill": "BORN 3rd · 4th · 8th · 9th · 12th · 13th · 17th · 18th · 22nd · 27th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_27_7sec_november_turning_point.mp4",
        "grid_headline": "WHY HE\nPULLS AWAY\nBY BIRTH DAY",
        "grid_sub": "YOUR 90-DAY CALENDAR",
        "hook_box_text": "Born on the 3rd, 4th, 8th, 9th, 12th, 13th, 17th, 18th, 21st, 22nd, 26th, 27th, 30th, or 31st?",
        "hook_end_sec": 5.8,
        "cta_tail_sec": 1.8,
        "broll_cutoff": 5.8,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "Born on the 3rd, 4th, 8th, 9th, 13th, 18th, or 27th? "
            "Your next love shift starts this week. "
            "So tap our bio to see your dates."
        ),
        "broll_clips": [
            (0.0, 2.9, "emo_05_couple_upset_disappointed.mp4"),
            (2.9, 5.8, "emo_04_guy_apologizing_upset_gf.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_anchors.png", 1.5),
            ("image", "scenes_cache/scene_relationships.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 3rd, 4th, 8th, 9th, 12th, 13th, 17th, 18th, 21st, 22nd, 26th, 27th, 30th, or 31st? "
            "Your next love shift starts this week—tap our bio to see your 3 turning-point dates 🌙✨ "
            "#november #relationships #lovetiming #numerology #datingadvice #lovecode #birthdaycompatibility #soulmate"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#november", "#relationships", "#lovetiming", "#numerology",
            "#datingadvice", "#lovecode", "#birthdaycompatibility", "#soulmate"
        ],
    },
    {
        "id": "short_28",
        "cohort": "Cohort C · Outlier Batch 7 (7.5s Comment Both Days + Visual Demo)",
        "format_type": "cohort_c_short",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_28_7sec_who_chases_who.mp4",
        "grid_headline": "WHO CHASES WHO\nBY BIRTH DAY",
        "grid_sub": "DROP BOTH DAYS BELOW",
        "hook_box_text": "Born on the 2nd, 6th, 9th, 11th, 15th, 18th, 20th, 24th, 27th, or 29th? Who chases who:",
        "hook_end_sec": 2.9,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I really value our connection, so I'm...",
        "spoken_script": (
            "Born on the 2nd, 6th, 9th, 11th, 15th, 18th, 20th, 24th, 27th, or 29th? "
            "You always care more first. "
            "So drop both birth days below or tap our bio."
        ),
        "broll_clips": [
            (0.0, 2.3, "broll_03_thoughtful_woman.mp4"),
            (2.3, 4.6, "broll_19_couple_field_walk.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Born on the 2nd, 6th, 9th, 11th, 15th, 18th, 20th, 24th, 27th, or 29th? Why you always care more first "
            "(drop both birth days below or test your match in our bio) 💔🔮 "
            "#relationships #overgiver #attachmentstyle #numerology #datingadvice #lovecode #birthdaycompatibility #crush"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#overgiver", "#attachmentstyle", "#numerology",
            "#datingadvice", "#lovecode", "#birthdaycompatibility", "#crush"
        ],
    },
    {
        "id": "short_29",
        "cohort": "Cohort C · Outlier Batch 7 (7.5s Comment Both Days + Visual Demo)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("BIRTH DAYS", "white"),
            ("THAT GO COLD", "coral"),
            ("& SILENT", "gold"),
        ],
        "giant_sub_pill": "BORN 4th · 7th · 8th · 13th · 16th · 17th · 22nd · 25th · 26th · 31st",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_29_7sec_silent_treatment_days.mp4",
        "grid_headline": "BIRTH DAYS THAT\nGO SILENT",
        "grid_sub": "HOW TO FLIP IT",
        "hook_box_text": "Dating someone born on the 4th, 7th, 8th, 13th, 16th, 17th, 22nd, 25th, 26th, or 31st?",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“I'm taking a step back this week because...",
        "spoken_script": (
            "Dating someone born on the 4th, 7th, 8th, 13th, 16th, 17th, 22nd, 25th, 26th, or 31st? "
            "Never chase when they go quiet. "
            "So get their exact text script in our bio."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_06_sofa_back_to_back.mp4"),
            (2.5, 4.6, "emo_02_couple_bed_backs.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Dating someone born on the 4th, 7th, 8th, 13th, 16th, 17th, 22nd, 25th, 26th, or 31st? "
            "Never chase when they go silent—get their exact Flip The Chase text script in our bio 📱💔 "
            "#relationships #textingadvice #silenttreatment #avoidantattachment #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '14 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#textingadvice", "#silenttreatment", "#avoidantattachment",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_30",
        "cohort": "Cohort C · Outlier Batch 7 (7.5s Comment Both Days + Visual Demo)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("ARE YOUR", "white"),
            ("BIRTHDAYS", "gold"),
            ("ENDGAME?", "coral"),
        ],
        "giant_sub_pill": "DAY 19 × DAY 23  •  96% SOULMATE LOCK",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_30_7sec_endgame_birthdays.mp4",
        "grid_headline": "ARE YOUR BIRTHDAYS\nENDGAME?",
        "grid_sub": "96% SOULMATE LOCK",
        "hook_box_text": "Some birthdays are built to last, and some are just a three month lesson.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+25%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "Some birthdays are built to last, but some are just a three month lesson. "
            "Comment both birth days below or test your match free at the link in bio."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_09_couple_forgiveness_hug.mp4"),
            (2.5, 4.6, "emo_10_loving_couple_close.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Are your birthdays endgame—or just a 3-month karmic lesson? "
            "(Comment both birth days below or test your match free at the link in bio) 🔥❤️‍🔥 "
            "#relationships #soulmate #endgame #compatibility #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#soulmate", "#endgame", "#compatibility",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_31",
        "cohort": "Cohort C · Batch 8 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("HE TEXTED DAILY", "white"),
            ("FOR 6 WEEKS", "gold"),
            ("THEN VANISHED", "coral"),
        ],
        "giant_sub_pill": "CRUSH BORN 4th · 7th · 13th · 16th · 22nd · 25th · 31st",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_31_7sec_six_weeks_vanished.mp4",
        "yt_title": "He Texted Daily For 6 Weeks Then Vanished 💔 #Shorts",
        "grid_headline": "HE TEXTED DAILY\nFOR 6 WEEKS\nTHEN VANISHED",
        "grid_sub": "CRUSH BORN 4, 7, 13, 16, 22, 25, 31",
        "hook_box_text": "He texted me every morning for six weeks, then went cold on a Tuesday.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 19th × Born 25th",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved catching up this week, and I...",
        "spoken_script": (
            "He texted me every morning for six weeks, then went cold on a Tuesday. "
            "I blamed myself until I tested his birth day against mine. "
            "Tap our bio before you text him."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_03_couple_silence_apart.mp4"),
            (2.5, 4.6, "emo_01_woman_phone_night.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "He texted me every morning for 6 weeks, then went cold on a Tuesday 💔 "
            "(Crush born 4th, 7th, 13th, 16th, 22nd, 25th, or 31st? Test both birth days free in our bio before you text him) "
            "#relationships #situationship #textingadvice #avoidantattachment #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#situationship", "#textingadvice", "#avoidantattachment",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_32",
        "cohort": "Cohort C · Batch 8 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("LEFT ON READ", "coral"),
            ("AT 11:42 PM?", "gold"),
            ("SEND THIS TEXT", "white"),
        ],
        "giant_sub_pill": "BORN 1st · 5th · 9th · 14th · 18th · 19th · 23rd · 27th · 28th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_32_7sec_read_at_midnight.mp4",
        "yt_title": "Left On Read At Midnight? Send This 9-Word Text 📱 #Shorts",
        "grid_headline": "LEFT ON READ\nAT 11:42 PM?\nSEND THIS TEXT",
        "grid_sub": "9-WORD RESET TEXT",
        "hook_box_text": "When he left me on read at midnight, I almost sent a long paragraph.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“No rush replying—I'm unplugging for the...",
        "spoken_script": (
            "When he left me on read at midnight, I almost sent a long paragraph. "
            "Instead, I used his birth day to send this nine word reset text. "
            "And he called me in ten minutes."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_12_upset_couple_closeup.mp4"),
            (2.5, 4.6, "emo_08_couple_bedroom_tension.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Left on read at 11:42 PM? Instead of sending a long paragraph, I used his birth day to send this 9-word reset text 📱✨ "
            "(Born 1st, 5th, 9th, 14th, 18th, 19th, 23rd, 27th, or 28th—unlock your text script in our bio) "
            "#leftonread #textingadvice #relationships #situationship #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#leftonread", "#textingadvice", "#relationships", "#situationship",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_33",
        "cohort": "Cohort C · Batch 8 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("WHY YOU FALL", "white"),
            ("FOR PEOPLE WHO", "gold"),
            ("PULL AWAY", "coral"),
        ],
        "giant_sub_pill": "BORN 2nd · 3rd · 6th · 11th · 12th · 15th · 20th · 24th · 29th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_33_7sec_wrong_birthday_match.mp4",
        "yt_title": "Why You Always Fall For People Who Pull Away 💔 #Shorts",
        "grid_headline": "WHY YOU FALL\nFOR PEOPLE WHO\nPULL AWAY",
        "grid_sub": "TEST BOTH BIRTH DAYS",
        "hook_box_text": "I spent a year begging for bare minimum attention from someone who could never open up.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 11th × Born 16th",
        "reveal_match_score": "94% PUSH-PULL MAGNET",
        "reveal_sms_lead": "“I really value what we have, so I'm giving...",
        "spoken_script": (
            "I spent a year begging for bare minimum attention from someone who could never open up. "
            "Then I saw why our two birth days clash. "
            "Test both birth days free in our bio."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_04_guy_apologizing_upset_gf.mp4"),
            (2.5, 4.6, "emo_02_couple_bed_backs.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Why you keep falling for people who pull away 💔 "
            "(Born 2nd, 3rd, 6th, 11th, 12th, 15th, 20th, 24th, or 29th? Test both birth days free in our bio to see why your numbers clash) "
            "#relationships #attachmentstyle #anxiousattachment #numerology #datingadvice #situationship #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#attachmentstyle", "#anxiousattachment", "#numerology",
            "#datingadvice", "#situationship", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_34",
        "cohort": "Cohort C · Batch 9 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("WHEN HE ACTS", "white"),
            ("COLD & DISTANT", "coral"),
            ("DO THIS FIRST", "gold"),
        ],
        "giant_sub_pill": "CRUSH BORN 3rd · 7th · 8th · 12th · 16th · 17th · 21st · 25th · 26th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_34_7sec_acting_distant_test.mp4",
        "yt_title": "When He Acts Cold & Distant, Do This First 🥶 #Shorts",
        "grid_headline": "WHEN HE ACTS\nCOLD & DISTANT\nDO THIS FIRST",
        "grid_sub": "CRUSH BORN 3, 7, 8, 12, 16, 17, 21, 25, 26",
        "hook_box_text": "The night he started acting distant, I almost asked him what was wrong.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "The night he started acting distant, I almost asked him what was wrong. "
            "Then I checked his birth day against mine and sent this one line instead. "
            "Test both birth days in our bio."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_02_couple_bed_backs.mp4"),
            (2.5, 4.6, "emo_07_upset_after_argument.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "When he starts acting cold & distant, do NOT ask him 'what's wrong'—send this 1 line instead 🥶📱 "
            "(Crush born 3rd, 7th, 8th, 12th, 16th, 17th, 21st, 25th, or 26th? Test both birth days free in our bio) "
            "#relationships #situationship #textingadvice #actingdistant #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#situationship", "#textingadvice", "#actingdistant",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_35",
        "cohort": "Cohort C · Batch 9 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("BIRTH DAYS THAT", "white"),
            ("BREADCRUMB YOU", "coral"),
            ("FOR MONTHS", "gold"),
        ],
        "giant_sub_pill": "BORN 5th · 9th · 10th · 14th · 18th · 19th · 23rd · 27th · 28th",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_35_7sec_breadcrumbing_days.mp4",
        "yt_title": "Birth Days That Breadcrumb You For Months 💔 #Shorts",
        "grid_headline": "BIRTH DAYS THAT\nBREADCRUMB YOU\nFOR MONTHS",
        "grid_sub": "BREADCRUMBING BIRTH CODE",
        "hook_box_text": "He gave me just enough attention to keep me hooked, but never committed.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 19th × Born 23rd",
        "reveal_match_score": "96% SOULMATE LOCK",
        "reveal_sms_lead": "“Hey, I loved hanging out, but I noticed...",
        "spoken_script": (
            "He gave me just enough attention to keep me hooked, but never committed. "
            "When I ran our two birth days, the warning was right there. "
            "Check your match free in our bio."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_01_woman_phone_night.mp4"),
            (2.5, 4.6, "emo_05_couple_upset_disappointed.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_mandala.png", 99.0),
        ],
        "tiktok_caption": (
            "Birth days that breadcrumb you for months (just enough attention to keep you hooked) 💔 "
            "(Born 5th, 9th, 10th, 14th, 18th, 19th, 23rd, 27th, or 28th? Check your match free in our bio) "
            "#breadcrumbing #situationship #relationships #textingadvice #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#breadcrumbing", "#situationship", "#relationships", "#textingadvice",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
    {
        "id": "short_36",
        "cohort": "Cohort C · Batch 9 (Dr. Plants Micro-Story + SFX)",
        "format_type": "cohort_c_short",
        "visual_format": "emotional_face_giant",
        "giant_lines": [
            ("DO THEY ALWAYS", "white"),
            ("COME BACK", "gold"),
            ("AFTER SILENCE?", "coral"),
        ],
        "giant_sub_pill": "BORN 1st · 2nd · 4th · 6th · 11th · 13th · 15th · 20th · 22nd · 24th · 31st",
        "jenny_hoyos_gate": True,
        "filename": "tiktok_short_36_7sec_who_comes_back.mp4",
        "yt_title": "Why They Always Come Back When You Pull Away 🔥 #Shorts",
        "grid_headline": "DO THEY ALWAYS\nCOME BACK\nAFTER SILENCE?",
        "grid_sub": "PULL-AWAY MAGNET DAYS",
        "hook_box_text": "Every time I pulled my energy back, he suddenly found time to text me.",
        "hook_end_sec": 4.6,
        "cta_tail_sec": 2.8,
        "broll_cutoff": 4.6,
        "tail_hold_sec": 0.25,
        "target_voice_sec": 7.25,
        "voice": "en-US-AvaNeural",
        "rate": "+24%",
        "reveal_match_pair": "Born 11th × Born 16th",
        "reveal_match_score": "94% PUSH-PULL MAGNET",
        "reveal_sms_lead": "“I really value what we have, so I'm giving...",
        "spoken_script": (
            "Every time I pulled my energy back, he suddenly found time to text me. "
            "It all comes down to how your two birth days lock together. "
            "Tap our bio to test both days."
        ),
        "broll_clips": [
            (0.0, 2.5, "emo_08_couple_bedroom_tension.mp4"),
            (2.5, 4.6, "emo_09_couple_forgiveness_hug.mp4"),
        ],
        "product_scenes": [
            ("image", "scenes_cache/scene_relationships.png", 1.5),
            ("image", "scenes_cache/scene_loshu.png", 99.0),
        ],
        "tiktok_caption": (
            "Why they always come back the second you pull your energy away 🔥 "
            "(Born 1st, 2nd, 4th, 6th, 11th, 13th, 15th, 20th, 22nd, 24th, or 31st? Tap our bio to test both birth days) "
            "#relationships #nocontact #situationship #textingadvice #numerology #datingadvice #lovecode #birthdaycompatibility"
        ),
        "first_comment": "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') and I'll reply with your Compatibility % score! 👇",
        "hashtags": [
            "#relationships", "#nocontact", "#situationship", "#textingadvice",
            "#numerology", "#datingadvice", "#lovecode", "#birthdaycompatibility"
        ],
    },
]


BANNED_JENNY_HOYOS_JARGON = {
    "pythagorean", "moolank", "bhagyank", "namank", "sephirot",
    "rosicrucian", "kabbalistic", "navagraha", "babylonian",
}


def count_syllables_word(word: str) -> int:
    import re
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    if w.endswith("es") or w.endswith("ed"):
        if not w.endswith("ted") and not w.endswith("ded") and not w.endswith("ses"):
            w = w[:-2]
    elif w.endswith("e") and not w.endswith("le"):
        w = w[:-1]
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


def compute_flesch_kincaid_grade(text: str) -> float:
    import re
    sentences = [s.strip() for s in re.split(r"[.!?:;]+", text) if s.strip()]
    words = [w for w in re.findall(r"[A-Za-z']+", text) if w]
    if not sentences or not words:
        return 0.0
    total_syllables = sum(count_syllables_word(w) for w in words)
    fk = 0.39 * (len(words) / len(sentences)) + 11.8 * (total_syllables / len(words)) - 15.59
    return round(fk, 2)


def validate_jenny_hoyos_readability(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforces Jenny Hoyos's Viral Shorts Gate:
    1. Flesch-Kincaid Grade Level <= 5.5
    2. Zero banned academic jargon in spoken_script
    3. But/Therefore/Yet twist connector present
    4. Zero-dead-air abrupt payoff (tail_hold_sec <= 0.35)
    """
    script = spec.get("spoken_script", "")
    fk_grade = compute_flesch_kincaid_grade(script)
    lower_words = set(script.lower().replace(",", " ").replace(".", " ").replace("?", " ").split())
    jargon_found = sorted(lower_words.intersection(BANNED_JENNY_HOYOS_JARGON))
    has_twist = any(conn in lower_words for conn in ("but", "therefore", "yet", "so", "until", "instead", "then", "suddenly"))
    tail_hold = float(spec.get("tail_hold_sec", 0.5))

    if fk_grade > 5.5:
        raise ValueError(f"[{spec['id']}] Jenny Hoyos Gate FAILED: Flesch-Kincaid Grade={fk_grade} > 5.5")
    if jargon_found:
        raise ValueError(f"[{spec['id']}] Jenny Hoyos Gate FAILED: Banned jargon found: {jargon_found}")
    if not has_twist:
        raise ValueError(f"[{spec['id']}] Jenny Hoyos Gate FAILED: Missing But/Therefore twist connector")
    if tail_hold > 0.35:
        raise ValueError(f"[{spec['id']}] Jenny Hoyos Gate FAILED: tail_hold_sec={tail_hold} > 0.35s")

    res = {
        "id": spec["id"],
        "fk_grade": fk_grade,
        "jargon_found": jargon_found,
        "has_twist": has_twist,
        "tail_hold_sec": tail_hold,
    }
    print(f"   ✓ [Jenny Hoyos Gate PASSED] [{spec['id']}] FK Grade={fk_grade} (<=5.5) | Twist={has_twist} | Jargon=0 | Tail={tail_hold}s", flush=True)
    return res


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
        self.font_hook_giant = ImageFont.truetype(FONT_BOLD, 68)
        self.font_hook_sub = ImageFont.truetype(FONT_BOLD, 38)
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

    def synthesize_sfx_and_riser_bed(
        self,
        total_dur: float,
        broll_cutoff: float,
        out_sfx_wav: str,
    ) -> None:
        """
        Synthesizes a studio-grade 44.1kHz stereo WAV sound design bed in Python (numpy + wave):
        1. 0.00s (Hook Impact): Subtle warm cinematic sub-bass impact (65Hz-110Hz soft thud, -14dB)
           when the Giant 120px Headline appears.
        2. 1.40s (Emotional Text Trigger): Crisp iMessage 'Sent' swoosh / midnight notification chime (-16dB)
           right when the story mentions texting or being left on read.
        3. 0.00s-4.55s (Tension Riser): Soft, warm heartbeat/pad swell (-24dB rising to -18dB)
           underneath the voiceover that creates emotional suspense.
        4. 4.60s (The Product Reveal Click): Crisp UI lock-pop / camera-shutter sound (-14dB)
           the exact frame the 96% SOULMATE LOCK + Situation Chip + Blurred iMessage Reveal Card
           docks into the lower third.
        """
        import wave

        sr = 44100
        dur_pad = max(total_dur + 0.5, 8.0)
        n_samples = int(dur_pad * sr)
        t_full = np.arange(n_samples, dtype=np.float64) / sr
        mix_l = np.zeros(n_samples, dtype=np.float64)
        mix_r = np.zeros(n_samples, dtype=np.float64)

        def db_to_amp(db: float) -> float:
            return float(10.0 ** (db / 20.0))

        # --- 3. 0.00s-4.55s TENSION RISER (-24dB rising to -18dB) ---
        riser_end = min(4.55, max(2.5, broll_cutoff - 0.05))
        pad_chord = (
            0.40 * np.sin(2.0 * np.pi * 110.0 * t_full)
            + 0.28 * np.sin(2.0 * np.pi * 165.0 * t_full)
            + 0.20 * np.sin(2.0 * np.pi * 220.0 * t_full)
            + 0.12 * np.sin(2.0 * np.pi * 330.0 * t_full)
        )
        # Subtle 75 BPM (1.25Hz) warm heartbeat throb (68Hz sub-pulse)
        hb_phase = (t_full * 1.25) % 1.0
        hb_env = np.exp(-((hb_phase - 0.12) / 0.055) ** 2) + 0.65 * np.exp(-((hb_phase - 0.30) / 0.065) ** 2)
        hb_wave = np.sin(2.0 * np.pi * 68.0 * t_full) * hb_env
        riser_raw = 0.62 * pad_chord + 0.38 * hb_wave
        riser_raw = riser_raw / max(1e-6, float(np.max(np.abs(riser_raw))))

        amp_start = db_to_amp(-24.0)  # 0.0631
        amp_peak = db_to_amp(-18.0)   # 0.1259
        amp_tail = db_to_amp(-24.5)
        env_riser = np.where(
            t_full <= riser_end,
            amp_start + (amp_peak - amp_start) * (t_full / max(0.1, riser_end)),
            amp_tail * np.exp(-np.maximum(0.0, t_full - riser_end) * 0.35),
        )
        # Smooth 0.25s fade-out at total_dur
        fade_mask = np.clip((total_dur - t_full) / 0.25, 0.0, 1.0)
        env_riser = env_riser * fade_mask
        mix_l += riser_raw * env_riser
        mix_r += np.roll(riser_raw, 18) * env_riser

        # --- 1. 0.00s HOOK IMPACT (65Hz-110Hz soft sub-bass thud, -14dB) ---
        imp_dur = 0.46
        imp_n = int(imp_dur * sr)
        t_imp = np.arange(imp_n, dtype=np.float64) / sr
        # Instantaneous frequency sweeping from 110Hz down to 65Hz
        phase_imp = 2.0 * np.pi * (65.0 * t_imp + 45.0 * 0.095 * (1.0 - np.exp(-t_imp / 0.095)))
        imp_wave = 0.78 * np.sin(phase_imp) + 0.22 * np.sin(2.0 * phase_imp)
        imp_attack = np.minimum(1.0, t_imp / 0.010)
        imp_decay = np.exp(-t_imp * 7.8)
        imp_sig = imp_wave * imp_attack * imp_decay
        imp_sig = imp_sig / max(1e-6, float(np.max(np.abs(imp_sig)))) * db_to_amp(-14.0)
        mix_l[:imp_n] += imp_sig
        mix_r[:imp_n] += imp_sig

        # --- 2. 1.40s EMOTIONAL TEXT TRIGGER (iMessage 'Sent' swoosh + midnight chime, -16dB) ---
        trig_t0 = 1.40
        trig_idx0 = int(trig_t0 * sr)
        trig_dur = 0.38
        trig_n = int(trig_dur * sr)
        if trig_idx0 + trig_n < n_samples:
            t_tr = np.arange(trig_n, dtype=np.float64) / sr
            # Part A (0.00s-0.14s): Upward iMessage 'Sent' swoosh (420Hz -> 1240Hz)
            sw_mask = (t_tr <= 0.14).astype(np.float64)
            u_sw = np.clip(t_tr / 0.14, 0.0, 1.0)
            phase_sw = 2.0 * np.pi * (420.0 * t_tr + (820.0 / (2.0 * 0.14)) * (t_tr ** 2))
            swoosh = np.sin(phase_sw) * np.sin(np.pi * u_sw) * sw_mask
            # Part B (0.08s-0.38s): Crisp two-note glassy midnight chime (880Hz A5 -> 1318.5Hz E6)
            t_ch = np.maximum(0.0, t_tr - 0.08)
            ch_mask = (t_tr >= 0.08).astype(np.float64)
            ch_att = np.minimum(1.0, t_ch / 0.006)
            ch_dec = np.exp(-t_ch * 13.5)
            chime = (0.55 * np.sin(2.0 * np.pi * 880.0 * t_ch) + 0.45 * np.sin(2.0 * np.pi * 1318.5 * t_ch)) * ch_att * ch_dec * ch_mask
            trig_sig = 0.52 * swoosh + 0.68 * chime
            trig_sig = trig_sig / max(1e-6, float(np.max(np.abs(trig_sig)))) * db_to_amp(-16.0)
            mix_l[trig_idx0 : trig_idx0 + trig_n] += trig_sig * 0.95
            mix_r[trig_idx0 : trig_idx0 + trig_n] += trig_sig * 1.05

        # --- 4. 4.60s PRODUCT REVEAL CLICK (UI lock-pop / camera-shutter sound, -14dB) ---
        rev_t0 = float(broll_cutoff if broll_cutoff <= 6.2 else 4.60)
        rev_idx0 = int(rev_t0 * sr)
        rev_dur = 0.16
        rev_n = int(rev_dur * sr)
        if rev_idx0 + rev_n < n_samples:
            t_rv = np.arange(rev_n, dtype=np.float64) / sr
            # Transient 1 (0.00s): Tactile shutter click (1800Hz -> 620Hz)
            click1 = (
                0.65 * np.sin(2.0 * np.pi * (620.0 * t_rv + 1180.0 * 0.012 * (1.0 - np.exp(-t_rv / 0.012))))
                + 0.35 * np.sin(2.0 * np.pi * 2400.0 * t_rv)
            ) * np.exp(-t_rv * 55.0)
            # Transient 2 (0.036s): Warm UI lock-pop harmonic snap (1046Hz C6 + 1568Hz G6)
            t_rv2 = np.maximum(0.0, t_rv - 0.036)
            m2 = (t_rv >= 0.036).astype(np.float64)
            pop2 = (
                0.60 * np.sin(2.0 * np.pi * 1046.5 * t_rv2)
                + 0.40 * np.sin(2.0 * np.pi * 1568.0 * t_rv2)
            ) * np.minimum(1.0, t_rv2 / 0.004) * np.exp(-t_rv2 * 32.0) * m2
            rev_sig = 0.65 * click1 + 0.75 * pop2
            rev_sig = rev_sig / max(1e-6, float(np.max(np.abs(rev_sig)))) * db_to_amp(-14.0)
            mix_l[rev_idx0 : rev_idx0 + rev_n] += rev_sig
            mix_r[rev_idx0 : rev_idx0 + rev_n] += rev_sig

        stereo = np.stack([mix_l, mix_r], axis=-1)
        stereo_i16 = np.clip(stereo * 32767.0, -32767, 32767).astype(np.int16)
        with wave.open(out_sfx_wav, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(stereo_i16.tobytes())
        print(
            f"   [SFX] Synthesized 4-layer sound design bed (0.00s -14dB Sub-Impact | 1.40s -16dB iMessage Chime | 0.00-{riser_end:.2f}s -24->-18dB Riser | {rev_t0:.2f}s -14dB Reveal Lock-Pop)",
            flush=True,
        )

    def mix_audio_with_subtle_pad(
        self,
        voice_path: str,
        out_mixed_path: str,
        cues: List[Dict[str, Any]],
        tail_hold_sec: float = 1.2,
        target_voice_sec: Optional[float] = None,
        broll_cutoff: float = 4.60,
    ) -> float:
        """
        Mixes the spoken story with the 4-layer studio sound design bed (SFX + Tension Riser)
        and `tail_hold_sec` tail hold.
        If `target_voice_sec` is specified and raw voice exceeds it, gently speeds up voice & cues
        via FFmpeg `atempo` so Cohort C shorts stay strictly on target (~7.5s).
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
            tempo = min(1.55, max(1.0, v_dur / target_voice_sec))
            for c in cues:
                c["start"] = c["start"] / tempo
                c["end"] = c["end"] / tempo
            v_dur = v_dur / tempo
            print(f"   [TTS] Applied pace tempo={tempo:.3f}x -> voice={v_dur:.2f}s (+{tail_hold_sec:.1f}s tail)", flush=True)

        total_est_dur = v_dur + tail_hold_sec
        amb_path = voice_path + "_sfx_bed.wav"
        self.synthesize_sfx_and_riser_bed(total_est_dur, broll_cutoff=broll_cutoff, out_sfx_wav=amb_path)

        atempo_filter = f"atempo={tempo:.4f}," if tempo > 1.001 else ""
        filter_complex = (
            f"[0:a]{atempo_filter}apad=pad_dur={tail_hold_sec:.2f}[vpad];"
            f"[vpad]volume=1.0[v];"
            f"[1:a]volume=1.0[bg];"
            f"[v][bg]amix=inputs=2:duration=first:dropout_transition=0:weights=1 1:normalize=0"
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

    def draw_giant_emotional_headline(
        self,
        frame: Image.Image,
        spec: Dict[str, Any],
        compact_top: bool = False,
    ) -> Image.Image:
        """
        Renders massive 115px-130px ultra-bold uppercase stacked headline across Y = 260..700
        over a full-bleed emotional human face/couple frame:
        - Soft dark top vignette gradient strictly behind Y = 0..760 so human faces in the
          middle/lower-middle third stay 100% bright and expressive.
        - Thick 8px black outline + heavy drop shadow.
        - Color-highlights emotional trigger words in vibrant Gold (#FFE14D) or
          Heartbreak Red/Coral (#FF4757) against Pure White (#FFFFFF).
        """
        arr = np.array(frame, dtype=np.float32)
        vig_h = 540 if compact_top else 760
        ramp = np.ones((1920, 1, 1), dtype=np.float32)
        ramp[:240, 0, 0] = 0.40
        ramp[240:vig_h, 0, 0] = np.linspace(0.40, 1.0, vig_h - 240, dtype=np.float32)
        arr = np.clip(arr * ramp, 0, 255).astype(np.uint8)
        frame = Image.fromarray(arr)
        draw = ImageDraw.Draw(frame)

        heavy_font_path = r"C:\Windows\Fonts\ariblk.ttf"
        if not os.path.exists(heavy_font_path):
            heavy_font_path = r"C:\Windows\Fonts\impact.ttf"
        if not os.path.exists(heavy_font_path):
            heavy_font_path = FONT_BOLD

        color_map = {
            "white": (255, 255, 255),
            "gold": (255, 225, 77),
            "coral": (255, 71, 87),
        }

        giant_lines = spec.get("giant_lines") or [
            ("WHY HE", "white"),
            ("PULLS AWAY", "coral"),
            ("BY BIRTH DAY", "gold"),
        ]

        cx = 540
        curr_y = 185 if compact_top else 285
        line_step = 116 if compact_top else 130
        size_candidates = (116, 110, 104, 98, 92, 86, 80) if compact_top else (130, 124, 118, 112, 106, 100, 94, 88, 82)

        for line_txt, col_key in giant_lines:
            txt_up = line_txt.strip().upper()
            fill_rgb = color_map.get(col_key, (255, 255, 255))
            # Auto-fit between 130px down to 82px so the line spans ~85% of the 1080px width (<= 965px)
            font_line = ImageFont.truetype(heavy_font_path, size_candidates[-1])
            for f_sz in size_candidates:
                cand = ImageFont.truetype(heavy_font_path, f_sz)
                bbox = draw.textbbox((0, 0), txt_up, font=cand, stroke_width=8)
                w = bbox[2] - bbox[0]
                if w <= 965:
                    font_line = cand
                    break

            # Heavy black drop shadow + 8px black stroke
            draw.text(
                (cx + 6, curr_y + 8),
                txt_up,
                fill=(0, 0, 0),
                font=font_line,
                anchor="mm",
                stroke_width=10,
                stroke_fill=(0, 0, 0),
            )
            draw.text(
                (cx, curr_y),
                txt_up,
                fill=fill_rgb,
                font=font_line,
                anchor="mm",
                stroke_width=8,
                stroke_fill=(0, 0, 0),
            )
            curr_y += line_step

        sub_pill = spec.get("giant_sub_pill")
        if sub_pill and not compact_top:
            f_pill = ImageFont.truetype(FONT_BOLD, 27)
            pill_y = curr_y - 34
            draw.rounded_rectangle(
                [56, pill_y - 30, 1024, pill_y + 30],
                radius=18,
                fill=(12, 13, 20),
                outline=(255, 225, 77),
                width=3,
            )
            draw.text((cx, pill_y), sub_pill, fill=(255, 225, 77), font=f_pill, anchor="mm")

        return frame

    def draw_native_tiktok_hook_box(
        self,
        draw: ImageDraw.ImageDraw,
        hook_text: str,
        grid_headline: Optional[str] = None,
        grid_sub: Optional[str] = None,
    ):
        """
        Draws an authentic native TikTok white rounded-rectangle text box sticker
        centered in the upper-middle safe zone (y ~ 360).
        When `grid_headline` is provided, renders a GIANT 68px bold 3-to-6 word Poster Headline
        with an optional 38px compact subtitle line below it so the 3-column profile grid is
        100% readable at a glance.
        """
        if grid_headline:
            h_lines = [ln.strip() for ln in grid_headline.split("\n") if ln.strip()]
            font_h = self.font_hook_giant
            for f_sz in (68, 64):
                font_h = self.font_hook_giant if f_sz == 68 else ImageFont.truetype(FONT_BOLD, f_sz)
                widths = [draw.textbbox((0, 0), ln, font=font_h)[2] - draw.textbbox((0, 0), ln, font=font_h)[0] for ln in h_lines]
                if max(widths) <= 910:
                    break
            h_widths = [draw.textbbox((0, 0), ln, font=font_h)[2] - draw.textbbox((0, 0), ln, font=font_h)[0] for ln in h_lines]
            line_h = 80
            sub_h = 54 if grid_sub else 0
            sub_w = (draw.textbbox((0, 0), grid_sub, font=self.font_hook_sub)[2] - draw.textbbox((0, 0), grid_sub, font=self.font_hook_sub)[0]) if grid_sub else 0

            max_w = max(max(h_widths), sub_w)
            total_h = len(h_lines) * line_h + sub_h

            cx, cy = 540, 370
            pad_x, pad_y = 38, 28
            x0 = max(36, cx - max_w // 2 - pad_x)
            y0 = cy - total_h // 2 - pad_y
            x1 = min(1044, cx + max_w // 2 + pad_x)
            y1 = cy + total_h // 2 + pad_y

            # Strong drop shadow behind the white TikTok poster sticker
            draw.rounded_rectangle(
                [x0 + 6, y0 + 8, x1 + 6, y1 + 8],
                radius=26,
                fill=(0, 0, 0),
            )
            # Crisp white rounded-rectangle poster card with subtle gold accent border
            draw.rounded_rectangle(
                [x0, y0, x1, y1],
                radius=26,
                fill=(255, 255, 255),
                outline=(212, 175, 55),
                width=4,
            )

            curr_y = y0 + pad_y + line_h // 2 - 4
            for ln in h_lines:
                draw.text((cx, curr_y), ln, fill=(12, 12, 16), font=font_h, anchor="mm")
                curr_y += line_h

            if grid_sub:
                sub_y = curr_y - line_h // 2 + 30
                draw.text((cx, sub_y), grid_sub, fill=(168, 28, 48), font=self.font_hook_sub, anchor="mm")
            return

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

    def draw_capcut_caption(self, draw: ImageDraw.ImageDraw, cue_text: str, cy: int = 1320):
        """
        Renders 56px bold white text with thick black stroke (width=5) and drop shadow
        at y=cy (default 1320, or 1072 during lower-third reveal dock), highlighting at most
        1 power word per phrase in warm gold (#FFD147).
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

        cx = 540
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
        'Tap @sacrednumberblueprint (Link in Bio)'
        'Test Both Birthdays Free → Blueprint.MegaVegaVentures.com'
        """
        line1 = "Tap @sacrednumberblueprint (Link in Bio)"
        line2 = "Test Both Birthdays Free → Blueprint.MegaVegaVentures.com"

        cx, cy = 540, 1620
        w_box, h_box = 980, 140
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
        f_sub = ImageFont.truetype(FONT_BOLD, 25)
        draw.text((cx, cy - 24), line1, fill=(255, 209, 71), font=self.font_cta_main, anchor="mm")
        draw.text((cx, cy + 25), line2, fill=(245, 245, 247), font=f_sub, anchor="mm")

    def draw_imessage_match_reveal_card(self, frame: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Upgrades the 7.5s video reveal phase (4.6s-7.5s) to visually display:
        1) Dark-mode Partner Match Card ('Born 19th × Born 23rd -> 96% SOULMATE LOCK')
        2) 1-Tap Situation Chip Strip (#situation-chip-strip: '[📱 Left me on read]' lit in gold,
           '[🥶 Acting cold]', '[💔 Pulled away]') right above the blurred iMessage bubble
        3) iMessage 'Flip The Chase' Text Script Bubble (first line visible + Gaussian-blurred secret text)
        4) Plain 5th-Grade Gold Lock CTA:
           '🔒 Unlock Full Text + Best & Worst Days To Text ($17) — Link in Bio'
        """
        is_emo_giant = spec.get("visual_format") == "emotional_face_giant"
        if is_emo_giant:
            frame = self.draw_giant_emotional_headline(frame, spec, compact_top=False)
            draw = ImageDraw.Draw(frame)
            f_pair = ImageFont.truetype(FONT_BOLD, 28)
            f_chip = ImageFont.truetype(FONT_BOLD, 20)
            f_sms_txt = ImageFont.truetype(FONT_BOLD, 26)
            f_lock = ImageFont.truetype(FONT_BOLD, 22)
            emoji_font_path = r"C:\Windows\Fonts\seguiemj.ttf"
            f_emoji = ImageFont.truetype(emoji_font_path, 20) if os.path.exists(emoji_font_path) else f_chip

            pair_txt = spec.get("reveal_match_pair", "Born 19th × Born 23rd")
            score_txt = spec.get("reveal_match_score", "96% SOULMATE LOCK")

            # Lower-Third Compact Match + Situation Chips + Blurred iMessage Dock (Y = 1138..1538)
            draw.rounded_rectangle([48, 1138, 1032, 1538], radius=24, fill=(12, 14, 20), outline=(212, 175, 55), width=3)

            # Row 1: Partner Match Score Bar (Y = 1152..1206)
            draw.rounded_rectangle([76, 1152, 1004, 1206], radius=14, fill=(20, 44, 32), outline=(74, 222, 128), width=2)
            draw.text((540, 1179), f"{pair_txt}  →  {score_txt}", fill=(110, 245, 165), font=f_pair, anchor="mm")

            # Row 2: 1-Tap Situation Selector Pills (#situation-chip-strip, Y = 1216..1266)
            chips = [
                ("📱", "Left me on read", True, 76, 404),
                ("🥶", "Acting cold", False, 416, 704),
                ("💔", "Pulled away", False, 716, 1004),
            ]
            for emj, lbl, is_active, cx0, cx1 in chips:
                bg_c = (52, 40, 14) if is_active else (22, 26, 36)
                bd_c = (255, 215, 77) if is_active else (88, 98, 122)
                tx_c = (255, 225, 88) if is_active else (210, 218, 235)
                draw.rounded_rectangle([cx0, 1216, cx1, 1266], radius=14, fill=bg_c, outline=bd_c, width=2 if is_active else 1)
                mid_x = (cx0 + cx1) // 2
                try:
                    draw.text((cx0 + 20, 1241), emj, fill=tx_c, font=f_emoji, anchor="lm", embedded_color=True)
                    draw.text((mid_x + 14, 1241), lbl, fill=tx_c, font=f_chip, anchor="mm")
                except Exception:
                    draw.text((mid_x, 1241), lbl, fill=tx_c, font=f_chip, anchor="mm")

            # Row 3: iMessage speech bubble with 1 clear line + 1 blurred secret line (Y = 1276..1442)
            draw.rounded_rectangle([76, 1276, 1004, 1442], radius=18, fill=(24, 38, 58), outline=(96, 165, 250), width=2)
            sms_lead = spec.get("reveal_sms_lead", "“Hey, I loved hanging out, but I noticed...")
            draw.text((108, 1316), sms_lead, fill=(255, 255, 255), font=f_sms_txt, anchor="lm")

            secret_box = (102, 1350, 976, 1432)
            secret_img = frame.crop(secret_box)
            s_draw = ImageDraw.Draw(secret_img)
            s_draw.text((8, 34), "our pace works best when neither of us forces it.”", fill=(225, 235, 250), font=f_sms_txt, anchor="lm")
            secret_blurred = secret_img.filter(ImageFilter.GaussianBlur(radius=6))
            frame.paste(secret_blurred, (secret_box[0], secret_box[1]))

            # Row 4: Gold 5th-Grade Unlock CTA Button (Y = 1454..1524)
            draw = ImageDraw.Draw(frame)
            draw.rounded_rectangle([76, 1454, 1004, 1524], radius=16, fill=(212, 175, 55), outline=(255, 235, 150), width=2)
            # Vector padlock icon + 5th-grade button text:
            # "🔒 Unlock Full Text + Best & Worst Days To Text ($17) — Link in Bio"
            draw.arc([104, 1473, 120, 1491], start=180, end=0, fill=(18, 15, 8), width=3)
            draw.rounded_rectangle([101, 1486, 123, 1505], radius=3, fill=(18, 15, 8))
            draw.text(
                (554, 1489),
                "Unlock Full Text + Best & Worst Days To Text ($17) — Link in Bio",
                fill=(18, 15, 8),
                font=f_lock,
                anchor="mm",
            )
            return frame

        frame = ImageEnhance.Brightness(frame).enhance(0.30)
        draw = ImageDraw.Draw(frame)

        f_badge = ImageFont.truetype(FONT_BOLD, 24)
        f_pair = ImageFont.truetype(FONT_BOLD, 35)
        f_score = ImageFont.truetype(FONT_BOLD, 32)
        f_day = ImageFont.truetype(FONT_BOLD, 24)
        f_sms_hdr = ImageFont.truetype(FONT_BOLD, 25)
        f_sms_txt = ImageFont.truetype(FONT_BOLD, 31)
        f_lock = ImageFont.truetype(FONT_BOLD, 24)

        y_shift = 0

        # --- CARD 1: PARTNER MATCH CARD ---
        draw.rounded_rectangle(
            [58, 165 + y_shift, 1022, 535 + y_shift],
            radius=28,
            fill=(14, 16, 22),
            outline=(212, 175, 55),
            width=4,
        )
        draw.text(
            (540, 208 + y_shift),
            "1-TAP PARTNER & CRUSH BIRTHDAY MATCH",
            fill=(243, 229, 171),
            font=f_badge,
            anchor="mm",
        )

        pair_txt = spec.get("reveal_match_pair", "Born 19th × Born 23rd")
        score_txt = spec.get("reveal_match_score", "96% SOULMATE LOCK")
        draw.text((540, 268 + y_shift), f"{pair_txt}  →  {score_txt}", fill=(255, 255, 255), font=f_pair, anchor="mm")

        draw.rounded_rectangle(
            [110, 314 + y_shift, 970, 392 + y_shift],
            radius=20,
            fill=(20, 44, 32),
            outline=(74, 222, 128),
            width=3,
        )
        draw.text((540, 353 + y_shift), f"{score_txt} · HIGH INITIAL PULL", fill=(110, 245, 165), font=f_score, anchor="mm")

        # Mini 1-Tap Birth Day Grid row inside Match Card
        days_demo = ["2", "7", "11", "14", "16", "*19*", "*23*", "25", "29"]
        bx0 = 102
        bw = 88
        bgap = 10
        for idx, d_lbl in enumerate(days_demo):
            dx0 = bx0 + idx * (bw + bgap)
            dx1 = dx0 + bw
            is_sel = "*" in d_lbl
            clean_lbl = d_lbl.replace("*", "")
            draw.rounded_rectangle(
                [dx0, 422 + y_shift, dx1, 502 + y_shift],
                radius=14,
                fill=(212, 175, 55) if is_sel else (26, 28, 36),
                outline=(255, 225, 110) if is_sel else (110, 95, 45),
                width=3 if is_sel else 2,
            )
            draw.text(
                ((dx0 + dx1) // 2, 462 + y_shift),
                clean_lbl,
                fill=(18, 15, 8) if is_sel else (243, 229, 171),
                font=f_day,
                anchor="mm",
            )

        # --- CARD 2: iMESSAGE "FLIP THE CHASE" TEXT SCRIPT BUBBLE ---
        draw.rounded_rectangle(
            [58, 560 + y_shift, 1022, 1155 + y_shift],
            radius=28,
            fill=(11, 13, 19),
            outline=(96, 165, 250),
            width=3,
        )
        draw.text(
            (540, 608 + y_shift),
            "YOUR \"FLIP THE CHASE\" TEXT SCRIPT (iMessage):",
            fill=(255, 209, 71),
            font=f_sms_hdr,
            anchor="mm",
        )

        # iMessage blue/slate speech bubble
        draw.rounded_rectangle(
            [94, 648 + y_shift, 986, 978 + y_shift],
            radius=24,
            fill=(24, 38, 58),
            outline=(96, 165, 250),
            width=2,
        )
        sms_lead = spec.get("reveal_sms_lead", "“Hey, I loved hanging out, but I noticed...")
        draw.text((130, 704 + y_shift), sms_lead, fill=(255, 255, 255), font=f_sms_txt, anchor="lm")

        # Render 2 realistic secret SMS lines and apply Gaussian blur so it looks like frosted glass
        secret_box = (120, 752 + y_shift, 960, 956 + y_shift)
        secret_img = frame.crop(secret_box)
        s_draw = ImageDraw.Draw(secret_img)
        s_draw.text((10, 40), "our pace works best when neither of us forces it.", fill=(225, 235, 250), font=f_sms_txt, anchor="lm")
        s_draw.text((10, 108), "Reach out next week when your head is clear.”", fill=(225, 235, 250), font=f_sms_txt, anchor="lm")
        secret_blurred = secret_img.filter(ImageFilter.GaussianBlur(radius=7))
        frame.paste(secret_blurred, (secret_box[0], secret_box[1]))

        # Glowing Gold Lock Button inside Card 2 (with drawn vector padlock icon)
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle(
            [94, 1004 + y_shift, 986, 1122 + y_shift],
            radius=20,
            fill=(212, 175, 55),
            outline=(255, 235, 150),
            width=3,
        )
        draw.arc([141, 1042 + y_shift, 159, 1062 + y_shift], start=180, end=0, fill=(18, 15, 8), width=3)
        draw.rounded_rectangle([137, 1057 + y_shift, 163, 1080 + y_shift], radius=4, fill=(18, 15, 8))
        draw.text(
            (558, 1063 + y_shift),
            "Tap Link in Bio to Test Both Birthdays & Unlock Your Script",
            fill=(18, 15, 8),
            font=f_lock,
            anchor="mm",
        )
        return frame

    def draw_format_a_imessage_thread(self, frame: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Format A — Native Dark-Mode iMessage Story ('imessage_thread'):
        Frame 0 (and 0.0s..hook_end_sec) opens on a crisp, high-contrast iMessage thread
        ('Delivered · Read 1:14 AM' + emotional text exchange + bold neon-gold/crimson header pill)
        that looks like a real phone screenshot, with mean_luma >= 55.
        """
        theme = spec.get("imessage_theme", "blue_crimson")
        # Bright frosted-slate iOS dark mode background so mean_luma >= 60
        frame = ImageEnhance.Brightness(frame).enhance(0.55)
        overlay = Image.new("RGBA", (1080, 1920), (22, 26, 38, 215) if theme == "blue_crimson" else (28, 24, 34, 215))
        frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(frame)

        f_hdr = ImageFont.truetype(FONT_BOLD, 62)
        f_sub = ImageFont.truetype(FONT_BOLD, 32)
        f_contact = ImageFont.truetype(FONT_BOLD, 28)
        f_msg = ImageFont.truetype(FONT_BOLD, 34)
        f_stat = ImageFont.truetype(FONT_BOLD, 25)
        f_pill = ImageFont.truetype(FONT_BOLD, 27)

        # 1. Top Bold Header Pill (Crimson or Royal Gold)
        hdr_bg = (165, 24, 48) if theme == "blue_crimson" else (180, 125, 20)
        hdr_border = (255, 209, 71) if theme == "blue_crimson" else (110, 245, 165)
        draw.rounded_rectangle([46, 115, 1034, 355], radius=28, fill=hdr_bg, outline=hdr_border, width=4)
        h_lines = [ln.strip() for ln in (spec.get("grid_headline") or "DO THEY MISS YOU?").split("\n") if ln.strip()]
        cy_h = 185 if len(h_lines) > 1 else 210
        for ln in h_lines:
            draw.text((540, cy_h), ln, fill=(255, 255, 255), font=f_hdr, anchor="mm")
            cy_h += 72
        if spec.get("grid_sub"):
            draw.rounded_rectangle([260, 298, 820, 344], radius=16, fill=(18, 18, 26))
            draw.text((540, 321), spec["grid_sub"], fill=(255, 215, 90), font=f_sub, anchor="mm")

        # 2. Phone Screen Container (y=380..1195)
        draw.rounded_rectangle([46, 380, 1034, 1195], radius=34, fill=(32, 36, 48), outline=(95, 110, 140), width=3)
        # iOS Contact Header Bar
        draw.rounded_rectangle([50, 384, 1030, 480], radius=30, fill=(44, 50, 66))
        draw.ellipse([498, 392, 582, 444], fill=(212, 175, 55))
        draw.text((540, 418), "19×23", fill=(16, 16, 22), font=f_stat, anchor="mm")
        draw.text((540, 462), "iMessage · Today 1:14 AM", fill=(210, 220, 238), font=f_contact, anchor="mm")

        # Incoming Gray Bubble (left-aligned)
        inc_txt = spec.get("imessage_incoming", "I just need some space to figure my head out right now...")
        inc_lines = textwrap.wrap(inc_txt, width=35)
        draw.rounded_rectangle([82, 505, 865, 675], radius=26, fill=(64, 70, 88), outline=(110, 120, 145), width=2)
        iy = 552
        for ln in inc_lines[:2]:
            draw.text((115, iy), ln, fill=(250, 252, 255), font=f_msg, anchor="lm")
            iy += 48

        # Outgoing Blue Bubble (right-aligned)
        out_txt = spec.get("imessage_outgoing", "Did I do something wrong? Why did you go completely quiet?")
        out_lines = textwrap.wrap(out_txt, width=35)
        bubble_col = (14, 118, 254) if theme == "blue_crimson" else (22, 138, 98)
        draw.rounded_rectangle([205, 705, 998, 880], radius=26, fill=bubble_col, outline=(145, 205, 255), width=2)
        oy = 752
        for ln in out_lines[:2]:
            draw.text((238, oy), ln, fill=(255, 255, 255), font=f_msg, anchor="lm")
            oy += 48

        # Delivered · Read status
        stat_txt = spec.get("imessage_status", "Delivered · Read 1:14 AM")
        draw.text((985, 912), stat_txt, fill=(255, 125, 145), font=f_stat, anchor="rm")

        # Bottom Highlighted Birth-Day Callout Card inside iMessage Window
        days_pill = spec.get("imessage_days_pill", "BORN 2nd · 6th · 7th · 11th · 15th · 16th · 20th · 24th · 25th")
        draw.rounded_rectangle([78, 955, 1002, 1165], radius=24, fill=(22, 25, 34), outline=(255, 209, 71), width=3)
        draw.text((540, 1012), "TARGET BIRTH DAYS IN THIS READING:", fill=(255, 209, 71), font=f_stat, anchor="mm")
        draw.rounded_rectangle([104, 1052, 976, 1138], radius=18, fill=(245, 238, 215))
        draw.text((540, 1095), days_pill, fill=(20, 18, 28), font=f_pill, anchor="mm")
        return frame

    def draw_format_b_birthday_matrix(self, frame: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Format B — Interactive Birth-Day Matrix Spotlight ('birthday_matrix'):
        Frame 0 (and 0.0s..hook_end_sec) opens on a luxury dark-velvet & gold 1–31 Birth-Day
        Calendar Grid with the hook's target birth days glowing in emerald/crimson (mean_luma >= 55).
        """
        frame = ImageEnhance.Brightness(frame).enhance(0.60)
        overlay = Image.new("RGBA", (1080, 1920), (34, 24, 48, 210))
        frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(frame)

        f_hdr = ImageFont.truetype(FONT_BOLD, 64)
        f_sub = ImageFont.truetype(FONT_BOLD, 30)
        f_day = ImageFont.truetype(FONT_BOLD, 36)
        f_foot = ImageFont.truetype(FONT_BOLD, 27)

        # 1. Luxury Gold/Emerald Header Card (y=115..355)
        draw.rounded_rectangle([46, 115, 1034, 355], radius=28, fill=(28, 56, 48), outline=(212, 175, 55), width=4)
        h_lines = [ln.strip() for ln in (spec.get("grid_headline") or "3 LOVE DATES\nTO WATCH NEXT").split("\n") if ln.strip()]
        cy_h = 182 if len(h_lines) > 1 else 210
        for ln in h_lines:
            draw.text((540, cy_h), ln, fill=(255, 248, 225), font=f_hdr, anchor="mm")
            cy_h += 72
        draw.rounded_rectangle([230, 295, 850, 342], radius=16, fill=(212, 175, 55))
        draw.text((540, 319), spec.get("grid_sub", "YOUR 90-DAY LOVE CALENDAR"), fill=(18, 15, 10), font=f_sub, anchor="mm")

        # 2. 1–31 Birth-Day Calendar Matrix Card (y=380..1195)
        draw.rounded_rectangle([46, 380, 1034, 1195], radius=32, fill=(42, 36, 58), outline=(212, 175, 55), width=3)
        draw.text((540, 428), "SPOTLIGHT BIRTH DAYS (1–31) · FIND YOUR NUMBER:", fill=(255, 220, 115), font=f_sub, anchor="mm")

        target_days = set(spec.get("matrix_days", [3, 4, 8, 9, 12, 13, 17, 18, 21, 22, 26, 27, 30, 31]))
        cols = 7
        tile_w, tile_h = 116, 108
        gap_x, gap_y = 16, 18
        grid_w = cols * tile_w + (cols - 1) * gap_x
        start_x = (1080 - grid_w) // 2
        start_y = 472

        for day_num in range(1, 32):
            idx = day_num - 1
            r = idx // cols
            c = idx % cols
            x0 = start_x + c * (tile_w + gap_x)
            y0 = start_y + r * (tile_h + gap_y)
            x1 = x0 + tile_w
            y1 = y0 + tile_h
            is_hit = day_num in target_days
            if is_hit:
                # Alternate Emerald and Crimson-Gold spotlight tiles
                fill_c = (18, 155, 105) if (day_num % 2 == 1) else (215, 65, 90)
                out_c = (255, 235, 140)
                txt_c = (255, 255, 255)
            else:
                fill_c = (72, 66, 92)
                out_c = (120, 112, 145)
                txt_c = (215, 210, 230)
            draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=fill_c, outline=out_c, width=3 if is_hit else 2)
            draw.text(((x0 + x1) // 2, (y0 + y1) // 2), str(day_num), fill=txt_c, font=f_day, anchor="mm")

        # Footer callout inside Matrix card
        draw.rounded_rectangle([78, 1102, 1002, 1172], radius=18, fill=(245, 238, 218))
        draw.text((540, 1137), "• Glowing Birth Days Enter a Major 14-Day Love Shift This Week", fill=(24, 18, 32), font=f_foot, anchor="mm")
        return frame

    def draw_format_c_editorial_broll(self, frame: Image.Image, spec: Dict[str, Any]) -> Image.Image:
        """
        Format C — Editorial Magazine Typography over Bright, Unique B-Roll ('editorial_broll'):
        Uses a bright, never-before-used lifestyle clip (mean_luma >= 90) with full-width editorial
        typography (icy-blue/crimson/gold accents — zero white rectangle box!).
        """
        draw = ImageDraw.Draw(frame)
        f_badge = ImageFont.truetype(FONT_BOLD, 28)
        f_hdr = ImageFont.truetype(FONT_BOLD, 74)
        f_sub = ImageFont.truetype(FONT_BOLD, 34)
        f_ribbon = ImageFont.truetype(FONT_BOLD, 26)

        # Top Icy-Blue / Obsidian Pill Badge (y=135..198)
        badge_txt = spec.get("editorial_badge", "SILENT TREATMENT DECODER · DAYS 1–31")
        draw.rounded_rectangle([120, 135, 960, 198], radius=30, fill=(14, 24, 38), outline=(56, 189, 248), width=3)
        draw.text((540, 166), badge_txt, fill=(125, 211, 252), font=f_badge, anchor="mm")

        # Full-Width Stacked Magazine Headline with heavy stroke & dual-tone colors (y=245..395)
        h_lines = [ln.strip() for ln in (spec.get("grid_headline") or "BIRTH DAYS THAT\nGO SILENT").split("\n") if ln.strip()]
        line_colors = [(255, 255, 255), (255, 209, 71), (255, 92, 138)]
        cy = 255
        for idx, ln in enumerate(h_lines):
            col = line_colors[idx % len(line_colors)]
            draw.text((544, cy + 5), ln, fill=(0, 0, 0), font=f_hdr, anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
            draw.text((540, cy), ln, fill=col, font=f_hdr, anchor="mm", stroke_width=7, stroke_fill=(12, 14, 22))
            cy += 88

        # Crimson Editorial Subtitle Pill
        if spec.get("grid_sub"):
            draw.rounded_rectangle([270, cy - 22, 810, cy + 36], radius=18, fill=(175, 24, 52), outline=(255, 215, 110), width=3)
            draw.text((540, cy + 7), spec["grid_sub"], fill=(255, 255, 255), font=f_sub, anchor="mm")
            cy += 78

        # Bottom Target Birth-Days Ribbon
        days_rib = spec.get("editorial_days_pill", "BORN 4th · 7th · 8th · 13th · 16th · 17th · 22nd · 25th · 26th · 31st")
        draw.rounded_rectangle([54, cy - 10, 1026, cy + 54], radius=18, fill=(16, 18, 28), outline=(255, 209, 71), width=2)
        draw.text((540, cy + 22), days_rib, fill=(255, 238, 180), font=f_ribbon, anchor="mm")
        return frame

    def verify_and_record_broll_registry(self, spec: Dict[str, Any]):
        """Enforces Strict Zero-Reuse B-Roll Registry (used_broll_registry.json) + Brightness Gate (mean_luma >= 55)."""
        reg_path = os.path.join(BASE_DIR, "used_broll_registry.json")
        reg = {"history": []}
        if os.path.exists(reg_path):
            try:
                reg = json.load(open(reg_path, encoding="utf-8"))
            except Exception:
                reg = {"history": []}

        primary_clip = spec["broll_clips"][0][2]
        clip_path = os.path.join(BROLL_DIR, primary_clip)
        cap = cv2.VideoCapture(clip_path)
        ret, bgr = cap.read()
        cap.release()
        mean_luma = float(np.mean(bgr)) if ret else 0.0
        if mean_luma < 55.0:
            raise ValueError(f"[{spec['id']}] Brightness Gate FAILED on {primary_clip}: mean_luma={mean_luma:.1f} < 55.0")

        # Check last 15 videos in history (excluding current spec['id'])
        recent = [h for h in reg.get("history", []) if h.get("id") != spec["id"]][-15:]
        recent_clips = {h.get("primary_clip") for h in recent}
        if primary_clip in recent_clips:
            raise ValueError(f"[{spec['id']}] Zero-Reuse Gate FAILED: {primary_clip} was already used in recent videos {recent_clips}")

        reg["history"] = [h for h in reg.get("history", []) if h.get("id") != spec["id"]] + [
            {
                "id": spec["id"],
                "visual_format": spec.get("visual_format", "legacy"),
                "primary_clip": primary_clip,
                "mean_luma": round(mean_luma, 1),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        ]
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=2)
        print(
            f"   ✓ [Anti-Slop B-Roll Gate PASSED] [{spec['id']}] format={spec.get('visual_format', 'legacy')} | clip={primary_clip} | luma={mean_luma:.1f} (>=55)",
            flush=True,
        )

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
        broll_cutoff = float(spec.get("broll_cutoff", 7.5 if is_short else 15.0))

        print(
            f"\n[RENDER] Building {spec['filename']} ({total_dur:.2f}s, {total_frames} frames, format={spec.get('format_type')}, visual_format={spec.get('visual_format', 'legacy')})...",
            flush=True,
        )
        if spec.get("visual_format"):
            self.verify_and_record_broll_registry(spec)

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
            v_fmt = spec.get("visual_format", "legacy")
            if t < broll_cutoff:
                active_broll = spec["broll_clips"][-1][2]
                local_t = t
                for b_start, b_end, b_fname in spec["broll_clips"]:
                    if b_start <= t < b_end:
                        active_broll = b_fname
                        local_t = t - b_start
                        break
                d_ratio = 1.00 if v_fmt == "emotional_face_giant" else 0.84
                frame = broll_readers[active_broll].get_frame(local_t, darken_ratio=d_ratio)
                if v_fmt == "emotional_face_giant":
                    # Warm, vibrant color grade (especially in the first 1.5s to stop early swipe-aways)
                    sat_boost = 1.20 if t <= 1.5 else 1.12
                    frame = ImageEnhance.Color(frame).enhance(sat_boost)
                    arr_w = np.array(frame, dtype=np.float32)
                    arr_w[:, :, 0] = np.clip(arr_w[:, :, 0] * 1.05 + 4.0, 0, 255)
                    arr_w[:, :, 1] = np.clip(arr_w[:, :, 1] * 1.02 + 2.0, 0, 255)
                    arr_w[:, :, 2] = np.clip(arr_w[:, :, 2] * 0.96, 0, 255)
                    if float(np.mean(arr_w)) < 88.0:
                        lift = 88.0 / max(20.0, float(np.mean(arr_w)))
                        arr_w = np.clip(arr_w * lift, 0, 255)
                    frame = Image.fromarray(arr_w.astype(np.uint8))
            elif is_short:
                if v_fmt == "emotional_face_giant":
                    active_broll = spec["broll_clips"][-1][2]
                    frame = broll_readers[active_broll].get_frame(t - broll_cutoff, darken_ratio=0.95)
                    frame = ImageEnhance.Color(frame).enhance(1.10)
                    frame = self.draw_imessage_match_reveal_card(frame, spec)
                else:
                    # Cohort C (broll_cutoff -> end): Fast dynamic zoom reveal across the 2 dossier scenes
                    reveal_dur = max(1.0, total_dur - broll_cutoff)
                    mid_t = broll_cutoff + (reveal_dur * 0.48)
                    if t < mid_t or len(p_imgs) == 1:
                        img_key = p_imgs[0]
                        u = max(0.0, min(1.0, (t - broll_cutoff) / max(0.5, mid_t - broll_cutoff)))
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
                    if broll_cutoff <= 5.0:
                        frame = self.draw_imessage_match_reveal_card(frame, spec)
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
                if broll_cutoff <= 5.0:
                    frame = self.draw_imessage_match_reveal_card(frame, spec)

            draw = ImageDraw.Draw(frame)

            # 2. Visual Format Hook (0.0s - hook_end_sec)
            if t <= hook_end_sec:
                if v_fmt == "emotional_face_giant":
                    if t < broll_cutoff:
                        frame = self.draw_giant_emotional_headline(frame, spec, compact_top=False)
                        draw = ImageDraw.Draw(frame)
                elif v_fmt == "imessage_thread":
                    frame = self.draw_format_a_imessage_thread(frame, spec)
                    draw = ImageDraw.Draw(frame)
                elif v_fmt == "birthday_matrix":
                    frame = self.draw_format_b_birthday_matrix(frame, spec)
                    draw = ImageDraw.Draw(frame)
                elif v_fmt == "editorial_broll":
                    frame = self.draw_format_c_editorial_broll(frame, spec)
                    draw = ImageDraw.Draw(frame)
                else:
                    self.draw_native_tiktok_hook_box(
                        draw,
                        spec["hook_box_text"],
                        grid_headline=spec.get("grid_headline"),
                        grid_sub=spec.get("grid_sub"),
                    )

            # 3. Center 3-Word CapCut-Style Captions Throughout
            active_cue_text = None
            while cue_idx < len(cues) and cues[cue_idx]["end"] < t:
                cue_idx += 1
            if cue_idx < len(cues) and cues[cue_idx]["start"] <= t <= cues[cue_idx]["end"]:
                active_cue_text = cues[cue_idx]["text"]

            if active_cue_text:
                cap_cy = 1072 if (v_fmt == "emotional_face_giant" and t >= broll_cutoff) else 1320
                self.draw_capcut_caption(draw, active_cue_text, cy=cap_cy)

            # 4. Closing Call-to-Action Pill
            if t >= (total_dur - cta_tail_sec):
                self.draw_final_5s_cta_pill(draw)

            if f_idx == 0:
                f0_path = os.path.join(BASE_DIR, f"frame0_{spec['id']}.png")
                frame.save(f0_path, format="PNG")
                f0_luma = float(np.mean(np.array(frame)))
                print(f"   ✓ Saved Frame-0 cover: {f0_path} (mean_luma={f0_luma:.1f})", flush=True)

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
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0
        vid_dur = (frame_count / fps) if fps > 0 else 14.0
        saved = []
        if vid_dur <= 8.5:
            checkpoints = [(1.5, "2s_hook"), (3.5, "5s_broll"), (6.0, "10s_reveal")]
        elif is_short:
            checkpoints = [(2.0, "2s_hook"), (5.5, "5s_broll"), (10.5, "10s_reveal")]
        else:
            checkpoints = [(2.0, "2s_hook"), (8.0, "8s_broll"), (20.0, "20s_reveal")]
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
                "yt_title": spec.get("yt_title", ""),
                "hook_name": spec["hook_box_text"],
                "lang": "en",
                "voice": spec["voice"],
                "rate": spec["rate"],
                "spoken_script": spec["spoken_script"],
                "flesch_kincaid_grade": compute_flesch_kincaid_grade(spec["spoken_script"]),
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
            if spec.get("jenny_hoyos_gate"):
                validate_jenny_hoyos_readability(spec)
            cues = await self.generate_voice_and_3word_cues(
                spec["spoken_script"], spec["voice"], spec["rate"], v_mp3
            )
            dur = self.mix_audio_with_subtle_pad(
                v_mp3,
                m_mp3,
                cues=cues,
                tail_hold_sec=spec.get("tail_hold_sec", 0.5 if is_short else 1.2),
                target_voice_sec=spec.get("target_voice_sec"),
                broll_cutoff=float(spec.get("broll_cutoff", 4.60)),
            )
            self.render_video(spec, cues, m_mp3, dur, out_mp4)

            for tmp in (v_mp3, m_mp3):
                if os.path.exists(tmp):
                    os.remove(tmp)

            # Copy to root, tiktok_videos, Google Drive tiktok_queue, and Artifacts
            shutil.copy2(out_mp4, os.path.join(BASE_DIR, fname))
            tt_vids_dir = os.path.join(BASE_DIR, "tiktok_videos")
            if os.path.exists(tt_vids_dir):
                shutil.copy2(out_mp4, os.path.join(tt_vids_dir, fname))
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
