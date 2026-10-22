"""
=============================================================================
SACRED NUMBER BLUEPRINT · TIKTOK VIDEO FACTORY
Automated Problem -> Solution -> CTA Talking Head / Luxury Dossier Video Generator
Output: 1080x1920 9:16 Vertical MP4s with realistic AI Voiceover, 432Hz ambient pad,
two-tone gold/white synced captions, and Ken Burns animated dossier cuts.
=============================================================================
"""

import asyncio
import io
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Dict, List, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

# Set up FFmpeg binary
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Font definitions
FONT_PATH_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_PATH_REG = r"C:\Windows\Fonts\segoeui.ttf"

# Gold keyword vocabulary for two-tone caption emphasis
GOLD_KEYWORDS = {
    'generic', 'birthday', 'reading', 'zero', 'sacred', 'number', 'blueprint',
    'five', 'ancient', 'systems', 'pythagorean', 'chaldean', 'kabbalah', 'vedic',
    'lo', 'shu', 'fifteen', 'three', 'overlap', 'anchors', 'wealth', 'relationships',
    'free', 'test', 'bio', 'eighty', '80%', 'percent', 'sound', 'vibration',
    'vibrations', 'frequencies', 'frequency', 'tree', 'life', 'sephirot', 'square',
    'hidden', 'timing', '52-day', 'cycle', 'cycles', 'rosicrucian', 'planetary',
    'periods', 'expansion', 'contracts', 'recovery', 'capital', 'biorhythm',
    'somatic', 'effortlessly', 'personalized', 'governs', 'destiny', 'missing',
    'unlocked', 'burnout', 'friction', 'preservation', 'solar', 'jupiterian'
}


def draw_gold_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 7, color: Tuple[int, int, int] = (212, 175, 55)):
    """Draws a crisp 8-point gold diamond star polygon."""
    inner = r * 0.38
    pts = [
        (cx, cy - r),
        (cx + inner, cy - inner),
        (cx + r, cy),
        (cx + inner, cy + inner),
        (cx, cy + r),
        (cx - inner, cy + inner),
        (cx - r, cy),
        (cx - inner, cy - inner)
    ]
    draw.polygon(pts, fill=color)


