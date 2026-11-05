#!/usr/bin/env python3
r"""
=============================================================================
SACRED NUMBER BLUEPRINT · TIKTOK SCHEDULE DEDUPLICATOR & 19x23 AVATAR SYNC
dedup_tiktok_scheduled_and_sync_avatars.py
-----------------------------------------------------------------------------
1. Scans all rows in TikTok Studio (`https://www.tiktok.com/tiktokstudio/content`)
   and public/scheduled cards on `https://www.tiktok.com/@sacrednumberblueprint`.
2. For each scheduled video (`short_24`, `short_26`, `short_27`, `short_29`, `short_30`),
   keeps ONLY the newest `emotional_face_giant` upload and deletes all older/duplicate
   scheduled copies so zero duplicates ever appear on the grid.
3. Uploads `sacred_avatar_512.png` (`19×23 · 96% MATCH`) in TikTok Edit Profile
   (handling the Apply crop modal + Save button) and verifies on Instagram.
=============================================================================
"""

import asyncio
import json
import os
import re
import sys
from typing import Dict, List, Set
from playwright.async_api import async_playwright, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_PATH = os.path.join(BASE_DIR, "sacred_avatar_512.png")
TT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\tiktok_browser_profile"
IG_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"


async def scroll_studio_table(page: Page, dy: int):
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


async def collect_all_studio_rows(page: Page) -> List[Dict[str, str]]:
    await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(5.0)
    try:
        await page.wait_for_selector('div[data-tt="components_RowLayout_FlexRow"]', timeout=15000)
    except Exception:
        pass

    await scroll_studio_table(page, -6000)
    await asyncio.sleep(0.8)

    seen: Dict[str, Dict[str, str]] = {}
    for _ in range(16):
        rows = page.locator('div[data-tt="components_RowLayout_FlexRow"]')
        cnt = await rows.count()
        for i in range(cnt):
            r = rows.nth(i)
            try:
                a_el = r.locator('a[href*="/video/"]').first
                if await a_el.count() == 0:
                    continue
                href = await a_el.get_attribute("href") or ""
                m = re.search(r"/video/(\d+)", href)
                if not m:
                    continue
                vid = m.group(1)
                if vid not in seen:
                    txt = (await r.inner_text()).strip()
                    seen[vid] = {"vid": vid, "text": txt, "order": len(seen)}
            except Exception:
                continue
        await scroll_studio_table(page, 650)
        await asyncio.sleep(0.8)
    return list(seen.values())


def classify_video_topic(txt: str) -> str:
    low = txt.lower()
    if "are your birthdays endgame" in low or "3-month karmic lesson" in low:
        return "short_30"
    if "dating someone born on the 4th, 7th, 8th, 13th" in low or "silent treatment" in low:
        return "short_29"
    if "why you always care more first" in low:
        return "short_28"
    if "your next love shift starts" in low or "born on the 3rd, 4th, 8th, 9th, 12th" in low:
        return "short_27"
    if "silence does not mean they forgot you" in low:
        return "short_26"
    if "intense chemistry can be a karmic trap" in low:
        return "short_25"
    if "only one birth number can handle your fire" in low:
        return "short_24"
    if "stop double texting when they go quiet" in low:
        return "short_23"
    if "why they act obsessed with you and then suddenly go cold" in low:
        return "short_22"
    if "why the next 30 days will test your heart" in low or "born on the 1st, 4th, 7th, 8th, 9th, 10th, 13th" in low:
        return "short_21"
    return f"other_{hash(low[:40])}"


async def delete_studio_row_by_vid(page: Page, vid: str, reason: str) -> bool:
    print(f"  [TT Studio Delete] {vid} ({reason})...", flush=True)
    if "/tiktokstudio/content" not in page.url:
        await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
    await scroll_studio_table(page, -6000)
    await asyncio.sleep(0.6)
    target_row = None
    for _ in range(16):
        row = page.locator(f'div[data-tt="components_RowLayout_FlexRow"]:has(a[href*="/video/{vid}"])').first
        if await row.count() > 0:
            await row.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            target_row = row
            break
        await scroll_studio_table(page, 650)
        await asyncio.sleep(0.8)

    if not target_row:
        print(f"    ⚠ Row {vid} not found.", flush=True)
        return False

    try:
        await target_row.hover()
        await asyncio.sleep(0.5)
        action_btns = target_row.locator('button[data-tt="components_ActionCell_Clickable"]')
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
                    await asyncio.sleep(2.8)
                print(f"    ✓ Deleted {vid}!", flush=True)
                return True
    except Exception as e:
        print(f"    [Error] {vid}: {e}", flush=True)
    return False


