import asyncio
import os
import glob
import subprocess
import imageio_ffmpeg
from playwright.async_api import async_playwright

async def record_walkthrough():
    print("=== RECORDING 9:16 VERTICAL PROMO VIDEO ===")
    video_dir = os.path.abspath("videos")
    os.makedirs(video_dir, exist_ok=True)

    # Clean old videos in directory
    for f in glob.glob(os.path.join(video_dir, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg at: {ffmpeg_exe}")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()

        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            record_video_dir=video_dir,
            record_video_size={'width': 780, 'height': 1688}
        )

        page = await context.new_page()

        # Helper for buttery smooth easing scroll
        await page.add_init_script('''
            window.smoothScrollTo = function(targetY, durationMs) {
                return new Promise(resolve => {
                    const startY = window.scrollY;
                    const diff = targetY - startY;
                    const startTime = performance.now();
                    function step(now) {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / durationMs, 1);
                        const ease = progress < 0.5 ? 4 * progress * progress * progress : 1 - Math.pow(-2 * progress + 2, 3) / 2;
                        window.scrollTo(0, startY + diff * ease);
                        if (progress < 1) {
                            requestAnimationFrame(step);
                        } else {
                            resolve();
                        }
                    }
                    requestAnimationFrame(step);
                });
            };
        ''')

        # SECONDS 0 - 2: Landing Page Hero
        print("0-2s: Landing Page Hero...")
        await page.goto("http://127.0.0.1:8080/?vip=adam", wait_until="networkidle")
        await asyncio.sleep(1.5)

        # SECONDS 2 - 5: Fill Form
        print("2-5s: Typing name and birthday...")
        # Smoothly scroll down slightly to form
        await page.evaluate("window.smoothScrollTo(180, 500)")
        await asyncio.sleep(0.6)

        # Click Sample button to fill details cleanly with visual feedback
        await page.click('button[data-action="sample"]')
        await asyncio.sleep(1.0)

        # Click calculate button
        await page.evaluate("window.smoothScrollTo(320, 400)")
        await asyncio.sleep(0.5)
        await page.click('button[type="submit"]')

        # SECONDS 5 - 8: Calculation Ritual & Teaser Arrival
        print("5-8s: Calculation ritual and reveal...")
        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        await asyncio.sleep(1.5)

        # SECONDS 8 - 14: Scroll through 20% Free Teaser
        print("8-14s: Scrolling through 20% Free Teaser...")
        # Scroll to Anchor 1 medallion
        await page.evaluate("window.smoothScrollTo(350, 1000)")
        await asyncio.sleep(1.4)

        # Scroll to 5-System Matrix (frosted glass)
        await page.evaluate("window.smoothScrollTo(880, 1200)")
        await asyncio.sleep(1.5)

        # Scroll to Order Bump & Checkout
        await page.evaluate("window.smoothScrollTo(2100, 1200)")
        await asyncio.sleep(1.2)

        # Click the Rosicrucian 52-Day Cycles Order Bump checkbox (watch total update to $84!)
        bump_checkbox = page.locator('#bump')
        await bump_checkbox.click()
        await asyncio.sleep(1.5)

        # SECONDS 14 - 16: Unlock Full 15-Page Dossier
        print("14-16s: Unlocking Full Dossier via VIP founder button...")
        await page.evaluate("window.smoothScrollTo(2400, 600)")
        await asyncio.sleep(0.5)
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        await asyncio.sleep(1.2)

        # SECONDS 16 - 25: Scroll through 15-Page Dossier
        print("16-25s: Scrolling through luxury 15-Page Dossier...")
        # Cover page
        await page.evaluate("window.smoothScrollTo(400, 1000)")
        await asyncio.sleep(1.2)

        # Big Three Master Overlap & Harmonics
        await page.evaluate("window.smoothScrollTo(1950, 1200)")
        await asyncio.sleep(1.5)

        # Kabbalistic Tree of Life
        await page.evaluate("window.smoothScrollTo(7200, 1400)")
        await asyncio.sleep(1.8)

        # Chinese Lo Shu 3x3 Magic Square & Five Elements
        await page.evaluate("window.smoothScrollTo(8900, 1400)")
        await asyncio.sleep(1.8)

        # Rosicrucian 365-Day Cycles Calendar
        await page.evaluate("window.smoothScrollTo(10600, 1400)")
        await asyncio.sleep(1.8)

        # SECONDS 25 - 28: Toggle to Spanish (EN | ES)
        print("25-28s: Scrolling to top and toggling EN | ES...")
        await page.evaluate("window.smoothScrollTo(0, 1000)")
        await asyncio.sleep(1.2)

        # Click Spanish toggle
        await page.click('button[data-lang="es"]')
        print("Toggled to Spanish!")
        await asyncio.sleep(1.8)

        # Quick smooth scroll down to show Spanish Cover & Overlap
        await page.evaluate("window.smoothScrollTo(500, 800)")
        await asyncio.sleep(1.5)

        # Finish recording
        print("Closing context to finalize video recording...")
        await page.close()
        await context.close()
        await browser.close()

    # Find the recorded video file
    video_files = glob.glob(os.path.join(video_dir, "*.webm"))
    if not video_files:
        raise RuntimeError("No video recorded by Playwright!")

    raw_video = video_files[0]
    output_mp4 = os.path.abspath("tiktok_promo_1.mp4")
    print(f"Recorded raw video: {raw_video}")

    # Convert with ffmpeg to standard high-quality MP4 (H.264 / AAC) at 1080x1920 9:16
    print(f"Encoding to {output_mp4} with ffmpeg...")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", raw_video,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x0A0A0C,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-r", "30",
        "-movflags", "+faststart",
        output_mp4
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("FFmpeg error:", proc.stderr)
        raise RuntimeError("FFmpeg encoding failed!")

    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"SUCCESS! Promo video created: {output_mp4} ({size_mb:.2f} MB)")

    # Also copy to Google Drive folder if available
    gdrive_dir = r"G:\My Drive\5_System_Numerology_MVP"
    if os.path.exists(gdrive_dir):
        dest = os.path.join(gdrive_dir, "tiktok_promo_1.mp4")
        import shutil
        shutil.copy2(output_mp4, dest)
        print(f"Copied promo video to Google Drive: {dest}")

if __name__ == '__main__':
    asyncio.run(record_walkthrough())
