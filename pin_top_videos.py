"""
=============================================================================
SACRED NUMBER BLUEPRINT · TOP 3 TIKTOK VIDEO PINNER
pin_top_videos.py
Pins our top 3 highest-performing videos (short_02, short_10, short_11)
to the top of https://www.tiktok.com/@sacrednumberblueprint.
=============================================================================
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "tiktok_browser_profile")
TOP_3_VIDEO_IDS = [
    "7700014647599992077",  # short_02 (217+ views)
    "7702232648323812622",  # short_10 (132+ views)
    "7702232880092597518",  # short_11 (128+ views)
]


async def pin_top_videos():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1440, "height": 960},
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        try:
            await page.locator('a[href*="/video/"]').first.wait_for(state="attached", timeout=20000)
        except Exception:
            pass
        await asyncio.sleep(3.5)

        for vid in TOP_3_VIDEO_IDS:
            box = None
            for _ in range(5):
                box = await page.evaluate(
                    """(v) => {
                        const a = document.querySelector(`a[href*="${v}"]`);
                        if (!a) return null;
                        const card = a.closest('[data-e2e="user-post-item"]') || a.parentElement || a;
                        card.scrollIntoView({block: 'center'});
                        const r = card.getBoundingClientRect();
                        return {x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width};
                    }""",
                    vid,
                )
                if box and box["w"] > 20:
                    break
                await page.evaluate("window.scrollBy(0, 600)")
                await asyncio.sleep(1.0)

            if not box:
                continue

            await asyncio.sleep(0.5)
            box = await page.evaluate(
                """(v) => {
                    const a = document.querySelector(`a[href*="${v}"]`);
                    const card = a.closest('[data-e2e="user-post-item"]') || a.parentElement || a;
                    const r = card.getBoundingClientRect();
                    return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                }""",
                vid,
            )
            await page.mouse.click(box["x"], box["y"])
            await asyncio.sleep(4.0)

            menu_btn = page.locator('[data-e2e="browse-ellipsis"], [data-e2e="video-setting"]').first
            if await menu_btn.count() > 0:
                await menu_btn.hover()
                await asyncio.sleep(1.0)
                await menu_btn.click()
                await asyncio.sleep(1.2)
                pin_opt = page.locator('li:has-text("Pin"), button:has-text("Pin"), [role="menuitem"]:has-text("Pin"), span:has-text("Pin to top")').first
                if await pin_opt.count() > 0:
                    txt = await pin_opt.inner_text()
                    if "Unpin" not in txt:
                        await pin_opt.click()
                        print(f"  ✓ Pinned video {vid}")
                        await asyncio.sleep(2.0)
                    else:
                        print(f"  ✓ Video {vid} already pinned")

            close_btn = page.locator('[data-e2e="browse-close"]').first
            if await close_btn.count() > 0:
                await close_btn.click()
            else:
                await page.keyboard.press("Escape")
            await asyncio.sleep(1.5)
            await page.evaluate("window.scrollTo(0, 0)")

        await ctx.close()


if __name__ == "__main__":
    asyncio.run(pin_top_videos())
