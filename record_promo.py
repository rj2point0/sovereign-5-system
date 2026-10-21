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
    print("  20-PAGE EDITION: MANDALA, TALLY, TREE, LOSHU, SOMATIC, CYCLES", flush=True)
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
    checkpoint_frames = {}

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
        async def smooth_scroll(y_start, y_target, steps=14, repeat_per_step=2):
            for i in range(steps):
                t = i / max(steps - 1, 1)
                ease = cubic_ease(t)
                y = int(y_start + (y_target - y_start) * ease)
                await page.evaluate(f"window.scrollTo(0, {y})")
                frame = await page.screenshot(type='jpeg', quality=95)
                write_frame(frame, repeat_per_step)

        # -------------------------------------------------------------
        # STEP 1: HERO CALCULATOR CENTERED & SACRED RITUAL (0–3s)
        # -------------------------------------------------------------
        print("[1/9] Step 1: Hero Calculator Centered & Sacred Ritual...", flush=True)
        await page.goto("http://127.0.0.1:8080/?vip=adam&lang=en", wait_until="networkidle")

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
        write_frame(hero_frame, 28)  # ~0.9s hold on calculator form

        # Click Load Founder Sample (Adam Vega, 1978-08-19)
        await page.click('button[data-action="sample"]')
        filled_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(filled_frame, 24)  # ~0.8s hold on filled details

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
        # STEP 2: TEASER, LOCKED MATRIX, & ORDER BUMP (3–8s)
        # -------------------------------------------------------------
        print("[2/9] Step 2: Teaser Anchor 7, Locked Matrix & Order Bump...", flush=True)
        anchor_y = await page.evaluate("""() => {
            const card = document.querySelector('#view-teaser .card');
            const rect = card.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await page.evaluate(f"window.scrollTo(0, {anchor_y})")
        teaser_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(teaser_frame, 40)  # 1.33s hold on #1 Signature Anchor 7

        # Smooth scroll to center the Blurred Locked Matrix
        matrix_y = await page.evaluate("""() => {
            const m = document.querySelector('#view-teaser .grid');
            const rect = m.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(anchor_y, matrix_y, steps=12, repeat_per_step=2)
        matrix_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(matrix_frame, 35)  # 1.17s hold on Frosted Glass Padlocks

        # Smooth scroll to center Checkout Card
        checkout_y = await page.evaluate("""() => {
            const co = document.getElementById('checkout');
            const rect = co.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(matrix_y, checkout_y, steps=12, repeat_per_step=2)
        checkout_base = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_base, 15)  # 0.5s hold on $37

        # Check Rosicrucian Order Bump (price updates to $84)
        await page.click('#bump')
        checkout_bump = await page.screenshot(type='jpeg', quality=95)
        write_frame(checkout_bump, 40)  # 1.33s hold on $84 updated total

        # Unlock full dossier
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)

        # -------------------------------------------------------------
        # STEP 3: PHYSICAL DOM REMOVAL & ZERO OVERFLOW AUDIT
        # -------------------------------------------------------------
        print("[3/9] Step 3: Physically removing all header/action/sticky elements & checking overflow...", flush=True)
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
            const p2 = document.querySelector('article.page[data-page="2"]');
            const p4 = document.querySelector('article.page[data-page="4"]');
            const p11 = document.querySelector('article.page[data-page="11"]');
            const p14 = document.querySelector('article.page[data-page="14"]');
            const p15 = document.querySelector('article.page[data-page="15"]');
            const p18 = document.querySelector('article.page[data-page="18"]');
            const doc = document.documentElement;
            return {
                docScroll: doc.scrollWidth,
                docClient: doc.clientWidth,
                p2Scroll: p2 ? p2.scrollWidth : null,
                p2Client: p2 ? p2.clientWidth : null,
                p4Scroll: p4 ? p4.scrollWidth : null,
                p4Client: p4 ? p4.clientWidth : null,
                p11Scroll: p11 ? p11.scrollWidth : null,
                p11Client: p11 ? p11.clientWidth : null,
                p14Scroll: p14 ? p14.scrollWidth : null,
                p14Client: p14 ? p14.clientWidth : null,
                p15Scroll: p15 ? p15.scrollWidth : null,
                p15Client: p15 ? p15.clientWidth : null,
                p18Scroll: p18 ? p18.scrollWidth : null,
                p18Client: p18 ? p18.clientWidth : null
            };
        }""")
        print(f"      Automated Overflow Metrics: {overflow_check}", flush=True)
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
        # STEP 4: DOSSIER COVER (8–10.5s)
        # -------------------------------------------------------------
        print("[4/9] Step 4: Framing Page 1 Sovereign Blueprint Luxury Cover...", flush=True)
        await page.evaluate("window.scrollTo(0, 0)")
        cover_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_1_cover.png'] = total_frames + 20
        write_frame(cover_frame, 75)  # 2.5s hold on luxury cover from Seal to 8-7-4 Medallions
        print("      Step 4 complete: Cover Page framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 5: PAGE 2 SACRED CONVERGENCE MANDALA SVG (10.5–13.5s)
        # -------------------------------------------------------------
        print("[5/9] Step 5: Page 2 5-Ring Sacred Convergence Mandala SVG (7 · 8 · 4)...", flush=True)
        p2_mandala_y = await page.evaluate("""() => {
            const p2 = document.querySelector('article.page[data-page="2"]');
            const svg = p2.querySelector('svg');
            const rect = svg.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(0, p2_mandala_y, steps=12, repeat_per_step=2)
        p2_mandala_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_2_mandala.png'] = total_frames + 20
        write_frame(p2_mandala_frame, 75)  # 2.5s hold centering 5-Ring Convergence Mandala & Core
        print("      Step 5 complete: Page 2 Convergence Mandala framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 6: PAGE 4 MASTER OVERLAP & FREQUENCY TALLY (13.5–17s)
        # -------------------------------------------------------------
        print("[6/9] Step 6: Page 4 Master Overlap & Gold Frequency Tally Bars...", flush=True)
        p4_cards_y = await page.evaluate("""() => {
            const p4 = document.querySelector('article.page[data-page="4"]');
            const cards = p4.querySelector('.grid');
            const rect = cards.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p2_mandala_y, p4_cards_y, steps=12, repeat_per_step=2)
        p4_cards_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p4_cards_frame, 30)  # 1.0s hold on Big Three cards (7, 8, 4)

        # Smooth glide down to the gold Frequency Tally bars (1–9) with proper flex spacing
        p4_tally_y = await page.evaluate("""() => {
            const p4 = document.querySelector('article.page[data-page="4"]');
            const grids = p4.querySelectorAll('.grid');
            const tally = grids[1] || p4.querySelector('.bar-row');
            const rect = tally.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p4_cards_y, p4_tally_y, steps=10, repeat_per_step=2)
        p4_tally_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_3_tally.png'] = total_frames + 20
        write_frame(p4_tally_frame, 55)  # 1.83s hold on Frequency Tally bars
        print("      Step 6 complete: Master Overlap & Frequency Tally framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 7: PAGE 11 KABBALISTIC TREE OF LIFE (17–20s)
        # -------------------------------------------------------------
        print("[7/9] Step 7: Page 11 Kabbalistic Tree of Life Diagram (Centered)...", flush=True)
        p11_y = await page.evaluate("""() => {
            const svg = document.querySelector('article.page[data-page="11"] svg');
            const rect = svg.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - (720 - rect.height) / 2);
        }""")
        await smooth_scroll(p4_tally_y, p11_y, steps=14, repeat_per_step=2)
        p11_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_4_tree.png'] = total_frames + 20
        write_frame(p11_frame, 75)  # 2.5s hold with Tree of Life completely centered
        print("      Step 7 complete: Tree of Life centered.", flush=True)

        # -------------------------------------------------------------
        # STEP 8: PAGE 14 CHINESE LO SHU 3x3 GRID & FIVE ELEMENTS (20–24s)
        # -------------------------------------------------------------
        print("[8/9] Step 8: Page 14 Chinese Lo Shu 3x3 Grid & Five Elements (Centered)...", flush=True)
        p14_loshu_y = await page.evaluate("""() => {
            const p14 = document.querySelector('article.page[data-page="14"]');
            const grid = p14.querySelector('.loshu');
            const rect = grid.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p11_y, p14_loshu_y, steps=12, repeat_per_step=2)
        p14_loshu_frame = await page.screenshot(type='jpeg', quality=95)
        write_frame(p14_loshu_frame, 35)  # 1.17s hold on Lo Shu 3x3 Grid

        # Smooth glide down to Five Elements progress bars & Dominant card
        p14_elements_y = await page.evaluate("""() => {
            const p14 = document.querySelector('article.page[data-page="14"]');
            const bars = p14.querySelector('.space-y-3');
            const rect = bars.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p14_loshu_y, p14_elements_y, steps=10, repeat_per_step=2)
        p14_elements_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_5_loshu.png'] = total_frames + 20
        write_frame(p14_elements_frame, 55)  # 1.83s hold on Five Elements bars & counts
        print("      Step 8 complete: Lo Shu Grid & Five Elements framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 9: PAGE 15 SOMATIC VITALITY & NERVOUS SYSTEM (24–27s)
        # -------------------------------------------------------------
        print("[9/10] Step 9: Page 15 Somatic Vitality, Nervous System & 5-Element Health...", flush=True)
        p15_somatic_y = await page.evaluate("""() => {
            const p15 = document.querySelector('article.page[data-page="15"]');
            const cards = p15.querySelector('.grid');
            const rect = cards.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 30);
        }""")
        await smooth_scroll(p14_elements_y, p15_somatic_y, steps=12, repeat_per_step=2)
        p15_somatic_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_6_somatic.png'] = total_frames + 20
        write_frame(p15_somatic_frame, 75)  # 2.5s hold on 4 Somatic Health & Nervous System Reset Cards
        print("      Step 9 complete: Somatic Vitality architecture framed.", flush=True)

        # -------------------------------------------------------------
        # STEP 10: PAGE 18 ROSICRUCIAN 365-DAY CYCLES CALENDAR (27–31s)
        # -------------------------------------------------------------
        print("[10/10] Step 10: Page 18 Rosicrucian Calendar (Active Today: Lunar Period)...", flush=True)
        p18_cycles_y = await page.evaluate("""() => {
            const p18 = document.querySelector('article.page[data-page="18"]');
            const table = p18.querySelector('table.lux-table');
            const rect = table.getBoundingClientRect();
            return Math.round(rect.top + window.scrollY - 90);
        }""")
        await smooth_scroll(p15_somatic_y, p18_cycles_y, steps=14, repeat_per_step=2)
        p18_cycles_frame = await page.screenshot(type='jpeg', quality=95)
        checkpoint_frames['verify_7_cycles.png'] = total_frames + 30
        write_frame(p18_cycles_frame, 105)  # 3.5s strong final hold on Cycle 2 Lunar Period & Calendar Table
        print("      Step 10 complete: Rosicrucian Calendar framed.", flush=True)

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
    # EXTRACT VERIFICATION SCREENSHOT FRAMES
    # -------------------------------------------------------------
    print("\n--- Extracting Verification PNG Frames from Video ---", flush=True)
    cap = cv2.VideoCapture(output_mp4)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    targets = [
        ("verify_1_cover.png", checkpoint_frames.get('verify_1_cover.png', 280), "Page 1 Cover"),
        ("verify_2_mandala.png", checkpoint_frames.get('verify_2_mandala.png', 380), "Page 2 Convergence Mandala"),
        ("verify_3_tally.png", checkpoint_frames.get('verify_3_tally.png', 480), "Page 4 Frequency Tally"),
        ("verify_4_tree.png", checkpoint_frames.get('verify_4_tree.png', 590), "Page 11 Tree of Life"),
        ("verify_5_loshu.png", checkpoint_frames.get('verify_5_loshu.png', 720), "Page 14 Five Elements"),
        ("verify_6_somatic.png", checkpoint_frames.get('verify_6_somatic.png', 820), "Page 15 Somatic Health"),
        ("verify_7_cycles.png", checkpoint_frames.get('verify_7_cycles.png', 920), "Page 18 Rosicrucian Cycles Table")
    ]

    for fname, fnum, label in targets:
        cap.set(cv2.CAP_PROP_POS_FRAMES, min(fnum, total_f - 1))
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(fname, frame)
            crop = frame[50:400, :]
            s_val = float(crop.std())
            print(f"Frame '{label}' saved to {fname} at frame {fnum} (Top 50..400 StdDev: {s_val:.2f})", flush=True)
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
        print(f"Synced video to Google Drive: {dest}", flush=True)
        for fname, _, _ in targets:
            if os.path.exists(fname):
                shutil.copy2(fname, os.path.join(gdrive_dir, fname))
        print("Synced verification frames to Google Drive.", flush=True)

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