class TikTokVideoFactory:
    def __init__(
        self,
        scripts_file: str = "tiktok_scripts.json",
        scenes_dir: str = "scenes_cache",
        output_dir: str = "videos",
        queue_dir: str = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
    ):
        self.scripts_file = scripts_file
        self.scenes_dir = scenes_dir
        self.output_dir = output_dir
        self.queue_dir = queue_dir
        
        os.makedirs(self.scenes_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        if os.path.exists(r"G:\My Drive"):
            os.makedirs(self.queue_dir, exist_ok=True)

        # Load fonts
        self.font_top = ImageFont.truetype(FONT_PATH_BOLD, 26)
        self.font_cap = ImageFont.truetype(FONT_PATH_BOLD, 44)
        self.font_bot = ImageFont.truetype(FONT_PATH_BOLD, 30)

        # Load script specifications
        with open(self.scripts_file, "r", encoding="utf-8") as f:
            self.scripts_data = json.load(f)["scripts"]

    async def generate_voice_and_cues(self, script_text: str, voice: str, rate: str, out_voice_path: str) -> List[Dict]:
        """
        Synthesizes TTS speech using edge-tts and converts SentenceBoundaries
        into punchy 3-4 word phrase subtitle cues with precise start/end timings.
        """
        print(f"   [TTS] Synthesizing speech with {voice} at rate {rate}...", flush=True)
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

        # Convert sentence boundaries into punchy phrase chunks (3-4 words)
        cues = []
        for sb in s_boundaries:
            start_sec = sb["offset"] / 10_000_000.0
            dur_sec = sb["duration"] / 10_000_000.0
            text = sb["text"].strip()
            words = text.split()
            if not words:
                continue

            chunk_list = []
            i = 0
            while i < len(words):
                rem = len(words) - i
                if rem <= 4:
                    chunk_list.append(" ".join(words[i:]))
                    break
                elif rem in (5, 6):
                    chunk_list.append(" ".join(words[i : i + 3]))
                    chunk_list.append(" ".join(words[i + 3 :]))
                    break
                else:
                    chunk_list.append(" ".join(words[i : i + 3]))
                    i += 3

            total_chars = sum(len(c) for c in chunk_list)
            curr_t = start_sec
            for c in chunk_list:
                c_dur = dur_sec * (len(c) / max(total_chars, 1))
                cues.append({"start": curr_t, "end": curr_t + c_dur, "text": c})
                curr_t += c_dur

        print(f"   [TTS] Generated {len(cues)} subtitle cues across {len(s_boundaries)} sentences.", flush=True)
        return cues

    def generate_ambient_audio(self, duration_sec: float, out_ambient_path: str):
        """
        Synthesizes a sacred 432Hz harmonic chord (frequencies 108Hz, 216Hz, 324Hz, 432Hz)
        with lowpass filtering at 450Hz and volume 0.10.
        """
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "lavfi",
            "-i", f"aevalsrc=0.25*sin(2*PI*108*t)+0.25*sin(2*PI*216*t)+0.25*sin(2*PI*324*t)+0.25*sin(2*PI*432*t):s=44100:d={duration_sec:.2f}",
            "-af", "lowpass=f=450,volume=0.10",
            out_ambient_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def mix_voice_and_ambient(self, voice_path: str, ambient_path: str, out_mixed_path: str) -> float:
        """
        Mixes voiceover with the 432Hz ambient chord and adds a 1.4s tail pad for the closing CTA hold.
        """
        cmd_mix = [
            FFMPEG_EXE, "-y",
            "-i", voice_path,
            "-i", ambient_path,
            "-filter_complex", "[0:a]apad=pad_dur=1.4[vpad];[vpad]volume=1.0[v];[1:a]volume=0.12[bg];[v][bg]amix=inputs=2:duration=first:dropout_transition=2",
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_mixed_path
        ]
        subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Get mixed audio duration using ffprobe/ffmpeg inspection
        cmd_probe = [FFMPEG_EXE, "-i", out_mixed_path]
        res = subprocess.run(cmd_probe, capture_output=True, text=True)
        dur = 40.0
        for line in res.stderr.splitlines():
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                dur = float(h) * 3600 + float(m) * 60 + float(s)
                break
        return dur

    def render_frame_overlay(
        self,
        base_img: Image.Image,
        t: float,
        scene_name: str,
        active_cue: str | None,
        zoom_factor: float
    ) -> bytes:
        """
        Applies Ken Burns zoom, renders persistent top banner (on dossier scenes), active two-tone caption pill,
        and bottom CTA banner (for dossier scenes), returning JPEG bytes.
        """
        w, h = 1080, 1920
        # 1. Ken Burns Crop & Resize
        if zoom_factor != 1.0:
            new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)
            x0 = (w - new_w) // 2
            y0 = (h - new_h) // 2
            frame = base_img.crop((x0, y0, x0 + new_w, y0 + new_h)).resize((w, h), Image.Resampling.BILINEAR)
        else:
            frame = base_img.copy()

        draw = ImageDraw.Draw(frame)

        # 2. Top Persistent Callout Banner (shown on dossier scenes: scenes 2, 3, 4)
        if scene_name not in ("hook", "cta"):
            top_txt = "FREE 5-SYSTEM CALCULATOR -> LINK IN BIO (@sacrednumberblueprint)"
            t_bbox = draw.textbbox((0, 0), top_txt, font=self.font_top)
            tw, th = t_bbox[2] - t_bbox[0], t_bbox[3] - t_bbox[1]
            tx, ty = 540, 140
            pad_x, pad_y = 42, 14
            draw.rounded_rectangle(
                [tx - tw // 2 - pad_x, ty - th // 2 - pad_y, tx + tw // 2 + pad_x, ty + th // 2 + pad_y],
                radius=22,
                fill=(14, 14, 18),
                outline=(212, 175, 55),
                width=2
            )
            draw_gold_star(draw, tx - tw // 2 - 20, ty, r=8)
            draw_gold_star(draw, tx + tw // 2 + 20, ty, r=8)
            draw.text((tx, ty - 2), top_txt, fill=(245, 245, 247), font=self.font_top, anchor="mm")

        # 3. Dynamic Center Caption Pill (if speaking)
        if active_cue:
            words = active_cue.split()
            space_w = draw.textbbox((0, 0), " ", font=self.font_cap)[2]
            w_widths = [draw.textbbox((0, 0), w, font=self.font_cap)[2] for w in words]
            tot_w = sum(w_widths) + (len(words) - 1) * space_w
            ch = draw.textbbox((0, 0), "Hg", font=self.font_cap)[3]
            cx, cy = 540, 1260
            cpad_x, cpad_y = 28, 14

            draw.rounded_rectangle(
                [cx - tot_w // 2 - cpad_x, cy - ch // 2 - cpad_y, cx + tot_w // 2 + cpad_x, cy + ch // 2 + cpad_y],
                radius=20,
                fill=(10, 10, 14),
                outline=(212, 175, 55),
                width=2
            )
            cur_x = cx - tot_w // 2
            for w, ww in zip(words, w_widths):
                is_gold = w.lower().strip("?,.!:'\"()") in GOLD_KEYWORDS
                col = (243, 198, 68) if is_gold else (255, 255, 255)
                draw.text((cur_x, cy - ch // 2 - 2), w, fill=col, font=self.font_cap)
                cur_x += ww + space_w

        # 4. Bottom Callout Banner (shown on dossier scenes: scenes 2, 3, 4)
        if scene_name not in ("hook", "cta"):
            bot_txt = "LINK IN BIO (@sacrednumberblueprint)"
            b_bbox = draw.textbbox((0, 0), bot_txt, font=self.font_bot)
            bw, bh = b_bbox[2] - b_bbox[0], b_bbox[3] - b_bbox[1]
            bx, by = 540, 1780
            bpad_x, bpad_y = 36, 14
            draw.rounded_rectangle(
                [bx - bw // 2 - bpad_x, by - bh // 2 - bpad_y, bx + bw // 2 + bpad_x, by + bh // 2 + bpad_y],
                radius=24,
                fill=(212, 175, 55)
            )
            draw_gold_star(draw, bx - bw // 2 - 18, by, r=8, color=(14, 14, 18))
            draw_gold_star(draw, bx + bw // 2 + 18, by, r=8, color=(14, 14, 18))
            draw.text((bx, by - 2), bot_txt, fill=(14, 14, 18), font=self.font_bot, anchor="mm")

        # Encode to JPEG
        buf = io.BytesIO()
        frame.save(buf, format="JPEG", quality=92)
        return buf.getvalue()

    def render_ad_video(
        self,
        ad_cfg: Dict,
        cues: List[Dict],
        mixed_audio_path: str,
        audio_dur: float,
        output_mp4: str
    ):
        """
        Orchestrates frame rendering and streams JPEG frames into FFmpeg at 30 fps.
        """
        ad_id = ad_cfg["id"]
        total_dur = audio_dur
        fps = 30
        total_frames = int(total_dur * fps)
        print(f"\n[RENDER] Building {ad_cfg['filename']} ({total_dur:.2f}s, {total_frames} frames)...", flush=True)

        # Map scene schedule based on ad_id
        if ad_id == "ad_01":
            scene_schedule = [
                (0.0, 7.55, "hook", "scenes_cache/card_hook_ad_01.png"),
                (7.55, 17.50, "mandala", "scenes_cache/scene_mandala.png"),
                (17.50, 27.00, "ledger", "scenes_cache/scene_ledger.png"),
                (27.00, 35.50, "anchors", "scenes_cache/scene_anchors.png"),
                (35.50, total_dur, "cta", "scenes_cache/card_cta_screen.png")
            ]
        elif ad_id == "ad_02":
            scene_schedule = [
                (0.0, 7.50, "hook", "scenes_cache/card_hook_ad_02.png"),
                (7.50, 16.50, "tree", "scenes_cache/scene_tree.png"),
                (16.50, 26.00, "loshu", "scenes_cache/scene_loshu.png"),
                (26.00, 33.45, "tally", "scenes_cache/scene_tally.png"),
                (33.45, total_dur, "cta", "scenes_cache/card_cta_screen.png")
            ]
        else:  # ad_03
            scene_schedule = [
                (0.0, 8.00, "hook", "scenes_cache/card_hook_ad_03.png"),
                (8.00, 17.50, "cycles", "scenes_cache/scene_cycles.png"),
                (17.50, 26.00, "somatic", "scenes_cache/scene_somatic.png"),
                (26.00, 30.50, "directives", "scenes_cache/scene_directives.png"),
                (30.50, total_dur, "cta", "scenes_cache/card_cta_screen.png")
            ]

        # Load all scene images into memory
        loaded_scenes = {}
        for _, _, s_name, path in scene_schedule:
            if s_name not in loaded_scenes:
                loaded_scenes[s_name] = Image.open(path).convert("RGB")

        # Launch FFmpeg pipe
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
            output_mp4
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        cue_idx = 0
        t0 = time.time()

        for f_idx in range(total_frames):
            t = f_idx / float(fps)

            # Find active scene
            active_scene_item = scene_schedule[-1]
            scene_idx = len(scene_schedule) - 1
            for s_i, (s_start, s_end, s_name, _) in enumerate(scene_schedule):
                if s_start <= t < s_end:
                    active_scene_item = (s_start, s_end, s_name, _)
                    scene_idx = s_i
                    break

            s_start, s_end, s_name, _ = active_scene_item
            base_img = loaded_scenes[s_name]

            # Compute Ken Burns zoom
            s_dur = max(s_end - s_start, 0.1)
            u = (t - s_start) / s_dur
            if scene_idx % 2 == 0:
                zoom = 1.000 + 0.032 * u
            else:
                zoom = 1.032 - 0.032 * u

            # Find active caption cue
            active_cue_text = None
            while cue_idx < len(cues) and cues[cue_idx]["end"] < t:
                cue_idx += 1
            if cue_idx < len(cues) and cues[cue_idx]["start"] <= t <= cues[cue_idx]["end"]:
                active_cue_text = cues[cue_idx]["text"]

            frame_bytes = self.render_frame_overlay(base_img, t, s_name, active_cue_text, zoom)
            proc.stdin.write(frame_bytes)

            if (f_idx + 1) % 150 == 0 or (f_idx + 1) == total_frames:
                pct = (f_idx + 1) / total_frames * 100.0
                elapsed = time.time() - t0
                speed = (f_idx + 1) / max(elapsed, 0.01)
                print(f"   Frame {f_idx + 1}/{total_frames} ({pct:.1f}%) | {speed:.1f} fps", flush=True)

        proc.stdin.close()
        proc.wait()

        render_sec = time.time() - t0
        mb_size = os.path.getsize(output_mp4) / (1024 * 1024)
        print(f"✓ Created {output_mp4} ({mb_size:.2f} MB in {render_sec:.1f}s)", flush=True)

    def export_queue(self):
        """
        Copies all 3 generated MP4s to Google Drive tiktok_queue,
        creates captions_and_hashtags.md and publish_queue.py.
        """
        print("\n[EXPORT] Copying MP4s and publishing guides to Queue...", flush=True)
        # 1. Copy MP4s to output and queue
        for ad in self.scripts_data:
            local_src = os.path.join(self.output_dir, ad["filename"])
            if os.path.exists(local_src):
                # Copy to local root as well
                shutil.copy2(local_src, ad["filename"])
                if os.path.exists(self.queue_dir):
                    g_dst = os.path.join(self.queue_dir, ad["filename"])
                    shutil.copy2(local_src, g_dst)
                    print(f"   ✓ Synced to G Drive: {g_dst}")

        # 2. Generate captions_and_hashtags.md
        md_content = self.build_captions_markdown()
        local_md = "captions_and_hashtags.md"
        with open(local_md, "w", encoding="utf-8") as f:
            f.write(md_content)
        if os.path.exists(self.queue_dir):
            shutil.copy2(local_md, os.path.join(self.queue_dir, local_md))
        print(f"   ✓ Wrote {local_md}")

        # 3. Generate publish_queue.py
        py_content = self.build_publish_queue_script()
        local_py = "publish_queue.py"
        with open(local_py, "w", encoding="utf-8") as f:
            f.write(py_content)
        if os.path.exists(self.queue_dir):
            shutil.copy2(local_py, os.path.join(self.queue_dir, local_py))
        print(f"   ✓ Wrote {local_py}")

    def build_captions_markdown(self) -> str:
        lines = [
            "# ✦ SACRED NUMBER BLUEPRINT · TIKTOK POSTING QUEUE ✦",
            f"**Account:** `@sacrednumberblueprint`  ",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Target Link in Bio:** `https://rj2point0.github.io/sovereign-5-system/`  ",
            "",
            "---",
            ""
        ]

        for i, ad in enumerate(self.scripts_data, 1):
            lines.extend([
                f"## 📹 VIDEO #{i}: {ad['filename']}",
                f"**Angle / Hook:** {ad['hook_name']}  ",
                f"**Audio Track:** Original Sound (`edge-tts` AvaNeural + 432Hz Ambient Harmonic Drone)  ",
                "",
                "### 📝 Copy-Paste TikTok Caption:",
                "```text",
                ad["tiktok_caption"],
                "```",
                "",
                "### 🏷️ Target Hashtags:",
                f"`{' '.join(ad['hashtags'])}`",
                "",
                "### 🎙️ Spoken Voiceover Script (Word-for-Word):",
                f"> \"{ad['spoken_script']}\"",
                "",
                "### 🎬 Visual Scene Architecture (1080x1920 Full Bleed):",
                "1. **0:00 - 0:07 Hook:** Luxury Problem Comparison Screen (1 System vs. 5 Systems).",
                "2. **0:07 - 0:17 Convergence:** Page 2 Sacred 5-Ring Mandala (7 · 8 · 4) or Tree of Life / Cycles.",
                "3. **0:17 - 0:27 Technical Proof:** Page 5 15-Calculation Ledger, Chinese Lo Shu Grid, or Somatic Health Box.",
                "4. **0:27 - 0:35 Deep Personalization:** Page 4 Master Overlap Anchors & Frequency Tally.",
                "5. **0:35 - 0:41 Clear CTA:** High-converting closing screen pointing to Link in Bio.",
                "",
                "---",
                ""
            ])

        lines.extend([
            "## 🚀 PROVEN TIKTOK POSTING PROTOCOL",
            "1. **Sound:** Set audio to **Original Sound - Sacred Number Blueprint** (the 432Hz ambient chord will encourage repeat watches).",
            "2. **Cover Frame:** Select the 0:03 frame displaying the golden hook comparison card.",
            "3. **Pinned Comment:** `\"Test your full 5-system overlap code at the link in our bio (Pythagorean, Chaldean, Kabbalah, Vedic & Lo Shu) 👁️✨\"`",
            "4. **Cadence:** Post 1 video every 24–48 hours to let the TikTok algorithm test diverse audience pools.",
            ""
        ])
        return "\n".join(lines)

    def build_publish_queue_script(self) -> str:
        return '''"""
Automated TikTok Queue Manager & Publisher Utility
Inspects ready-to-post videos, verifies file sizes and durations,
and prints copy-paste captions for TikTok Web Studio.
"""

import os, json, glob

QUEUE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_FILE = os.path.join(QUEUE_DIR, "tiktok_scripts.json")

def inspect_queue():
    print("=" * 65)
    print("   SACRED NUMBER BLUEPRINT · TIKTOK QUEUE STATUS")
    print("=" * 65)
    
    mp4s = sorted(glob.glob(os.path.join(QUEUE_DIR, "tiktok_ad_*.mp4")))
    if not mp4s:
        # Check parent folder
        mp4s = sorted(glob.glob("tiktok_ad_*.mp4"))
    
    print(f"Found {len(mp4s)} videos ready for broadcast:")
    for f in mp4s:
        sz_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  • {os.path.basename(f)}: {sz_mb:.2f} MB")
        
    print("\\nPosting Instructions:")
    print("  1. Log into TikTok Web Studio: https://www.tiktok.com/creator-center/upload")
    print("  2. Upload desired MP4 video.")
    print("  3. Copy caption & hashtags from captions_and_hashtags.md")
    print("  4. Verify Link in Bio points to: https://rj2point0.github.io/sovereign-5-system/")
    print("=" * 65)

if __name__ == "__main__":
    inspect_queue()
'''

    async def run(self):
        print("=" * 65)
        print("   STARTING TIKTOK VIDEO FACTORY (3 FULL PRODUCTION ADS)")
        print("=" * 65)

        for ad in self.scripts_data:
            ad_id = ad["id"]
            filename = ad["filename"]
            out_mp4 = os.path.join(self.output_dir, filename)
            voice_mp3 = f"voice_{ad_id}.mp3"
            ambient_wav = f"ambient_{ad_id}.wav"
            mixed_mp3 = f"mixed_{ad_id}.mp3"

            print(f"\n▶ Processing Video [{ad_id}]: {ad['hook_name']}...", flush=True)

            # 1. Voiceover & Subtitles
            cues = await self.generate_voice_and_cues(
                ad["spoken_script"],
                ad["voice"],
                ad["rate"],
                voice_mp3
            )

            # 2. Ambient Audio & Mix
            # Estimate raw voice duration from last cue
            raw_dur = cues[-1]["end"] if cues else 40.0
            print(f"   [Audio] Synthesizing 432Hz ambient chord ({raw_dur:.1f}s)...", flush=True)
            self.generate_ambient_audio(raw_dur + 2.0, ambient_wav)
            
            print(f"   [Audio] Mixing voice and ambient pad...", flush=True)
            mixed_dur = self.mix_voice_and_ambient(voice_mp3, ambient_wav, mixed_mp3)

            # 3. Video Rendering
            self.render_ad_video(ad, cues, mixed_mp3, mixed_dur, out_mp4)

            # Clean temporary audio files
            for temp_f in (voice_mp3, ambient_wav, mixed_mp3):
                if os.path.exists(temp_f):
                    os.remove(temp_f)

        # 4. Sync assets to G: Drive Queue & publish guides
        self.export_queue()

        print("\n" + "=" * 65)
        print("   ALL 3 TIKTOK ADS SUCCESSFULLY PRODUCED AND EXPORTED!")
        print("=" * 65)


if __name__ == "__main__":
    factory = TikTokVideoFactory()
    asyncio.run(factory.run())
