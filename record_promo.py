import asyncio
import os
import sys
import shutil
import subprocess
import time
import cv2
import imageio_ffmpeg
from playwright.async_api import async_playwright

def cubic_ease(t):
    """Smooth cubic in-out easing curve for fluid, luxury camera movement"""
    return 4 * t * t * t if t < 0.5 else 1.0 - pow(-2.0 * t + 2.0, 3) / 2.0

async def record_promo():
    t_start = time.time()
    print("=========================================================", flush=True)
    print("  RECORDING 9:16 VERTICAL PROMO (1080x1920 FULL BLEED)   ", flush=True)
    print("=========================================================", flush=True)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    output_mp4 = os.path.abspath("tiktok_promo_1.mp4")
    print(f"FFmpeg binary: {ffmpeg_exe}", flush=True)
    print(f"Target Output: {output_mp4}", flush=True)

    # Clean old file if exists
    if os.path.exists(output_mp4):
        try:
            os.remove(output_mp4)
        except Exception:
            pass

    # Start FFmpeg with DEVNULL to prevent OS pipe buffer deadlocks on Windows
    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-r", "30",
        "-i", "-",
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "18",
        "-r", "30",
        "-movflags", "+faststart",
        output_mp4
    ]

    ffmpeg_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    total_frames = 0

    def write_frame(frame_bytes, count=1):
        nonlocal total_frames
        for _ in range(count):
            ffmpeg_proc.stdin.write(frame_bytes)
        total_frames += count

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Viewport: 360x640 with device_scale_factor=3 yields exactly 1080x1920 full bleed
        context = await browser.new_context(
            viewport={'width': 360, 'height': 640},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        # Inject styles to eliminate grey borders, enforce auto scrolling, and hide debug/utility elements
        await page.add_init_script("""
            const style = document.createElement('style');
            style.textContent = `
                html { scroll-behavior: auto !important; background: #0A0A0C !important; }
                body { background: #0A0A0C !important; }
                #toast, .toast, #claim-bar, .vip-badge, #dossier-actions, [data-vip-indicator] {
                    display: none !important;
                }
            `;
            document.documentElement.appendChild(style);
        """)

        # Efficient smooth scroll helper: takes 16-18 easing screenshots and writes each twice (32-36 frames @ 30fps)
        async def smooth_scroll(y_start, y_target, steps=16, repeat_per_step=2):
            for i in range(steps):
                t = i / max(steps - 1, 1)
                ease = cubic_ease(t)
                y = int(y_start + (y_target - y_start) * ease)
                await page.evaluate(f"window.scrollTo(0, {y})")
                frame = await page.screenshot(type='jpeg', quality=95)
                write_frame(frame, repeat_per_step)

        # -------------------------------------------------------------
        # SCENE 1: HERO HOOK (0.0s – 2.0s = 60 frames)
        # -------------------------------------------------------------
        print("[1/11] Hero Hook & Title...", flush=True)
        await page.goto("http://127.0.0.1:8080/?vip=adam", wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, 0)")
        hero_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(hero_frame, 45)  # 1.5s pause on hero hook
        await smooth_scroll(0, 240, steps=8, repeat_per_step=2)  # 0.5s smooth scroll down to form
        print("Step 1 complete: Hero Hook rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 2: FORM FILL & SACRED GEOMETRY RITUAL (2.0s – 5.5s = 105 frames)
        # -------------------------------------------------------------
        print("[2/11] Loading Founder Sample & Ritual Animation...", flush=True)
        form_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(form_frame, 10)

        # Click Load Founder Sample button
        await page.click('button[data-action="sample"]')
        filled_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(filled_frame, 25)  # Pause on filled form (Adam Vega, 1978-08-19)

        # Submit calculation form to trigger ritual
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#ritual', state='visible')

        # Capture 10 frames of spinning ritual animation, repeating each 4x (40 frames)
        for _ in range(10):
            await asyncio.sleep(0.04)
            r_frame = await page.screenshot(type='jpeg', quality=95)
            write_frame(r_frame, 4)

        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        print("Step 2 complete: Ritual & calculation finished.", flush=True)

        # -------------------------------------------------------------
        # SCENE 3: 20% TEASER SCAN & ANCHOR 7 MEDALLION (5.5s – 8.5s = 90 frames)
        # -------------------------------------------------------------
        print("[3/11] 20% Teaser Scan & Anchor 7 Medallion...", flush=True)
        await page.evaluate("window.scrollTo(0, 0)")
        teaser_top = await page.screenshot(type='jpeg', quality=95)
        write_frame(teaser_top, 54)  # 1.8s pause on Anchor 7 reveal
        await smooth_scroll(0, 820, steps=18, repeat_per_step=2)  # 1.2s smooth scroll to 5-System Matrix
        print("Step 3 complete: Teaser & Anchor 7 rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 4: 5-SYSTEM MATRIX (LOCKED & FROSTED GLASS) (8.5s – 11.5s = 90 frames)
        # -------------------------------------------------------------
        print("[4/11] 5-System Matrix & Frosted Glass Padlocks...", flush=True)
        matrix_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(matrix_frame, 54)  # 1.8s pause to read locked systems
        await smooth_scroll(820, 4420, steps=18, repeat_per_step=2)  # 1.2s smooth scroll to checkout
        print("Step 4 complete: Frosted matrix rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 5: CHECKOUT CARD & BUMP TOGGLE ($37 -> $84) (11.5s – 15.0s = 105 frames)
        # -------------------------------------------------------------
        print("[5/11] Checkout Card & Rosicrucian Bump ($37 -> $84)...", flush=True)
        checkout_base = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_base, 18)  # 0.6s on $37

        # Click order bump checkbox
        await page.click('#bump')
        checkout_bump = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_bump, 42)  # 1.4s on $84 updated total

        # Unlock full dossier via founder bypass
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        print("Step 5 complete: Checkout bump & full unlock.", flush=True)

        # -------------------------------------------------------------
        # SCENE 6: FULL LUXURY DOSSIER COVER (15.0s – 18.5s = 105 frames)
        # -------------------------------------------------------------
        print("[6/11] Sovereign Blueprint Luxury Cover...", flush=True)
        # Scroll directly to top of Cover Card
        await page.evaluate("window.scrollTo(0, 320)")
        cover_top = await page.screenshot(type='jpeg', quality=95)
        write_frame(cover_top, 40)  # 1.3s pause on Seal, Title, "ADAM VEGA"

        # Gentle glide down to bring Big Three Overlap Medallions (8, 7, 4) into full view
        await smooth_scroll(320, 520, steps=10, repeat_per_step=2)
        cover_medals = await page.screenshot(type='jpeg', quality=95)
        write_frame(cover_medals, 45)  # 1.5s pause on Big Three medallions
        print("Step 6 complete: Luxury Cover rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 7: MASTER OVERLAP & HARMONICS (18.5s – 21.5s = 90 frames)
        # -------------------------------------------------------------
        print("[7/11] Master Overlap 7-8-4 & Harmonics 9 & 6...", flush=True)
        await smooth_scroll(520, 3150, steps=18, repeat_per_step=2)  # 1.2s scroll to Page 3
        overlap_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(overlap_frame, 54)  # 1.8s pause on Master Overlap Anchors & Harmonics
        print("Step 7 complete: Master Overlap 7-8-4 rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 8: KABBALISTIC TREE OF LIFE (21.5s – 24.5s = 90 frames)
        # -------------------------------------------------------------
        print("[8/11] Kabbalistic Tree of Life Diagram...", flush=True)
        await smooth_scroll(3150, 14350, steps=18, repeat_per_step=2)  # 1.2s scroll to Page 9
        kabbalah_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(kabbalah_frame, 54)  # 1.8s pause on Tree of Life vector diagram
        print("Step 8 complete: Tree of Life rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 9: CHINESE LO SHU 3x3 GRID & FIVE ELEMENTS (24.5s – 27.5s = 90 frames)
        # -------------------------------------------------------------
        print("[9/11] Chinese Lo Shu 3x3 Grid & Five Elements...", flush=True)
        await smooth_scroll(14350, 18500, steps=18, repeat_per_step=2)  # 1.2s scroll to Page 11
        loshu_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(loshu_frame, 54)  # 1.8s pause on Lo Shu Magic Square
        print("Step 9 complete: Lo Shu Magic Square rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 10: ROSICRUCIAN 365-DAY CYCLES CALENDAR (27.5s – 30.5s = 90 frames)
        # -------------------------------------------------------------
        print("[10/11] Rosicrucian 365-Day Cycles Calendar...", flush=True)
        await smooth_scroll(18500, 22250, steps=18, repeat_per_step=2)  # 1.2s scroll to Page 13
        cycles_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(cycles_frame, 54)  # 1.8s pause on 7-Period Cycles Calendar
        print("Step 10 complete: Rosicrucian Calendar rendered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 11: BILINGUAL SPANISH TOGGLE (EN | ES) (30.5s – 33.5s = 90 frames)
        # -------------------------------------------------------------
        print("[11/11] Scrolling to top & Toggling to Spanish (EN | ES)...", flush=True)
        await smooth_scroll(22250, 320, steps=15, repeat_per_step=2)  # 1.0s fast smooth scroll back to top of cover

        # Click Spanish language toggle
        await page.click('button[data-lang="es"]')
        await asyncio.sleep(0.3)
        es_cover_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(es_cover_frame, 60)  # 2.0s pause on luxury Spanish edition
        print("Step 11 complete: Spanish edition rendered.", flush=True)

        print(f"Total video frames encoded: {total_frames} (Duration: {total_frames / 30.0:.2f}s)", flush=True)
        await browser.close()

    # Close FFmpeg stdin and finalize video
    print("Finalizing MP4 video container...", flush=True)
    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()

    if ffmpeg_proc.returncode != 0:
        raise RuntimeError("FFmpeg encoding failed!")

    file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    elapsed = time.time() - t_start
    print(f"\n[OK] Video successfully written to: {output_mp4} ({file_size_mb:.2f} MB in {elapsed:.1f}s)", flush=True)

    # -------------------------------------------------------------
    # VERIFICATION: CHECK 1080x1920 RESOLUTION & BOTTOM-RIGHT PIXEL
    # -------------------------------------------------------------
    print("\n--- Verifying Output Video Specifications ---", flush=True)
    cap = cv2.VideoCapture(output_mp4)
    ret, test_frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to read encoded MP4 video!")

    h, w, c = test_frame.shape
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = frame_count / (fps if fps > 0 else 30.0)

    # Read frame at mid-video (frame 450)
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(450, frame_count - 1))
    ret_mid, mid_frame = cap.read()
    cap.release()

    # Check pixel (1070, 1910) -> (y=1910, x=1070)
    px_b, px_g, px_r = mid_frame[1910, 1070]
    print(f"Resolution: {w}x{h} (Aspect Ratio 9:16)", flush=True)
    print(f"Duration:   {duration_sec:.2f}s ({frame_count} frames @ {fps:.1f} fps)", flush=True)
    print(f"Bottom-Right Pixel (1070, 1910) BGR: [{px_b}, {px_g}, {px_r}]", flush=True)

    assert w == 1080 and h == 1920, f"Expected 1080x1920, got {w}x{h}"
    # Obsidian dark should have all channels <= 25 (NOT grey ~128)
    assert px_b < 25 and px_g < 25 and px_r < 25, f"Expected dark obsidian, got BGR [{px_b}, {px_g}, {px_r}]"
    print("VERIFICATION PASSED: Full-bleed 1080x1920 with dark obsidian background and zero grey borders!", flush=True)

    # Sync to Google Drive
    gdrive_dir = r"G:\My Drive\5_System_Numerology_MVP"
    if os.path.exists(gdrive_dir):
        dest = os.path.join(gdrive_dir, "tiktok_promo_1.mp4")
        shutil.copy2(output_mp4, dest)
        print(f"Synced to Google Drive: {dest}", flush=True)

    # Sync to Antigravity brain artifacts
    art_dir = r"C:\Users\User\.gemini\antigravity\brain\5be548e1-0bfd-4f21-b5d4-67c12098b05e"
    if os.path.exists(art_dir):
        shutil.copy2(output_mp4, os.path.join(art_dir, "tiktok_promo_1.mp4"))
        print(f"Synced to artifacts directory: {art_dir}", flush=True)

if __name__ == '__main__':
    asyncio.run(record_promo())
