#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · 45-SECOND 16:9 YOUTUBE VSL WALKTHROUGH &
SHORTS "RELATED VIDEO" CLICKABLE BRIDGE AUTOMATION
build_and_publish_yt_vsl_bridge.py
-----------------------------------------------------------------------------
1. Renders a 45-second 16:9 (1920x1080) standard YouTube video:
   `videos/yt_channel_vsl_walkthrough.mp4`
   Why 16:9? YouTube disables clickable links in Shorts comments/descriptions,
   but 100% ENABLES clickable links in standard 16:9 video descriptions and
   pinned comments—and lets every Short link directly to a 16:9 video via the
   native `Related video` pill right above the Short's title!
2. Uploads the 16:9 VSL video LIVE to @sacrednumberblueprint with clickable
   link `https://blueprint.megavegaventures.com/?utm_source=yt_vsl&cohort=pinned`
   at the top of the description AND in the pinned comment.
3. Links our top YouTube Shorts (`short_35`, `short_24`, `short_31`, `short_32`,
   `short_37`, `short_43`, `short_44`, `short_45`) to this 16:9 VSL via the
   `Related video` (`ytcp-video-metadata-related-video`) field in YouTube Studio.
=============================================================================
"""

import argparse
import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import sys
import wave
from datetime import datetime
from typing import Any, Dict, List, Optional

import edge_tts
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright, Page

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
AVATARS_DIR = os.path.join(BASE_DIR, "podcast_avatars")
YT_CHANNEL_ID = "UCBIWSA7ZBuBEP_9rj3uSfqA"
TRACKER_PATH = os.path.join(BASE_DIR, "uploaded_yt_shorts.json")

VSL_FILENAME = "yt_channel_vsl_walkthrough.mp4"
VSL_TITLE = "How To Test Both Birth Days (1–31) & Decode Their Last Text Free 💔📲"
VSL_CLICKABLE_URL = "https://blueprint.megavegaventures.com/?utm_source=yt_vsl&cohort=pinned"
VSL_DESCRIPTION = (
    f"👉 TEST BOTH BIRTH DAYS (1–31) & SEE YOUR TEXT SCRIPT HERE:\n"
    f"{VSL_CLICKABLE_URL}\n\n"
    "Why do they pull away right when you get close? 💔 In this 45-second walkthrough, "
    "Maya & Julian show you how to:\n"
    "1️⃣ Tap YOUR Birth Day (1–31) and THEIR Birth Day (1–31) to see your exact "
    "Compatibility % Score across 5 ancient systems.\n"
    "2️⃣ Tap what they just did (Left me on read, Acting cold, Pulled away fast, or "
    "Stubborn silence) or paste their last text to decode their hidden motive.\n"
    "3️⃣ Unblur your custom \"Flip The Chase\" text script and see the 3 best days to "
    "text them this month!\n\n"
    f"👇 Tap here to run your 2-birthday match right now:\n{VSL_CLICKABLE_URL}"
)
VSL_PINNED_COMMENT = (
    f"📌 CLICK HERE To Test Both Birth Days (1–31) & Unblur Your \"Flip The Chase\" "
    f"Text Script: {VSL_CLICKABLE_URL} 💔📲 (Or drop both birth days below like '19 & 23'!)"
)

TARGET_SHORTS_FOR_RELATED_LINK = [
    ("short_35", "BtPMMrR85Bs"),
    ("short_43", "XbNVIjb4eBo"),
    ("short_44", "XYtxS5vllUE"),
    ("short_45", "A1QCTI8JKYg"),
    ("short_24", "9jgH8Hssjw8"),
    ("short_31", "IOFdayPUpoA"),
    ("short_32", "2NEQkRMDARQ"),
    ("short_37", "OVz7TSxgygk"),
]

VSL_SEGMENTS = [
    {
        "speaker": "maya",
        "voice": "en-US-AvaNeural",
        "rate": "+8%",
        "pitch": "+2Hz",
        "step_badge": "STEP 1 OF 3 · TAP BOTH BIRTH DAYS (1–31)",
        "headline": "CAME FROM OUR SHORTS?\nTEST BOTH BIRTH DAYS IN 10 SECONDS",
        "bullets": [
            "1. Click the blue link in the description or pinned comment below",
            "2. Tap YOUR Birth Day (1–31) on the top strip",
            "3. Tap HIS Birth Day (1–31) right underneath",
        ],
        "text": (
            "Came here from our Shorts? Here is how to test both birth days in ten seconds, "
            "using the clickable link right below this video in the description and pinned comment."
        ),
    },
    {
        "speaker": "julian",
        "voice": "en-US-AndrewNeural",
        "rate": "+9%",
        "pitch": "-2Hz",
        "step_badge": "STEP 1 OF 3 · INSTANT 5-SYSTEM MATCH SCORE",
        "headline": "DAY 19 × DAY 23 → 96%\nSOULMATE LOCK REVEALED",
        "bullets": [
            "✓ Checks all 5 ancient systems (Vedic, Lo Shu, Chaldean, Western, Kabbalah)",
            "✓ Reveals his Birth-Day Driver (#1–#9) & hidden attachment blindspot",
            "✓ Shows your exact Chemistry % and Unresolved Friction Risk",
        ],
        "text": (
            "Step one: tap your birth day from one to thirty-one, and tap his birth day right underneath. "
            "You'll immediately see your five-system compatibility score, like Day nineteen and Day twenty-three at ninety-six percent."
        ),
    },
    {
        "speaker": "maya",
        "voice": "en-US-AvaNeural",
        "rate": "+8%",
        "pitch": "+2Hz",
        "step_badge": "STEP 2 OF 3 · SITUATION CHIPS & TEXT DECODER",
        "headline": "TAP WHAT HE JUST DID OR\nPASTE HIS LAST TEXT MESSAGE",
        "bullets": [
            "📱 Tap: Left me on read · Acting cold · Pulled away fast · Stubborn silence",
            "💬 Or paste the exact text he sent you into the Crush Text Decoder",
            "🧠 Instantly see Julian's male-insider psychological translation",
        ],
        "text": (
            "Step two: tap what he just did—left you on read, acting cold, pulled away fast, or stubborn silence—"
            "or paste his exact last text message into the decoder box."
        ),
    },
    {
        "speaker": "julian",
        "voice": "en-US-AndrewNeural",
        "rate": "+9%",
        "pitch": "-2Hz",
        "step_badge": "STEP 3 OF 3 · UNBLUR YOUR TEXT SCRIPT",
        "headline": "UNBLUR YOUR 'FLIP THE CHASE'\nSCRIPT & 3 BEST DAYS TO TEXT",
        "bullets": [
            "🔓 Enter your email to unblur Part 1 & his #1 Secret Fear free",
            "📋 Unlock the full word-for-word text script + what he'll reply",
            "📅 Plus the 3 Best & Worst Days to text him this month!",
        ],
        "text": (
            "Step three: unblur your custom Flip The Chase text script, plus the three best and worst days to text him this month. "
            "Tap the blue link in the description or pinned comment right now to run yours free."
        ),
    },
]


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            r"C:\Windows\Fonts\ariblk.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
        ]
        if bold
        else [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]
    )
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


async def capture_live_funnel_screenshots(out_dir: str) -> List[str]:
    """Captures 3 crisp mobile UI screenshots of blueprint.megavegaventures.com for the 16:9 VSL."""
    os.makedirs(out_dir, exist_ok=True)
    paths = [
        os.path.join(out_dir, "vsl_step1_hero.png"),
        os.path.join(out_dir, "vsl_step2_decoder.png"),
        os.path.join(out_dir, "vsl_step3_script.png"),
    ]
    if all(os.path.exists(p) and os.path.getsize(p) > 10000 for p in paths):
        return paths

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 412, "height": 820}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto("https://blueprint.megavegaventures.com/?utm_source=yt_vsl", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(0.6)
        await page.click('#quick-day-strip button[data-action="quick-day"][data-day="19"]')
        await asyncio.sleep(0.4)
        await page.screenshot(path=paths[0])

        await page.click('#hero-partner-day-strip button[data-action="hero-partner-day"][data-day="23"]')
        await page.wait_for_selector("#view-teaser:not(.hidden)", timeout=8000)
        await asyncio.sleep(0.5)
        await page.locator("#situation-chip-strip").scroll_into_view_if_needed()
        await asyncio.sleep(0.3)
        await page.fill("#crush-last-text-input", "sorry been super busy this week")
        await page.click("#btn-decode-crush-text")
        await asyncio.sleep(0.4)
        await page.screenshot(path=paths[1])

        await page.locator("#flip-chase-preview-bubble").scroll_into_view_if_needed()
        await asyncio.sleep(0.4)
        await page.screenshot(path=paths[2])
        await browser.close()
    return paths


async def synthesize_vsl_audio(out_wav: str) -> List[Dict[str, Any]]:
    """Synthesizes the 4-segment Maya x Julian walkthrough audio with subtle studio SFX."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_version() and imageio_ffmpeg.get_ffmpeg_exe()
    temp_dir = os.path.join(VIDEOS_DIR, "_vsl_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    seg_timings: List[Dict[str, Any]] = []
    pcm_chunks: List[np.ndarray] = []
    sr = 24000
    cur_t = 0.0

    for idx, seg in enumerate(VSL_SEGMENTS):
        mp3_p = os.path.join(temp_dir, f"seg_{idx}.mp3")
        wav_p = os.path.join(temp_dir, f"seg_{idx}.wav")
        comm = edge_tts.Communicate(seg["text"], seg["voice"], rate=seg["rate"], pitch=seg["pitch"])
        await comm.save(mp3_p)
        subprocess.run(
            [ffmpeg_exe, "-y", "-i", mp3_p, "-ac", "1", "-ar", str(sr), "-f", "wav", wav_p],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        with wave.open(wav_p, "rb") as wf:
            raw = wf.readframes(wf.getnframes())
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

        # Trim leading/trailing silence
        abs_s = np.abs(samples)
        non_silent = np.where(abs_s > 220)[0]
        if len(non_silent) > 10:
            s_i = max(0, non_silent[0] - int(0.04 * sr))
            e_i = min(len(samples), non_silent[-1] + int(0.08 * sr))
            samples = samples[s_i:e_i]

        # Add a 0.18s studio pause between segments
        pause = np.zeros(int(0.18 * sr), dtype=np.float32)
        chunk = np.concatenate([samples, pause])
        dur = len(chunk) / sr
        seg_timings.append({
            "index": idx,
            "start": cur_t,
            "end": cur_t + dur,
            "duration": dur,
            **seg,
        })
        pcm_chunks.append(chunk)
        cur_t += dur

    full_voice = np.concatenate(pcm_chunks)
    total_samples = len(full_voice)
    t_axis = np.arange(total_samples, dtype=np.float32) / sr

    # Warm ambient late-night studio pad + transition chimes at segment boundaries
    bed = 320.0 * np.sin(2 * np.pi * 65.0 * t_axis) + 180.0 * np.sin(2 * np.pi * 130.0 * t_axis)
    for st in seg_timings:
        idx0 = int(st["start"] * sr)
        chime_len = min(int(0.28 * sr), total_samples - idx0)
        if chime_len > 0:
            ct = np.arange(chime_len, dtype=np.float32) / sr
            env = np.exp(-ct * 12.0)
            chime = 2200.0 * env * (np.sin(2 * np.pi * 880.0 * ct) + 0.5 * np.sin(2 * np.pi * 1320.0 * ct))
            bed[idx0 : idx0 + chime_len] += chime

    mixed = np.clip(full_voice + bed, -32767, 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(mixed.tobytes())

    return seg_timings


def render_vsl_video() -> str:
    """Renders the 1920x1080 16:9 YouTube VSL walkthrough MP4."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    temp_dir = os.path.join(VIDEOS_DIR, "_vsl_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    shots = asyncio.run(capture_live_funnel_screenshots(temp_dir))
    wav_path = os.path.join(temp_dir, "vsl_master.wav")
    seg_timings = asyncio.run(synthesize_vsl_audio(wav_path))
    total_dur = seg_timings[-1]["end"]
    print(f"  ✓ Synthesized 4-segment Maya × Julian VSL audio: {total_dur:.2f}s", flush=True)

    W, H = 1920, 1080
    fps = 24
    total_frames = int(math.ceil(total_dur * fps))

    # Load avatars and UI screenshots
    maya_av = Image.open(os.path.join(BASE_DIR, "maya_avatar_128.png")).convert("RGBA").resize((116, 116), Image.Resampling.LANCZOS)
    julian_av = Image.open(os.path.join(BASE_DIR, "julian_avatar_128.png")).convert("RGBA").resize((116, 116), Image.Resampling.LANCZOS)
    ui_imgs = [Image.open(p).convert("RGB").resize((460, 860), Image.Resampling.LANCZOS) for p in shots]

    f_badge = load_font(24, bold=True)
    f_h1 = load_font(52, bold=True)
    f_bullet = load_font(28, bold=False)
    f_host_name = load_font(28, bold=True)
    f_host_role = load_font(20, bold=False)
    f_cta_bar = load_font(32, bold=True)
    f_sub = load_font(34, bold=True)

    out_mp4 = os.path.join(VIDEOS_DIR, VSL_FILENAME)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", wav_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_mp4,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for f_idx in range(total_frames):
        t = f_idx / fps
        active_seg = seg_timings[-1]
        for s in seg_timings:
            if s["start"] <= t <= s["end"]:
                active_seg = s
                break

        seg_idx = active_seg["index"]
        speaker = active_seg["speaker"]
        ui_idx = 0 if seg_idx in (0, 1) else (1 if seg_idx == 2 else 2)

        img = Image.new("RGB", (W, H), (11, 11, 16))
        draw = ImageDraw.Draw(img)

        # Top studio pill
        draw.rounded_rectangle((70, 42, 1160, 102), radius=30, fill=(24, 20, 36), outline=(212, 175, 55), width=2)
        draw.text((98, 57), f"🎙️ LATE NIGHT TRUTH PODCAST  ·  {active_seg['step_badge']}", font=f_badge, fill=(255, 225, 77))

        # Host cards (Maya & Julian)
        for h_idx, (h_key, h_name, h_role, av_im, hx) in enumerate([
            ("maya", "MAYA", "Host · Late Night Truth", maya_av, 70),
            ("julian", "JULIAN", "Numerology & Relationship Expert", julian_av, 630),
        ]):
            is_speaking = (speaker == h_key)
            bg_col = (30, 25, 44) if is_speaking else (18, 18, 25)
            border_col = (255, 225, 77) if is_speaking else (70, 70, 88)
            bw = 4 if is_speaking else 1
            draw.rounded_rectangle((hx, 128, hx + 530, 276), radius=24, fill=bg_col, outline=border_col, width=bw)
            img.paste(av_im, (hx + 20, 144), av_im)
            draw.text((hx + 152, 152), h_name, font=f_host_name, fill=(255, 225, 77) if is_speaking else (210, 210, 220))
            draw.text((hx + 152, 190), h_role, font=f_host_role, fill=(180, 180, 195))
            # Animated studio waveform bars
            for b_i in range(14):
                bx = hx + 154 + b_i * 24
                if is_speaking:
                    bh = int(10 + 18 * abs(math.sin(t * 11.0 + b_i * 0.7)))
                    b_col = (52, 211, 153) if h_key == "julian" else (255, 225, 77)
                else:
                    bh = 4
                    b_col = (80, 80, 95)
                draw.rounded_rectangle((bx, 244 - bh, bx + 14, 248), radius=4, fill=b_col)

        # Headline block
        y_cursor = 310
        for line_i, h_line in enumerate(active_seg["headline"].split("\n")):
            col = (255, 255, 255) if line_i == 0 else (255, 225, 77)
            draw.text((70, y_cursor), h_line, font=f_h1, fill=col)
            y_cursor += 66

        # Step bullets card
        draw.rounded_rectangle((70, 465, 1160, 735), radius=24, fill=(18, 19, 27), outline=(212, 175, 55), width=2)
        by = 492
        for bul in active_seg["bullets"]:
            draw.text((100, by), bul, font=f_bullet, fill=(243, 229, 171))
            by += 74

        # Live spoken caption box
        draw.rounded_rectangle((70, 760, 1160, 915), radius=20, fill=(28, 22, 42), outline=(120, 100, 180), width=2)
        words = active_seg["text"].split()
        rel_p = max(0.0, min(0.999, (t - active_seg["start"]) / max(0.1, active_seg["duration"])))
        w_pos = int(rel_p * len(words))
        chunk_start = (w_pos // 10) * 10
        sub_words = words[chunk_start : chunk_start + 10]
        l1 = " ".join(sub_words[:5])
        l2 = " ".join(sub_words[5:10])
        draw.text((100, 788), f"“{l1}", font=f_sub, fill=(255, 255, 255))
        if l2:
            draw.text((100, 840), f"{l2}”", font=f_sub, fill=(255, 225, 77))

        # Right-hand Mobile Frame (X = 1260..1760)
        px, py = 1270, 42
        draw.rounded_rectangle((px - 14, py - 14, px + 460 + 14, py + 860 + 14), radius=38, fill=(24, 24, 32), outline=(212, 175, 55), width=4)
        img.paste(ui_imgs[ui_idx], (px, py))

        # Bottom Full-Width Clickable Link Pointer Banner
        pulse = int(15 * abs(math.sin(t * 5.0)))
        draw.rounded_rectangle(
            (70, 945, 1850, 1045),
            radius=24,
            fill=(28 + pulse, 45 + pulse, 34),
            outline=(52, 211, 153),
            width=4,
        )
        draw.text(
            (115, 976),
            "👇 CLICK THE LINK IN THE DESCRIPTION OR PINNED COMMENT BELOW: blueprint.megavegaventures.com 👇",
            font=f_cta_bar,
            fill=(255, 255, 255),
        )

        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()

    if os.path.exists(GDRIVE_QUEUE_DIR):
        try:
            shutil.copy2(out_mp4, os.path.join(GDRIVE_QUEUE_DIR, VSL_FILENAME))
        except Exception:
            pass
    print(f"  ✓ Rendered 16:9 YouTube VSL video -> {out_mp4} ({os.path.getsize(out_mp4)/(1024*1024):.2f} MB)", flush=True)
    return out_mp4


async def upload_vsl_and_link_related_shorts(vsl_mp4_path: str, existing_vsl_id: str = ""):
    """Uploads the 16:9 VSL to YouTube Studio, pins the clickable link comment, and wires Related Video on top Shorts."""
    from yt_shorts_auto_uploader import (
        YT_PROFILE_DIR,
        prepare_cloned_profile6_userdata,
        load_tracker,
        save_tracker,
    )

    tracker = load_tracker()
    cdp_userdata = prepare_cloned_profile6_userdata()
    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_proc = None

    async with async_playwright() as p:
        browser = None
        ctx = None
        if os.path.exists(chrome_exe):
            try:
                chrome_proc = subprocess.Popen(
                    [
                        chrome_exe,
                        "--remote-debugging-port=9222",
                        f"--user-data-dir={cdp_userdata}",
                        "--profile-directory=Profile 6",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--window-size=1400,920",
                        f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                for _ in range(10):
                    await asyncio.sleep(1.0)
                    try:
                        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=5000)
                        break
                    except Exception:
                        pass
                if browser:
                    ctx = browser.contexts[0] if browser.contexts else await browser.new_context(viewport={"width": 1400, "height": 920})
                    print("  ✓ [CDP] Attached directly to real Google Chrome (Profile 6) over http://127.0.0.1:9222", flush=True)
            except Exception as e:
                print(f"  [CDP Notice] Fallback to persistent context ({e})", flush=True)

        if ctx is None:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=YT_PROFILE_DIR,
                channel="chrome",
                headless=False,
                viewport={"width": 1400, "height": 920},
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled"],
            )

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        page.set_default_timeout(15000)
        try:
            await page.set_viewport_size({"width": 1400, "height": 920})
        except Exception:
            pass

        try:
            studio_home = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}"
            print(f"  [YT Auth] Navigating to {studio_home} ...", flush=True)
            await page.goto(studio_home, wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(3.5)
            if "accounts.google.com" in page.url or "signin" in page.url.lower():
                print(f"  ✗ Not logged into YouTube Studio ({page.url}). Exiting fast.", flush=True)
                return
            print(f"  ✓ [YT Auth] Authenticated in YouTube Studio: {page.url}", flush=True)

            vsl_vid = existing_vsl_id or tracker.get("vsl_bridge_video_id", "")
            if not vsl_vid:
                # Check if already present in Studio Videos tab before uploading
                await page.goto(f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/upload", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(4.0)
                found_existing = await page.evaluate(
                    """() => {
                        const rows = Array.from(document.querySelectorAll('ytcp-video-row'));
                        for (const r of rows) {
                            const txt = (r.innerText || '').toLowerCase();
                            if (txt.includes('how to test both birth days')) {
                                const a = r.querySelector('a[href*="/video/"]');
                                if (a) {
                                    const m = a.href.match(/\\/video\\/([A-Za-z0-9_-]{11})/);
                                    if (m) return m[1];
                                }
                            }
                        }
                        return '';
                    }"""
                )
                if found_existing:
                    vsl_vid = found_existing
                    print(f"  ✓ [YT VSL Check] Found existing 16:9 VSL in Studio: {vsl_vid}", flush=True)
                    tracker["vsl_bridge_video_id"] = vsl_vid
                    tracker["vsl_bridge_url"] = f"https://www.youtube.com/watch?v={vsl_vid}"
                    save_tracker(tracker)

            if not vsl_vid:
                studio_url = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/upload?d=ud"
                print(f"\n  [YT VSL Upload] Uploading 16:9 VSL: {VSL_TITLE}", flush=True)
                await page.goto(studio_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.5)

                file_input = page.locator('input[type="file"]').first
                if await file_input.count() == 0:
                    create_btn = page.locator('ytcp-button#create-icon, button:has-text("Create")').first
                    if await create_btn.count() > 0:
                        await create_btn.click(force=True)
                        await asyncio.sleep(1.0)
                        up_item = page.locator('tp-yt-paper-item:has-text("Upload videos")').first
                        if await up_item.count() > 0:
                            await up_item.click(force=True)
                            await asyncio.sleep(1.5)

                await page.locator('input[type="file"]').first.set_input_files(vsl_mp4_path)
                await asyncio.sleep(6.5)

                try:
                    dialog_txt = await page.inner_text("ytcp-uploads-dialog")
                    m = re.search(r"(?:youtu\.be/|youtube\.com/watch\?v=|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})", dialog_txt)
                    if m:
                        vsl_vid = m.group(1)
                except Exception:
                    pass

                boxes = page.locator("ytcp-social-suggestions-textbox #textbox, div#textbox[contenteditable='true']")
                if await boxes.count() >= 1:
                    tbox = boxes.nth(0)
                    await tbox.click(force=True)
                    await page.keyboard.press("Control+A")
                    await tbox.fill(VSL_TITLE[:100])
                    await asyncio.sleep(0.5)
                if await boxes.count() >= 2:
                    dbox = boxes.nth(1)
                    await dbox.click(force=True)
                    await page.keyboard.press("Control+A")
                    await dbox.fill(VSL_DESCRIPTION)
                    await asyncio.sleep(0.5)

                not_kids = page.locator(
                    'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], tp-yt-paper-radio-button:has-text("No, it\'s not made for kids")'
                ).first
                if await not_kids.count() > 0:
                    await not_kids.scroll_into_view_if_needed()
                    await not_kids.click(force=True)
                    await asyncio.sleep(0.6)

                for _ in range(3):
                    next_btn = page.locator("ytcp-button#next-button").first
                    if await next_btn.count() > 0 and await next_btn.is_visible():
                        await next_btn.click(force=True)
                        await asyncio.sleep(1.6)

                if not vsl_vid:
                    try:
                        dialog_txt = await page.inner_text("ytcp-uploads-dialog")
                        m = re.search(r"(?:youtu\.be/|youtube\.com/watch\?v=|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})", dialog_txt)
                        if m:
                            vsl_vid = m.group(1)
                    except Exception:
                        pass

                pub_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"], tp-yt-paper-radio-button:has-text("Public")').first
                if await pub_radio.count() > 0:
                    await pub_radio.click(force=True)
                    await asyncio.sleep(0.8)

                done_btn = page.locator("ytcp-button#done-button").first
                if await done_btn.count() > 0:
                    await done_btn.click(force=True)
                    await asyncio.sleep(5.5)

                print(f"  ✓ [YT VSL Upload] Published 16:9 VSL Live -> https://www.youtube.com/watch?v={vsl_vid}", flush=True)
                tracker["vsl_bridge_video_id"] = vsl_vid
                tracker["vsl_bridge_url"] = f"https://www.youtube.com/watch?v={vsl_vid}"
                save_tracker(tracker)

                if vsl_vid:
                    watch_url = f"https://www.youtube.com/watch?v={vsl_vid}"
                    print(f"  [YT VSL Seed] Opening {watch_url} to seed & pin clickable-link comment...", flush=True)
                    await page.goto(watch_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(5.0)
                    await page.evaluate("window.scrollBy(0, 600)")
                    await asyncio.sleep(2.5)
                    placeholder = page.locator("#simplebox-placeholder, ytd-comment-simplebox-renderer #placeholder-area").first
                    if await placeholder.count() > 0 and await placeholder.is_visible():
                        await placeholder.click(force=True)
                        await asyncio.sleep(0.8)
                    box = page.locator("#contenteditable-root, div[contenteditable='true'][aria-label*='comment' i]").first
                    if await box.count() > 0:
                        await box.click(force=True)
                        await box.fill(VSL_PINNED_COMMENT)
                        await asyncio.sleep(0.6)
                        submit_btn = page.locator("ytd-button-renderer#submit-button button, button[aria-label='Comment']").first
                        if await submit_btn.count() > 0:
                            await submit_btn.click(force=True)
                            await asyncio.sleep(3.5)
                            print(f"    ✓ Posted clickable-link comment on {vsl_vid}", flush=True)
                    try:
                        threads = page.locator("ytd-comment-thread-renderer")
                        if await threads.count() > 0:
                            th = threads.first
                            menu_btn = th.locator("ytd-menu-renderer button, button[aria-label='Action menu']").first
                            if await menu_btn.count() > 0:
                                await menu_btn.click(force=True)
                                await asyncio.sleep(0.8)
                                pin_item = page.locator("ytd-menu-navigation-item-renderer:has-text('Pin'), tp-yt-paper-item:has-text('Pin')").first
                                if await pin_item.count() > 0:
                                    await pin_item.click(force=True)
                                    await asyncio.sleep(0.8)
                                    confirm_pin = page.locator("yt-confirm-dialog-renderer #confirm-button button, button:has-text('Pin')").last
                                    if await confirm_pin.count() > 0 and await confirm_pin.is_visible():
                                        await confirm_pin.click(force=True)
                                        await asyncio.sleep(2.0)
                                    print(f"    ✓ Pinned clickable-link comment on {vsl_vid}!", flush=True)
                    except Exception as e:
                        print(f"    [YT VSL Pin Notice] {e}", flush=True)

            print(f"\n  [YT Studio Related Video] Wiring Related Video ({vsl_vid}) across {len(TARGET_SHORTS_FOR_RELATED_LINK)} Shorts...", flush=True)
            linked_shorts = tracker.setdefault("related_video_linked", {})
            for short_key, short_vid in TARGET_SHORTS_FOR_RELATED_LINK:
                if linked_shorts.get(short_key) == vsl_vid:
                    print(f"    ✓ [{short_key}] ({short_vid}) already linked to {vsl_vid}, skipping.", flush=True)
                    continue
                edit_url = f"https://studio.youtube.com/video/{short_vid}/edit"
                await page.goto(edit_url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.5)

                clicked_rel = await page.evaluate(
                    """() => {
                        const relEl = document.querySelector('ytcp-video-metadata-related-video, #related-video');
                        if (relEl) {
                            relEl.scrollIntoView({block: 'center'});
                            const trigger = relEl.querySelector('ytcp-dropdown-trigger, button, #trigger, .dropdown-trigger-text, div.compact-row') || relEl;
                            trigger.click();
                            return 'relEl';
                        }
                        const els = Array.from(document.querySelectorAll('ytcp-button, div, span'));
                        for (const s of els) {
                            if ((s.innerText || '').trim() === 'Related video') {
                                s.scrollIntoView({block: 'center'});
                                s.click();
                                return 'textMatch';
                            }
                        }
                        return '';
                    }"""
                )
                await asyncio.sleep(2.5)
                if clicked_rel:
                    search_inp = page.locator('ytcp-video-pick-dialog input, tp-yt-paper-dialog input[type="text"], input[placeholder*="Search" i], #search-input input').first
                    if await search_inp.count() > 0 and await search_inp.is_visible():
                        await search_inp.fill("How To Test Both Birth Days")
                        await asyncio.sleep(2.2)

                    picked = await page.evaluate(
                        """() => {
                            const cards = Array.from(document.querySelectorAll('ytcp-entity-card, ytcp-video-row, .entity-card, [role="option"], tp-yt-paper-item, div.video-Card, ytcp-video-pick-dialog div'));
                            for (const c of cards) {
                                const txt = (c.innerText || '').toLowerCase();
                                if (txt.includes('how to test both birth days') && c.offsetHeight > 20 && c.offsetHeight < 300) {
                                    c.click();
                                    return true;
                                }
                            }
                            return false;
                        }"""
                    )
                    await asyncio.sleep(1.5)
                    if picked:
                        save_btn = page.locator('ytcp-button#save, #save button, button[aria-label="Save"]').first
                        if await save_btn.count() > 0 and await save_btn.is_enabled():
                            await save_btn.click(force=True)
                            await asyncio.sleep(3.0)
                            linked_shorts[short_key] = vsl_vid
                            save_tracker(tracker)
                            print(f"    ✓ [{short_key}] ({short_vid}) Linked Related Video -> {vsl_vid} & Saved!", flush=True)
                        else:
                            print(f"    ⚠ [{short_key}] Picked VSL but Save button not enabled.", flush=True)
                    else:
                        print(f"    ⚠ [{short_key}] Could not find VSL card in Related Video modal.", flush=True)
                else:
                    print(f"    ⚠ [{short_key}] Related Video selector not found on {edit_url}", flush=True)
        finally:
            if browser:
                await browser.close()
            elif ctx:
                await ctx.close()
            if chrome_proc:
                chrome_proc.terminate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--vsl-id", default="")
    args = parser.parse_args()

    mp4_path = os.path.join(VIDEOS_DIR, VSL_FILENAME)
    if args.render_only or not os.path.exists(mp4_path):
        mp4_path = render_vsl_video()
    if not args.render_only:
        asyncio.run(upload_vsl_and_link_related_shorts(mp4_path, existing_vsl_id=args.vsl_id))


if __name__ == "__main__":
    main()
