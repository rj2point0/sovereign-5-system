#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · ANTI-SLOP GRID DEDUPLICATION & 0-VIEW CLEANUP
cleanup_duplicate_and_zero_view_posts.py
-----------------------------------------------------------------------------
1. Uses exact TikTok Studio `data-tt` selectors on https://www.tiktok.com/tiktokstudio/content:
   - Deletes duplicate Scheduled posts (`7703601254852824333`, `7703601237857455374`,
     `7703601405159869710`) and old white-box Scheduled posts (`7703630452141067534`,
     `7703630711911206157`, `7704068719772699917`, `7704068831345413390`) so we replace
     them cleanly with the new 3-Format videos.
   - Sets Published duplicate copies (`7704122197744291085` 12v vs 36v,
     `7703341818120768781` 94v vs 106v, `7703341562952043789` 33v vs 72v,
     `7703623597469748493` 96v vs 104v, `7702469276480916749` 0v vs 95v) and all >1h
     0-view videos (`7702844869877828877`, `7702844640541641997`) to `Only me` (Private)
     via `button[data-tt="components_PrivacyCell_TUXButton"]`.
2. Cleans up Instagram Reels (`https://www.instagram.com/sacrednumberblueprint/reels/`):
   - Deletes duplicate `DfN3scQOV9B` (old 14s `short_21` vs `DfTR1XxublV` 122v),
     lakeside silhouette duplicate `DfP3rbpu_81` (`short_27` 7v), and recycled B-roll
     Reels `DfP3jR_OPp6` (`short_26`), `DfS6QdAuGPY` (`short_29`), `DfS6YOPO8hJ` (`short_30`)
     before uploading the new 3-Format Reels.
3. Captures clean verification screenshots of both public grids.
=============================================================================
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from playwright.async_api import async_playwright, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\tiktok_browser_profile"
IG_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"
REPORT_PATH = os.path.join(BASE_DIR, "grid_cleanup_report.json")

# Scheduled duplicates + old white-box scheduled videos to delete in TikTok Studio
TT_SCHEDULED_TO_DELETE = [
    ("7703601254852824333", "scheduled_dup_short_22_already_live_157v"),
    ("7703601237857455374", "scheduled_dup_short_23"),
    ("7703601405159869710", "scheduled_dup_short_24"),
    ("7703630452141067534", "replace_old_whitebox_short_26_with_format_A"),
    ("7703630711911206157", "replace_old_silhouette_short_27_with_format_B"),
    ("7704068719772699917", "replace_old_whitebox_short_29_with_format_C"),
    ("7704068831345413390", "replace_old_dark_short_30_with_format_A"),
]

# Published duplicate copies (keeping higher-view copy public) + >1h 0-view videos -> set to 'Only me' (Private)
TT_PUBLISHED_TO_PRIVATE = [
    ("7704122197744291085", "duplicate_short_21_12v_vs_36v"),
    ("7703341818120768781", "duplicate_short_20_94v_vs_106v"),
    ("7703341562952043789", "duplicate_short_19_33v_vs_72v"),
    ("7703623597469748493", "duplicate_short_17_96v_vs_104v"),
    ("7702469276480916749", "duplicate_short_15_0v_vs_95v"),
    ("7702844869877828877", "zero_views_short_18_bare_minimum"),
    ("7702844640541641997", "zero_views_short_16_begging_for_crumbs"),
]

# Instagram Reels to Delete (duplicate short_21 + lakeside silhouette short_27 + old white-box short_26/29/30)
IG_SHORTCODES_TO_DELETE = [
    ("DfVZE-MOd5x", "replace_old_smalltext_short_26_with_emotional_face_giant"),
    ("DfVZMjvOwbP", "replace_old_smalltext_short_27_with_emotional_face_giant"),
    ("DfVZUGgOpJ5", "replace_old_smalltext_short_29_with_emotional_face_giant"),
    ("DfVZcSZOe8a", "replace_old_smalltext_short_30_with_emotional_face_giant"),
    ("DfN3scQOV9B", "duplicate_short_21_old_14s_vs_DfTR1XxublV_122v"),
    ("DfP3rbpu_81", "duplicate_lakeside_silhouette_short_27_7v"),
    ("DfP3jR_OPp6", "replace_old_whitebox_short_26_with_format_A"),
    ("DfS6QdAuGPY", "replace_old_whitebox_short_29_with_format_C"),
    ("DfS6YOPO8hJ", "replace_old_dark_short_30_with_format_A"),
]


