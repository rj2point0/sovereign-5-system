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
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3.0)
        refresh_btn = page.locator('button:text-is("Refresh")').first
        if await refresh_btn.count() > 0 and await refresh_btn.is_visible():
            await refresh_btn.click()
            await asyncio.sleep(3.5)
        try:
            await page.locator('a[href*="/video/"]').first.wait_for(state="attached", timeout=20000)
        except Exception:
            pass
        await asyncio.sleep(3.5)

        # Scroll down a couple times so all 20 videos are attached in the profile grid
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 700)")
            await asyncio.sleep(1.0)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.0)

        for vid in TOP_3_VIDEO_IDS:
            card_loc = page.locator('[data-e2e="user-post-item"]', has=page.locator(f'a[href*="{vid}"]')).first
            if await card_loc.count() == 0:
                print(f"  ⚠ Could not find video {vid} on profile grid")
                continue

            await card_loc.scroll_into_view_if_needed()
            await asyncio.sleep(0.8)
            await card_loc.click()
            try:
                await page.locator('[data-e2e="browse-close"]').first.wait_for(state="visible", timeout=10000)
            except Exception:
                await card_loc.click(force=True)
                await asyncio.sleep(3.5)
            await asyncio.sleep(2.5)

            # Find the creator three-dots menu in the right panel next to the creator name (NOT browse-ellipsis on the player!)
            dots_pt = await page.evaluate(
                """() => {
                    const settingEl = document.querySelector('[data-e2e="video-setting"]');
                    if (settingEl) {
                        const r = settingEl.getBoundingClientRect();
                        if (r.width > 0 && r.left > 750) return {x: r.left + r.width / 2, y: r.top + r.height / 2, how: 'data-e2e:video-setting'};
                    }
                    const svgs = Array.from(document.querySelectorAll('svg'));
                    for (const s of svgs) {
                        const r = s.getBoundingClientRect();
                        if (r.left > 1000 && r.top > 25 && r.top < 120 && r.width >= 14 && r.width <= 40) {
                            return {x: r.left + r.width / 2, y: r.top + r.height / 2, how: 'right-card-svg'};
                        }
                    }
                    const creatorLinks = Array.from(document.querySelectorAll('a[href*="/@sacrednumberblueprint"]'));
                    for (const cl of creatorLinks) {
                        const cr = cl.getBoundingClientRect();
                        if (cr.top > 15 && cr.top < 150 && cr.left > 750) {
                            const row = cl.parentElement && cl.parentElement.parentElement ? cl.parentElement.parentElement : cl.parentElement;
                            if (row) {
                                const rr = row.getBoundingClientRect();
                                return {
                                    x: rr.right - 22,
                                    y: rr.top + 24,
                                    how: 'creator-row-right',
                                };
                            }
                        }
                    }
                    return null;
                }"""
            )
            if dots_pt:
                print(f"  [Video {vid}] Found creator menu icon at ({dots_pt['x']:.0f}, {dots_pt['y']:.0f}) via {dots_pt['how']}")
                await page.mouse.move(dots_pt["x"], dots_pt["y"])
                await asyncio.sleep(1.5)
                await page.mouse.click(dots_pt["x"], dots_pt["y"])
                await asyncio.sleep(1.5)
                await page.screenshot(path=f"pin_menu_{vid}.png")
                pin_opt = page.locator('li:has-text("Pin"), button:has-text("Pin"), [role="menuitem"]:has-text("Pin"), span:has-text("Pin"), div:text-is("Pin"), div:text-is("Pin to top")').first
                if await pin_opt.count() > 0:
                    txt = await pin_opt.inner_text()
                    if "Unpin" not in txt:
                        await pin_opt.click(force=True)
                        print(f"  ✓ Clicked Pin on video {vid} (menu text: {txt.strip()})")
                        await asyncio.sleep(3.0)
                    else:
                        print(f"  ✓ Video {vid} already pinned (menu text: {txt.strip()})")
                else:
                    pop_txt = await page.evaluate("""() => Array.from(document.querySelectorAll('ul, [role="menu"], [class*="Popup"], [class*="Action"]')).map(el => (el.innerText || '').replace(/\\s+/g, ' ').trim()).filter(Boolean)""")
                    print(f"  ⚠ No Pin option visible for {vid}; menus={pop_txt[:5]}")
            else:
                print(f"  ⚠ dots_pt was null for {vid}")

            close_btn = page.locator('[data-e2e="browse-close"]').first
            if await close_btn.count() > 0:
                await close_btn.click(force=True)
            else:
                await page.keyboard.press("Escape")
            await asyncio.sleep(1.5)

        # Reload profile to verify Display Name, Bio, and Top Grid Order
        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3.0)
        refresh_btn = page.locator('button:text-is("Refresh")').first
        if await refresh_btn.count() > 0 and await refresh_btn.is_visible():
            await refresh_btn.click()
            await asyncio.sleep(3.5)
        try:
            await page.locator('a[href*="/video/"]').first.wait_for(state="attached", timeout=20000)
        except Exception:
            pass
        await asyncio.sleep(3.5)
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 700)")
            await asyncio.sleep(0.8)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1.0)
        await page.screenshot(path="tiktok_profile_pinned_verified.png")

        prof_audit = await page.evaluate(
            """() => {
                const displayName = (document.querySelector('[data-e2e="user-subtitle"]') || {}).innerText || '';
                const userTitle = (document.querySelector('[data-e2e="user-title"]') || {}).innerText || '';
                const bio = (document.querySelector('[data-e2e="user-bio"]') || {}).innerText || '';
                const cards = Array.from(document.querySelectorAll('[data-e2e="user-post-item"]')).slice(0, 18).map(c => {
                    const a = c.querySelector('a[href*="/video/"]');
                    const href = a ? a.href : '';
                    const vid = (href.match(/video\\/(\\d+)/) || [])[1] || '';
                    const views = (c.querySelector('[data-e2e="video-views"]') || {}).innerText || '';
                    const text = (c.innerText || '').replace(/\\s+/g, ' ').trim();
                    const imgAlt = a && a.querySelector('img') ? (a.querySelector('img').alt || '').slice(0, 48) : '';
                    return {vid, views, pinned: text.toLowerCase().includes('pinned'), text, imgAlt};
                });
                return {displayName, userTitle, bio, cards};
            }"""
        )
        print(f"\n[Profile Audit] Title: {prof_audit['userTitle']!r} | Subtitle/Name: {prof_audit['displayName']!r} | Bio: {prof_audit['bio']!r}")
        for idx, c in enumerate(prof_audit["cards"], 1):
            print(f"  Grid #{idx}: vid={c['vid']} | pinned={c['pinned']} | views={c['views']} | {c['imgAlt']}")

        # Check TikTok Studio Content table for views/likes/comments across short_10..short_18
        await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.5)
        for scroll_i in range(3):
            await page.mouse.wheel(0, 700)
            await asyncio.sleep(1.5)
            await page.screenshot(path=f"tiktok_studio_scroll_{scroll_i+1}.png")
        studio_text = await page.evaluate("() => document.body.innerText")
        lines = [ln.strip() for ln in studio_text.splitlines() if ln.strip()]
        print("\n[TikTok Studio Posts Text Lines]")
        print(" | ".join(lines[:90]))

        await ctx.close()


if __name__ == "__main__":
    asyncio.run(pin_top_videos())