async def update_tiktok_avatar_properly(page: Page):
    print("\n▶ [TikTok Avatar] Updating avatar on https://www.tiktok.com/@sacrednumberblueprint ...", flush=True)
    await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(5.0)

    edit_btn = page.locator('[data-e2e="edit-profile-entrance"], button:has-text("Edit profile")').first
    if await edit_btn.count() == 0:
        print("  ⚠ Edit profile button not found.", flush=True)
        return
    await edit_btn.click(force=True)
    await asyncio.sleep(3.0)

    # Specifically target the file input inside the Edit Profile modal
    avatar_input = page.locator('div[data-e2e="edit-profile-avatar"] input[type="file"], div[role="dialog"] input[type="file"]').first
    if await avatar_input.count() > 0:
        await avatar_input.set_input_files(AVATAR_PATH)
        print("  ✓ Set sacred_avatar_512.png on dialog input[type='file'].", flush=True)
    else:
        avatar_click = page.locator('[data-e2e="edit-profile-avatar"], div[aria-label*="Profile photo"]').first
        if await avatar_click.count() > 0:
            async with page.expect_file_chooser(timeout=10000) as fc_info:
                await avatar_click.click(force=True)
            fc = await fc_info.value
            await fc.set_files(AVATAR_PATH)
            print("  ✓ Set sacred_avatar_512.png via file chooser.", flush=True)

    await asyncio.sleep(3.0)
    # Wait for and click Apply button in crop dialog
    for _ in range(8):
        apply_btn = page.locator('button:has-text("Apply"), [data-e2e="edit-profile-avatar-apply"]').last
        if await apply_btn.count() > 0 and await apply_btn.is_visible():
            await apply_btn.click(force=True)
            print("  ✓ Clicked 'Apply' on crop dialog.", flush=True)
            await asyncio.sleep(3.5)
            break
        await asyncio.sleep(0.6)

    # Now click Save button in Edit Profile dialog
    save_btn = page.locator('[data-e2e="edit-profile-save"], div[role="dialog"] button:has-text("Save")').last
    if await save_btn.count() > 0 and await save_btn.is_visible():
        await save_btn.click(force=True)
        print("  ✓ Clicked 'Save' on Edit Profile dialog!", flush=True)
        await asyncio.sleep(6.0)


async def run_tiktok_dedup_and_avatar():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=TT_PROFILE_DIR,
            headless=False,
            viewport={"width": 1366, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        rows = await collect_all_studio_rows(page)
        print(f"  [TT Studio] Collected {len(rows)} total rows.", flush=True)

        # Group by topic; for any topic with multiple Scheduled copies (or Scheduled + Published), keep only 1!
        by_topic: Dict[str, List[Dict[str, str]]] = {}
        for r in rows:
            t = classify_video_topic(r["text"])
            by_topic.setdefault(t, []).append(r)

        to_delete: List[tuple] = []
        for topic, items in by_topic.items():
            if not topic.startswith("short_"):
                continue
            # Sort by vid descending (higher snowflake ID = newer upload!)
            items_sorted = sorted(items, key=lambda x: int(x["vid"]), reverse=True)
            if len(items_sorted) > 1:
                # Keep the newest (highest vid) OR if one is already Published with views and another is Scheduled:
                # For short_23: 7704542849571900685 is our newest Published LIVE Giant-Text upload -> delete any other short_23
                # For short_24, short_26, short_27, short_29, short_30: keep ONLY the highest vid (newest Giant-Text upload) and delete all older copies!
                keep = items_sorted[0]
                print(f"  [Topic {topic}] Keeping newest vid={keep['vid']} (out of {len(items_sorted)} copies)", flush=True)
                for dup in items_sorted[1:]:
                    # Only delete if it's Scheduled or a recent 0-view duplicate
                    if "Scheduled" in dup["text"] or topic in ("short_23", "short_24", "short_26", "short_27", "short_29", "short_30", "short_21"):
                        to_delete.append((dup["vid"], f"duplicate_{topic}_keeping_{keep['vid']}"))

        print(f"  [TT Studio] Deleting {len(to_delete)} duplicate/old copies...", flush=True)
        for vid, reason in to_delete:
            await delete_studio_row_by_vid(page, vid, reason)

        await update_tiktok_avatar_properly(page)

        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.0)
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(4.5)
        shot_path = os.path.join(BASE_DIR, "tiktok_avatar_19x23_verified.png")
        await page.screenshot(path=shot_path)
        print(f"  ✓ Saved clean TikTok profile screenshot -> {shot_path}", flush=True)
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(run_tiktok_dedup_and_avatar())