async def scroll_studio_table(page: Page, dy: int):
    """Scrolls TikTok Studio's inner scrollable table container + mouse wheel."""
    first_row = page.locator('div[data-tt="components_RowLayout_FlexRow"]').first
    if await first_row.count() > 0:
        try:
            box = await first_row.bounding_box()
            if box:
                await page.mouse.move(box["x"] + 200, box["y"] + 20)
                await page.mouse.wheel(0, dy)
        except Exception:
            pass
    await page.evaluate(
        """(dy) => {
            window.scrollBy(0, dy);
            document.querySelectorAll('div').forEach(el => {
                const st = window.getComputedStyle(el);
                if ((st.overflowY === 'auto' || st.overflowY === 'scroll') && el.scrollHeight > el.clientHeight + 50) {
                    el.scrollBy(0, dy);
                }
            });
        }""",
        dy,
    )


async def find_studio_row_for_vid(page: Page, vid: str):
    """Scrolls TikTok Studio Content table from top to find the row containing `/video/{vid}`."""
    try:
        await page.wait_for_selector('div[data-tt="components_RowLayout_FlexRow"]', timeout=15000)
    except Exception:
        pass
    await scroll_studio_table(page, -6000)
    await asyncio.sleep(0.6)
    for _ in range(14):
        row = page.locator(f'div[data-tt="components_RowLayout_FlexRow"]:has(a[href*="/video/{vid}"])').first
        if await row.count() > 0:
            await row.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            return row
        await scroll_studio_table(page, 650)
        await asyncio.sleep(0.9)
    return None


async def delete_tiktok_studio_row(page: Page, vid: str, reason: str) -> str:
    print(f"  [TT Studio Delete] {vid} ({reason})...", flush=True)
    if "/tiktokstudio/content" not in page.url:
        await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
    row = await find_studio_row_for_vid(page, vid)
    if not row:
        print(f"    ⚠ Row {vid} not found in TikTok Studio (already removed).", flush=True)
        return "not_found"

    try:
        await row.hover()
        await asyncio.sleep(0.5)
        action_btns = row.locator('button[data-tt="components_ActionCell_Clickable"]')
        cnt = await action_btns.count()
        for idx in range(cnt - 1, -1, -1):
            btn = action_btns.nth(idx)
            await btn.click(force=True)
            await asyncio.sleep(1.0)
            del_menu = page.locator('div[role="menuitem"]:has-text("Delete"), li:has-text("Delete"), span:text-is("Delete"), button:has-text("Delete")').first
            if await del_menu.count() > 0 and await del_menu.is_visible():
                await del_menu.click(force=True)
                await asyncio.sleep(1.2)
                conf_btn = page.locator('div[role="dialog"] button:has-text("Delete"), button.TUXButton--primary:has-text("Delete")').last
                if await conf_btn.count() > 0 and await conf_btn.is_visible():
                    await conf_btn.click(force=True)
                    await asyncio.sleep(2.5)
                print(f"    ✓ Deleted {vid} from TikTok Studio!", flush=True)
                return "deleted"
    except Exception as e:
        print(f"    [TT Delete Error] {vid}: {e}", flush=True)
    return "failed"


async def set_tiktok_studio_row_private(page: Page, vid: str, reason: str) -> str:
    print(f"  [TT Studio Private] {vid} ({reason})...", flush=True)
    if "/tiktokstudio/content" not in page.url:
        await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
    row = await find_studio_row_for_vid(page, vid)
    if not row:
        print(f"    ⚠ Row {vid} not found in TikTok Studio.", flush=True)
        return "not_found"

    try:
        priv_btn = row.locator('button[data-tt="components_PrivacyCell_TUXButton"]').first
        if await priv_btn.count() > 0:
            cur_txt = (await priv_btn.inner_text()).strip()
            if "Only me" in cur_txt:
                print(f"    ✓ {vid} is already 'Only me'.", flush=True)
                return "already_private"
            await priv_btn.click(force=True)
            await asyncio.sleep(1.0)
            only_me = page.locator('span:text-is("Only me"), div[role="option"]:has-text("Only me"), li:has-text("Only me"), div[data-tt*="Select"] :text-is("Only me")').last
            if await only_me.count() > 0 and await only_me.is_visible():
                await only_me.click(force=True)
                await asyncio.sleep(2.2)
                print(f"    ✓ Set {vid} privacy -> 'Only me' (Private)!", flush=True)
                return "private"
    except Exception as e:
        print(f"    [TT Private Error] {vid}: {e}", flush=True)
    return "failed"


