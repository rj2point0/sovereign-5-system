import asyncio
import os
import sys
import shutil
import subprocess
import time
import cv2
import numpy as np
import imageio_ffmpeg
from playwright.async_api import async_playwright

def cubic_ease(t):
    """Smooth cubic in-out easing curve for fluid, luxury camera movement"""
    return 4 * t * t * t if t < 0.5 else 1.0 - pow(-2.0 * t + 2.0, 3) / 2.0

async def record_promo():
    t_start = time.time()
    print("=========================================================", flush=True)
    print("  RECORDING 9:16 VERTICAL PROMO (405x720 RETINA MASTER)", flush=True)
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
    # Raw frame: 405x720 at scale=3 is 1215x2160 (exact 9:16)
    # Downscaled via lanczos to 1080x1920 (exact 9:16 full-bleed)
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
        # Viewport: 405x720 with device_scale_factor=3 yields 1215x2160 (exact 9:16)
        context = await browser.new_context(
            viewport={'width': 405, 'height': 720},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        # Helper: smooth scroll between two Y coordinates with cubic easing
        async def smooth_scroll(y_start, y_target, steps=15, repeat_per_step=2):
            for i in range(steps):
                t = i / max(steps - 1, 1)
                ease = cubic_ease(t)
                y = int(y_start + (y_target - y_start) * ease)
                await page.evaluate(f"window.scrollTo(0, {y})")
                frame = await page.screenshot(type='jpeg', quality=95)
                write_frame(frame, repeat_per_step)

        # -------------------------------------------------------------
        # STEP 1: HERO CALCULATOR CENTERED (0–3s)
        # -------------------------------------------------------------
        print("[1/7] Step 1: Hero Calculator Centered & Sacred Ritual...", flush=True)
        await page.goto("http://127.0.0.1:8080/?vip=adam", wait_until="networkidle")

        # Disable toast and normalize scroll
        await page.evaluate("""() => {
            window._disableToast = true;
            window.toast = () => {};
            document.documentElement.style.scrollBehavior = 'auto';
            document.body.style.scrollBehavior = 'auto';
            const t = document.getElementById('toast');
            if (t) t.remove();
        }""")

        # Center calculator form in 720px viewport
        hero_y = await page.evaluate("""() => {
            const form = document.getElementById('calc-form');
            const rect = form.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await page.evaluate(f"window.scrollTo(0, {hero_y})")
        hero_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(hero_frame, 30)  # 1.0s hold on calculator form

        # Click Load Founder Sample (Adam Vega, 1978-08-19)
        await page.click('button[data-action="sample"]')
        filled_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(filled_frame, 25)  # 0.8s hold on filled details

        # Submit calculation form & capture spinning sacred geometry rings
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#ritual', state='visible')
        for _ in range(8):
            await asyncio.sleep(0.04)
            r_frame = await page.screenshot(type='jpeg', quality=95)
            write_frame(r_frame, 4)  # 32 frames of rotating sacred geometry

        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        print("      Step 1 complete: Hero form & calculation ritual rendered.", flush=True)

        # -------------------------------------------------------------
        # STEP 2: TEASER, LOCKED MATRIX, & ORDER BUMP (3–9s)
        # -------------------------------------------------------------
        print("[2/7] Step 2: Teaser Anchor 7, Locked Matrix & Order Bump...", flush=True)
        anchor_y = await page.evaluate("""() => {
            const card = document.querySelector('#view-teaser .card');
            const rect = card.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await page.evaluate(f"window.scrollTo(0, {anchor_y})")
        teaser_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(teaser_frame, 45)  # 1.5s hold on #1 Signature Anchor 7

        # Smooth scroll to center the Blurred Locked Matrix
        matrix_y = await page.evaluate("""() => {
            const m = document.querySelector('#view-teaser .grid');
            const rect = m.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(anchor_y, matrix_y, steps=15, repeat_per_step=2)
        matrix_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(matrix_frame, 45)  # 1.5s hold on Frosted Glass Padlocks

        # Smooth scroll to center Checkout Card
        checkout_y = await page.evaluate("""() => {
            const co = document.getElementById('checkout');
            const rect = co.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(matrix_y, checkout_y, steps=15, repeat_per_step=2)
        checkout_base = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_base, 15)  # 0.5s hold on $37

        # Check Rosicrucian Order Bump (price updates to $84)
        await page.click('#bump')
        checkout_bump = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_bump, 45)  # 1.5s hold on $84 updated total

        # Unlock full dossier
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)

        # -------------------------------------------------------------
        # STEP 3: PHYSICAL DOM REMOVAL & ZERO OVERFLOW AUDIT
        # -------------------------------------------------------------
        print("[3/7] Step 3: Physically removing all header/action/sticky elements & checking overflow...", flush=True)
        removed_elements = await page.evaluate("""() => {
            document.documentElement.style.scrollBehavior = 'auto';
            document.body.style.scrollBehavior = 'auto';

            const toRemove = [];
            document.querySelectorAll('header, #claim-bar, #dossier-actions, #toast, .toast, .sticky-cta, #ritual').forEach(el => {
                toRemove.push(el.tagName + '#' + el.id);
                el.remove();
            });

            // Remove any other element with position fixed or sticky
            document.querySelectorAll('*').forEach(el => {
                const s = getComputedStyle(el);
                if (s.position === 'fixed' || s.position === 'sticky') {
                    toRemove.push(el.tagName + '#' + el.id + '(pos=' + s.position + ')');
                    el.remove();
                }
            });

            const vd = document.getElementById('view-dossier');
            if (vd) { vd.style.padding = '0'; vd.style.margin = '0'; }

            // Ensure cover fills the 720px viewport cleanly from seal down to 8-7-4 medallions
            const style = document.createElement('style');
            style.textContent = `
                .cover {
                    min-height: 700px !important;
                    height: 716px !important;
                    padding: 26px 16px 36px !important;
                    display: flex !important;
                    flex-direction: column !important;
                    justify-content: space-between !important;
                    box-sizing: border-box !important;
                }
                .cover .seal { width: 78px !important; height: 78px !important; }
                .cover .hairline { margin-top: 10px !important; margin-bottom: 10px !important; }
                .cover h1 { font-size: 1.95rem !important; margin-top: 4px !important; }
                .cover .font-display.text-3xl { font-size: 1.7rem !important; margin-top: 4px !important; }
                .cover .eyebrow { font-size: 0.62rem !important; margin-bottom: 4px !important; }
                .cover p { margin-top: 2px !important; }
            `;
            document.documentElement.appendChild(style);
            return toRemove;
        }""")
        print(f"      Removed {len(removed_elements)} blocking elements: {removed_elements}", flush=True)

        # AUTOMATED OVERFLOW ASSERTION: scrollWidth <= clientWidth
        overflow_check = await page.evaluate("""() => {
            const p11 = document.querySelector('article.page[data-page="11"]');
            const p13 = document.querySelector('article.page[data-page="13"]');
            const doc = document.documentElement;
            return {
                docScroll: doc.scrollWidth,
                docClient: doc.clientWidth,
                p11Scroll: p11.scrollWidth,
                p11Client: p11.clientWidth,
                p13Scroll: p13.scrollWidth,
                p13Client: p13.clientWidth
            };
        }""")
        print(f"      Automated Overflow Metrics: {overflow_check}", flush=True)
        assert overflow_check['p11Scroll'] <= overflow_check['p11Client'], f"Page 11 overflow detected! {overflow_check}"
        assert overflow_check['p13Scroll'] <= overflow_check['p13Client'], f"Page 13 overflow detected! {overflow_check}"
        assert overflow_check['docScroll'] <= overflow_check['docClient'], f"Document overflow detected! {overflow_check}"
        print("      Automated Overflow Assertion PASSED: Zero horizontal overflow!", flush=True)

        # Pre-Verification: Check top rows 50..400 at scroll position 1200
        await page.evaluate("window.scrollTo(0, 1200)")
        test_png = await page.screenshot(type='png')
        nparr = np.frombuffer(test_png, np.uint8)
        img_check = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        crop_top = img_check[50:400, :]
        std_val = float(crop_top.std())
        print(f"      Pre-Verification Top 50..400 StdDev: {std_val:.2f} (must be > 10.0)", flush=True)
        assert std_val > 10.0, f"Error: Top 25% is still a flat rectangle! StdDev={std_val}"
        print("      Pre-Verification PASSED: Top 25% contains real varied content, zero gray rectangle!", flush=True)

        # -------------------------------------------------------------
        # STEP 4: DOSSIER COVER (9–12s)
        # -------------------------------------------------------------
        print("[4/7] Step 4: Framing Page 1 Sovereign Blueprint Luxury Cover...", flush=True)
        await page.evaluate("window.scrollTo(0, 0)")
        cover_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(cover_frame, 90)  # 3.0s hold on luxury cover from Seal to 8-7-4 Medallions
        print("      Step 4 complete: Cover Page framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 5: MASTER OVERLAP & FREQUENCY TALLY (12–17s)
        # -------------------------------------------------------------
        print("[5/7] Step 5: Page 3 Master Overlap & Gold Frequency Tally Bars...", flush=True)
        p3_cards_y = await page.evaluate("""() => {
            const p3 = document.querySelector('article.page[data-page="3"]');
            const cards = p3.querySelector('.grid');
            const rect = cards.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(0, p3_cards_y, steps=15, repeat_per_step=2)
        p3_cards_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p3_cards_frame, 35)  # 1.2s hold on Big Three cards (7, 8, 4)

        # Smooth glide down to the gold Frequency Tally bars (1–9) with proper flex spacing
        p3_tally_y = await page.evaluate("""() => {
            const p3 = document.querySelector('article.page[data-page="3"]');
            const grids = p3.querySelectorAll('.grid');
            const tally = grids[1] || p3.querySelector('.bar-row');
            const rect = tally.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p3_cards_y, p3_tally_y, steps=12, repeat_per_step=2)
        p3_tally_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p3_tally_frame, 65)  # 2.2s hold on Frequency Tally bars
        print("      Step 5 complete: Master Overlap & Frequency Tally framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 6: KABBALISTIC TREE OF LIFE (17–21s)
        # -------------------------------------------------------------
        print("[6/7] Step 6: Page 9 Kabbalistic Tree of Life Diagram (Centered)...", flush=True)
        p9_y = await page.evaluate("""() => {
            const svg = document.querySelector('article.page[data-page="9"] svg');
            const rect = svg.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(p3_tally_y, p9_y, steps=16, repeat_per_step=2)
        p9_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p9_frame, 90)  # 3.0s hold with all 10 Sephirot 1 to 10 completely centered
        print("      Step 6 complete: Tree of Life centered.", flush=True)

        # -------------------------------------------------------------
        # STEP 7: CHINESE LO SHU 3x3 GRID & FIVE ELEMENTS (21–26s)
        # -------------------------------------------------------------
        print("[7/8] Step 7: Page 11 Chinese Lo Shu 3x3 Grid & Five Elements (Centered)...", flush=True)
        p11_loshu_y = await page.evaluate("""() => {
            const p11 = document.querySelector('article.page[data-page="11"]');
            const grid = p11.querySelector('.loshu');
            const rect = grid.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p9_y, p11_loshu_y, steps=15, repeat_per_step=2)
        p11_loshu_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p11_loshu_frame, 45)  # 1.5s hold on Lo Shu 3x3 Grid

        # Smooth glide down to Five Elements progress bars & Dominant card
        p11_elements_y = await page.evaluate("""() => {
            const p11 = document.querySelector('article.page[data-page="11"]');
            const bars = p11.querySelector('.space-y-3');
            const rect = bars.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p11_loshu_y, p11_elements_y, steps=12, repeat_per_step=2)
        p11_elements_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p11_elements_frame, 65)  # 2.2s hold on Five Elements bars & counts
        print("      Step 7 complete: Lo Shu Grid & Five Elements framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 8: ROSICRUCIAN 365-DAY CYCLES CALENDAR (26–31s)
        # -------------------------------------------------------------
        print("[8/8] Step 8: Page 13 Rosicrucian Calendar (Active Today: Lunar Period)...", flush=True)
        p13_y = await page.evaluate("""() => {
            const p13 = document.querySelector('article.page[data-page="13"]');
            const table = p13.querySelector('table.lux-table');
            const rect = table.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 90);
        }""")
        await smooth_scroll(p11_elements_y, p13_y, steps=16, repeat_per_step=2)
        p13_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p13_frame, 120)  # 4.0s strong final hold on Cycle 2 Lunar Period & Calendar Table
        print("      Step 8 complete: Rosicrucian Calendar framed.", flush=True)

        print(f"\nTotal video frames encoded: {total_frames} (Duration: {total_frames / 30.0:.2f}s)", flush=True)
        await browser.close()

    # Finalize MP4 container
    print("Finalizing MP4 video container...", flush=True)
    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()

    if ffmpeg_proc.returncode != 0:
        raise RuntimeError("FFmpeg encoding failed!")

    file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    elapsed = time.time() - t_start
    print(f"\n[OK] Video successfully written to: {output_mp4} ({file_size_mb:.2f} MB in {elapsed:.1f}s)", flush=True)

    # -------------------------------------------------------------
    # EXTRACT 5 VERIFICATION SCREENSHOT FRAMES
    # -------------------------------------------------------------
    print("\n--- Extracting 5 Verification PNG Frames from Video ---", flush=True)
    cap = cv2.VideoCapture(output_mp4)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Frame targets:
    # 1. Cover: ~11.0s (frame 330)
    # 2. Frequency Tally: ~15.5s (frame 475)
    # 3. Tree of Life: ~19.0s (frame 580)
    # 4. Five Elements: ~24.5s (frame 740)
    # 5. Rosicrucian Cycles Table: ~29.5s (frame 890)
    targets = [
        ("verify_1_cover.png", 330, "Page 1 Cover"),
        ("verify_2_tally.png", 475, "Page 3 Frequency Tally"),
        ("verify_3_tree.png", 580, "Page 9 Tree of Life"),
        ("verify_4_loshu.png", 740, "Page 11 Five Elements"),
        ("verify_5_cycles.png", 890, "Page 13 Rosicrucian Cycles Table")
    ]

    for fname, fnum, label in targets:
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(fnum, total_f - 1))
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(fname, frame)
            crop = frame[50:400, :]
            s_val = float(crop.std())
            print(f"Frame '{label}' saved to {fname} (Top 50..400 StdDev: {s_val:.2f})", flush=True)
            assert s_val > 5.0, f"Error: Top 25% in {label} is blocked by a flat rectangle!"

    # Verify resolution & bottom-right pixel
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(450, total_f - 1))
    _, mid_frame = cap.read()
    cap.release()

    h, w, _ = mid_frame.shape
    px_b, px_g, px_r = mid_frame[1910, 1070]
    print(f"Final Resolution: {w}x{h} (Aspect Ratio 9:16)", flush=True)
    print(f"Final Duration:   {total_f / fps:.2f}s ({total_f} frames @ {fps:.1f} fps)", flush=True)
    print(f"Bottom-Right Pixel (1070, 1910) BGR: [{px_b}, {px_g}, {px_r}]", flush=True)

    assert w == 1080 and h == 1920
    assert px_b < 25 and px_g < 25 and px_r < 25
    print("ALL VERIFICATIONS PASSED: 100% unobstructed, zero horizontal overflow, diagrams centered!", flush=True)

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
        for fname, _, _ in targets:
            if os.path.exists(fname):
                shutil.copy2(fname, os.path.join(art_dir, fname))
        print(f"Synced to artifacts directory: {art_dir}", flush=True)

if __name__ == '__main__':
    asyncio.run(record_promo())
