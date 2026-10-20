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
    print("  RECORDING 9:16 VERTICAL PROMO (1080x1920 RETINA FULL BLEED)", flush=True)
    print("=========================================================", flush=True)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    output_mp4 = os.path.abspath("tiktok_promo_1.mp4")
    print(f"FFmpeg binary: {ffmpeg_exe}", flush=True)
    print(f"Target Output: {output_mp4}", flush=True)

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

        # Inject styles: auto scroll, dark background, remove debug/toast/sticky elements
        await page.add_init_script("""
            window._disableToast = true;
            window.toast = function() {};
            const style = document.createElement('style');
            style.id = 'clean-recording-style';
            style.textContent = `
                html { scroll-behavior: auto !important; background: #0A0A0C !important; }
                body { background: #0A0A0C !important; }
                #toast, .toast, #claim-bar, .vip-badge, [data-vip-indicator] {
                    display: none !important;
                    opacity: 0 !important;
                    visibility: hidden !important;
                }
            `;
            document.documentElement.appendChild(style);
        """)

        async def smooth_scroll(y_start, y_target, steps=15, repeat_per_step=2):
            for i in range(steps):
                t = i / max(steps - 1, 1)
                ease = cubic_ease(t)
                y = int(y_start + (y_target - y_start) * ease)
                await page.evaluate(f"window.scrollTo(0, {y})")
                frame = await page.screenshot(type='jpeg', quality=95)
                write_frame(frame, repeat_per_step)

        # -------------------------------------------------------------
        # SCENE 1: HERO HOOK (0.0s – 3.5s)
        # -------------------------------------------------------------
        print("[1/7] Scene A: Hero Hook & Form Fill...", flush=True)
        await page.goto("http://127.0.0.1:8080/?vip=adam", wait_until="networkidle")
        await page.evaluate("window.scrollTo(0, 0)")
        hero_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(hero_frame, 45)  # 1.5s hold on headline

        await smooth_scroll(0, 240, steps=8, repeat_per_step=2)  # 0.5s scroll to form

        # Load Founder Sample
        await page.click('button[data-action="sample"]')
        filled_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(filled_frame, 25)  # Pause on Adam Vega, 1978-08-19

        # Click calculate & record spinning ritual animation
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#ritual', state='visible')
        for _ in range(8):
            await asyncio.sleep(0.04)
            r_frame = await page.screenshot(type='jpeg', quality=95)
            write_frame(r_frame, 4)  # 32 frames of smooth spinning animation

        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        print("Step 1 complete: Hero Calculator & Ritual finished.", flush=True)

        # -------------------------------------------------------------
        # SCENE 2: TEASER SCAN, MATRIX, & ORDER BUMP (3.5s – 8.7s)
        # -------------------------------------------------------------
        print("[2/7] Scene B: Teaser Anchor 7, Locked Matrix & Order Bump...", flush=True)
        await page.evaluate("window.scrollTo(0, 0)")
        teaser_top = await page.screenshot(type='jpeg', quality=95)
        write_frame(teaser_top, 45)  # 1.5s hold on #1 Signature Anchor 7

        await smooth_scroll(0, 820, steps=16, repeat_per_step=2)  # Scroll to Matrix
        matrix_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(matrix_frame, 35)  # 1.2s hold on Frosted Glass Padlocks

        await smooth_scroll(820, 4420, steps=18, repeat_per_step=2)  # Scroll to Checkout
        checkout_base = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_base, 15)  # 0.5s on $37

        # Check the Rosicrucian Order Bump checkbox (updates to $84)
        await page.click('#bump')
        checkout_bump = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_bump, 45)  # 1.5s on $84 updated total

        # Unlock full dossier
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)

        # Remove header, action container, claim-bar, and toast completely
        await page.evaluate("""() => {
            const style = document.createElement('style');
            style.textContent = `
                header, #claim-bar, #dossier-actions, #toast, .toast, .sticky-cta {
                    display: none !important;
                }
                #view-dossier { padding: 0 !important; margin: 0 !important; }
                .cover {
                    min-height: 620px !important;
                    height: 636px !important;
                    padding: 24px 16px !important;
                    display: flex !important;
                    flex-direction: column !important;
                    justify-content: space-between !important;
                    box-sizing: border-box !important;
                }
                .cover .seal { width: 72px !important; height: 72px !important; }
                .cover .hairline { margin-top: 10px !important; margin-bottom: 10px !important; }
                .cover h1 { font-size: 1.85rem !important; margin-top: 4px !important; }
                .cover .font-display.text-3xl { font-size: 1.6rem !important; margin-top: 4px !important; }
                .cover .eyebrow { font-size: 0.58rem !important; margin-bottom: 4px !important; }
                .cover p { margin-top: 2px !important; }
            `;
            document.documentElement.appendChild(style);
            const t = document.getElementById('toast');
            if (t) t.remove();
        }""")
        print("Step 2 complete: Teaser & Checkout Bump finished.", flush=True)

        # -------------------------------------------------------------
        # SCENE 3: LUXURY COVER (9.0s – 13.0s)
        # -------------------------------------------------------------
        print("[3/7] Scene C: Framing Page 1 Sovereign Blueprint Luxury Cover...", flush=True)
        await page.evaluate("window.scrollTo(0, 0)")
        cover_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(cover_frame, 120)  # Full 4.0s hold on luxury cover from Seal to 8-7-4 Medallions
        print("Step 3 complete: Luxury Cover framed.", flush=True)

        # -------------------------------------------------------------
        # SCENE 4: MASTER OVERLAP & HARMONICS (13.0s – 16.7s)
        # -------------------------------------------------------------
        print("[4/7] Scene D: Page 3 Master Overlap Anchors & Tally Bars...", flush=True)
        p3_y = await page.evaluate("""() => {
            const el = document.querySelector('article.page[data-page="3"]');
            return Math.round(el.getBoundingClientRect().top + window.scrollY - 16);
        }""")
        await smooth_scroll(0, p3_y, steps=18, repeat_per_step=2)
        p3_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p3_frame, 90)  # 3.0s hold on Anchors 7, 8, 4 + Frequency Tally Bars
        print("Step 4 complete: Master Overlap & Tally Bars framed.", flush=True)

        # -------------------------------------------------------------
        # SCENE 5: KABBALISTIC TREE OF LIFE (16.7s – 20.4s)
        # -------------------------------------------------------------
        print("[5/7] Scene E: Page 9 Kabbalistic Tree of Life Diagram (Centered)...", flush=True)
        p9_y = await page.evaluate("""() => {
            const svg = document.querySelector('article.page[data-page="9"] svg');
            const rect = svg.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (640 - rect.height) / 2);
        }""")
        await smooth_scroll(p3_y, p9_y, steps=18, repeat_per_step=2)
        p9_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p9_frame, 90)  # 3.0s hold on Tree of Life vector diagram
        print("Step 5 complete: Tree of Life centered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 6: CHINESE LO SHU 3x3 GRID (20.4s – 24.1s)
        # -------------------------------------------------------------
        print("[6/7] Scene F: Page 11 Chinese Lo Shu 3x3 Magic Square (Centered)...", flush=True)
        p11_y = await page.evaluate("""() => {
            const grid = document.querySelector('article.page[data-page="11"] .loshu');
            const rect = grid.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (640 - rect.height) / 2);
        }""")
        await smooth_scroll(p9_y, p11_y, steps=18, repeat_per_step=2)
        p11_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p11_frame, 90)  # 3.0s hold with all 3 rows (4-9-2, 3-5-7, 8-1-6) fully visible
        print("Step 6 complete: Lo Shu 3x3 Grid centered.", flush=True)

        # -------------------------------------------------------------
        # SCENE 7: 365-DAY ROSICRUCIAN CALENDAR (24.1s – 30.5s)
        # -------------------------------------------------------------
        print("[7/7] Scene G: Page 13 Rosicrucian Calendar (Active Today: Lunar Period)...", flush=True)
        p13_y = await page.evaluate("""() => {
            const card = document.querySelector('article.page[data-page="13"] .card-soft');
            const rect = card.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p11_y, p13_y, steps=18, repeat_per_step=2)
        p13_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p13_frame, 120)  # 4.0s strong ending hold on 365-Day Rosicrucian Cycles
        print("Step 7 complete: Rosicrucian Calendar framed.", flush=True)

        print(f"\nTotal video frames encoded: {total_frames} (Duration: {total_frames / 30.0:.2f}s)", flush=True)
        await browser.close()

    # Finalize MP4
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

    # Read frame at mid-video
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(450, frame_count - 1))
    ret_mid, mid_frame = cap.read()
    cap.release()

    px_b, px_g, px_r = mid_frame[1910, 1070]
    print(f"Resolution: {w}x{h} (Aspect Ratio 9:16)", flush=True)
    print(f"Duration:   {duration_sec:.2f}s ({frame_count} frames @ {fps:.1f} fps)", flush=True)
    print(f"Bottom-Right Pixel (1070, 1910) BGR: [{px_b}, {px_g}, {px_r}]", flush=True)

    assert w == 1080 and h == 1920, f"Expected 1080x1920, got {w}x{h}"
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