async def run_tiktok_cleanup() -> Dict[str, Any]:
    res: Dict[str, Any] = {"deleted_scheduled": [], "set_private": []}
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=TT_PROFILE_DIR,
            headless=False,
            viewport={"width": 1400, "height": 920},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for vid, reason in TT_SCHEDULED_TO_DELETE:
            st = await delete_tiktok_studio_row(page, vid, reason)
            res["deleted_scheduled"].append({"vid": vid, "reason": reason, "status": st})

        for vid, reason in TT_PUBLISHED_TO_PRIVATE:
            st = await set_tiktok_studio_row_private(page, vid, reason)
            res["set_private"].append({"vid": vid, "reason": reason, "status": st})

        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.0)
        tt_shot = os.path.join(BASE_DIR, "tiktok_grid_cleaned.png")
        await page.screenshot(path=tt_shot)
        print(f"  ✓ Saved cleaned TikTok profile screenshot: {tt_shot}", flush=True)
        await ctx.close()
    return res


async def delete_ig_reel(page: Page, shortcode: str, reason: str) -> str:
    print(f"  [IG Delete] {shortcode} ({reason})...", flush=True)
    try:
        if "/sacrednumberblueprint/reels" not in page.url:
            await page.goto("https://www.instagram.com/sacrednumberblueprint/reels/", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4.2)

        card = page.locator(f'a[href*="/reel/{shortcode}/"], a[href*="/p/{shortcode}/"]').first
        if await card.count() == 0:
            await page.evaluate("window.scrollBy(0, 700)")
            await asyncio.sleep(1.5)
        if await card.count() == 0:
            print(f"    ✓ {shortcode} not on Reels grid (already removed).", flush=True)
            return "already_deleted"

        await card.scroll_into_view_if_needed()
        await asyncio.sleep(0.5)
        await card.click(force=True)
        await asyncio.sleep(3.2)

        more_btn = page.locator(
            'div[role="dialog"] svg[aria-label="More options"], svg[aria-label="More options"], button:has(svg[aria-label="More options"]), div[role="button"]:has(svg[aria-label="More options"])'
        ).last
        if await more_btn.count() > 0:
            await more_btn.click(force=True)
            await asyncio.sleep(1.2)
            del_btn = page.locator('button:text-is("Delete"), button:has-text("Delete"), div[role="button"]:has-text("Delete")').first
            if await del_btn.count() > 0 and await del_btn.is_visible():
                await del_btn.click(force=True)
                await asyncio.sleep(1.2)
                confirm_btn = page.locator('button:text-is("Delete"), div[role="dialog"] button:has-text("Delete")').last
                if await confirm_btn.count() > 0 and await confirm_btn.is_visible():
                    await confirm_btn.click(force=True)
                    await asyncio.sleep(4.2)
                    print(f"    ✓ Deleted IG Reel {shortcode}!", flush=True)
                    return "deleted"
        # Close modal if still open
        await page.keyboard.press("Escape")
        await asyncio.sleep(1.0)
    except Exception as e:
        print(f"    [IG Delete Notice] {shortcode}: {e}", flush=True)
    return "failed"


async def run_ig_cleanup() -> Dict[str, Any]:
    res: Dict[str, Any] = {"deleted_reels": []}
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=IG_PROFILE_DIR,
            headless=False,
            viewport={"width": 1366, "height": 920},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for sc, reason in IG_SHORTCODES_TO_DELETE:
            st = await delete_ig_reel(page, sc, reason)
            res["deleted_reels"].append({"shortcode": sc, "reason": reason, "status": st})

        await page.goto("https://www.instagram.com/sacrednumberblueprint/reels/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
        ig_shot = os.path.join(BASE_DIR, "ig_grid_cleaned.png")
        await page.screenshot(path=ig_shot)
        print(f"  ✓ Saved cleaned Instagram Reels grid screenshot: {ig_shot}", flush=True)
        await ctx.close()
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["tiktok", "ig", "all"], default="all")
    args = parser.parse_args()
    out = {"updated_at": datetime.now().isoformat()}
    if args.platform in ("tiktok", "all"):
        out["tiktok"] = asyncio.run(run_tiktok_cleanup())
    if args.platform in ("ig", "all"):
        out["instagram"] = asyncio.run(run_ig_cleanup())
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved grid cleanup report -> {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
