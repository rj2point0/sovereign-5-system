#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · INSTAGRAM PROFILE SYNC, REEL UPGRADE & PINNER
sync_ig_profile_and_pin.py
-----------------------------------------------------------------------------
1. Updates Instagram Bio to:
   "Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇"
   and Name to "Love & Birthday Compatibility" (via /accounts/edit/ or Accounts Center).
2. Checks modification times of upgraded 68px giant-headline Reels
   (short_14, short_16, short_17, short_18) vs uploaded_ig_reels.json and
   cross-posts any that were upgraded after their original IG post.
3. Pins our top 3 relationship Reels to the top of @sacrednumberblueprint.
=============================================================================
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IG_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "ig_browser_profile")
UPLOADED_IG_PATH = os.path.join(BASE_DIR, "uploaded_ig_reels.json")
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
LOCAL_VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

TARGET_NAME = "Love & Birthday Compatibility"
TARGET_BIO = "Why do they pull away? 💔 Test your birthday & theirs across 5 systems 👇"


def check_upgraded_reels_needed():
    """Returns list of filenames among short_14, short_16, short_17, short_18 whose .mp4 is newer than uploaded_ig_reels.json."""
    if not os.path.exists(UPLOADED_IG_PATH):
        return []
    with open(UPLOADED_IG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    uploaded = data.get("uploaded_reels", {})
    candidates = [
        "tiktok_short_14_test_crush_birthday.mp4",
        "tiktok_short_16_last_text_crumbs.mp4",
        "tiktok_short_17_three_months_situationship.mp4",
        "tiktok_short_18_cares_less_power.mp4",
    ]
    to_repost = []
    for fname in candidates:
        p = os.path.join(GDRIVE_QUEUE_DIR, fname)
        if not os.path.exists(p):
            p = os.path.join(LOCAL_VIDEOS_DIR, fname)
        if not os.path.exists(p):
            continue
        mtime_utc = datetime.fromtimestamp(os.path.getmtime(p), tz=timezone.utc)
        rec = uploaded.get(fname, {})
        up_str = rec.get("updated_at", "")
        up_dt = None
        if up_str:
            try:
                up_dt = datetime.fromisoformat(up_str)
            except Exception:
                pass
        print(f"  [Check] {fname}: file_mtime={mtime_utc.isoformat()} | ig_uploaded={up_str}")
        if not up_dt or mtime_utc > up_dt:
            to_repost.append(fname)
    return to_repost


async def update_ig_bio_and_name(page):
    print("\n▶ [IG Profile] Navigating to https://www.instagram.com/accounts/edit/ ...", flush=True)
    await page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(5.0)
    await page.screenshot(path=os.path.join(BASE_DIR, "ig_edit_profile_before.png"))

    # 1. Update Bio textarea (#pepBio or textarea)
    bio_Selectors = [
        "textarea#pepBio",
        'textarea[placeholder*="Bio"]',
        "textarea",
    ]
    bio_updated = False
    for sel in bio_Selectors:
        loc = page.locator(sel).first
        if await loc.count() > 0 and await loc.is_visible():
            await loc.click(force=True)
            await asyncio.sleep(0.3)
            await loc.fill(TARGET_BIO)
            await asyncio.sleep(0.6)
            bio_updated = True
            print(f"  ✓ [IG Bio] Filled Bio ({len(TARGET_BIO)} chars): {TARGET_BIO}", flush=True)
            break

    # 2. Check if Name input is directly editable on /accounts/edit/
    name_selectors = [
        "input#pepName",
        'input[placeholder="Name"]',
        'input[aria-label="Name"]',
    ]
    for sel in name_selectors:
        loc = page.locator(sel).first
        if await loc.count() > 0 and await loc.is_visible():
            readonly = await loc.get_attribute("readonly")
            disabled = await loc.get_attribute("disabled")
            if not readonly and not disabled:
                await loc.click(force=True)
                await loc.fill(TARGET_NAME)
                print(f"  ✓ [IG Name] Filled Name directly: {TARGET_NAME}", flush=True)
            else:
                print("  ℹ [IG Name] Name field is managed via Meta Accounts Center link.", flush=True)
            break

    # Click Submit button on /accounts/edit/
    if bio_updated:
        submit_selectors = [
            'div[role="button"]:text-is("Submit")',
            'button:text-is("Submit")',
            'button[type="submit"]',
        ]
        for sel in submit_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click(force=True)
                print("  ✓ [IG Bio] Clicked Submit on Edit Profile!", flush=True)
                await asyncio.sleep(4.0)
                break

    # 3. Try updating Name via clicking "Meta Account" on /accounts/edit/
    try:
        await page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(3.5)
        meta_btn = page.locator('a[href*="accountscenter"], :text-is("Meta Account"), div[role="button"]:has-text("Meta Account")').first
        if await meta_btn.count() > 0:
            await meta_btn.click(force=True)
            await asyncio.sleep(4.5)
            target_page = page.context.pages[-1]
            await asyncio.sleep(2.0)
            await target_page.screenshot(path=os.path.join(BASE_DIR, "ig_accounts_center_step1.png"))
            ac_txt = await target_page.evaluate("() => document.body.innerText")
            print("  [IG Accounts Center Step 1]:", " | ".join([l.strip() for l in ac_txt.splitlines() if l.strip()][:12]), flush=True)
            prof_row = target_page.locator('a[href*="/profiles/"], [role="button"]:has-text("1 profile"), [role="link"]:has-text("1 profile"), :text-is("1 profile")').first
            if await prof_row.count() > 0:
                await prof_row.click(force=True)
                await asyncio.sleep(3.5)
                await target_page.screenshot(path=os.path.join(BASE_DIR, "ig_accounts_center_step2.png"))
                ig_sub_row = target_page.locator('[role="button"]:has-text("sacrednumberblueprint"), [role="link"]:has-text("sacrednumberblueprint"), :text-is("sacrednumberblueprint")').first
                if await ig_sub_row.count() > 0 and await ig_sub_row.is_visible():
                    await ig_sub_row.click(force=True)
                    await asyncio.sleep(3.5)
                    await target_page.screenshot(path=os.path.join(BASE_DIR, "ig_accounts_center_step2b.png"))
                name_row = target_page.locator('a[href*="/name"], [role="link"]:has-text("Name"), [role="button"]:has-text("Name"), :text-is("Name")').first
                if await name_row.count() > 0:
                    await name_row.click(force=True)
                    await asyncio.sleep(3.5)
                    await target_page.screenshot(path=os.path.join(BASE_DIR, "ig_accounts_center_step3.png"))
                    inp = target_page.locator('input[type="text"]').first
                    if await inp.count() > 0:
                        await inp.click(force=True)
                        await inp.fill(TARGET_NAME)
                        await asyncio.sleep(0.8)
                        done_btn = target_page.locator('[role="button"]:has-text("Done"), button:has-text("Done"), [role="button"]:has-text("Save"), button:has-text("Save")').first
                        if await done_btn.count() > 0:
                            await done_btn.click(force=True)
                            print(f"  ✓ [IG Accounts Center] Updated Name to '{TARGET_NAME}'!", flush=True)
                            await asyncio.sleep(4.0)
    except Exception as e:
        print(f"  ℹ [IG Accounts Center] Note: {e}", flush=True)

    await page.goto("https://www.instagram.com/sacrednumberblueprint/", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(4.5)
    await page.screenshot(path=os.path.join(BASE_DIR, "ig_profile_synced_verified.png"))
    header_txt = await page.evaluate("() => (document.querySelector('header') || document.body).innerText")
    print("  [IG Profile Header Snapshot]:", " | ".join([line.strip() for line in header_txt.splitlines() if line.strip()][:10]), flush=True)


async def pin_top_ig_reels(page):
    """Attempts to pin our top 3 relationship Reels on @sacrednumberblueprint."""
    print("\n▶ [IG Pin] Checking top relationship Reels on https://www.instagram.com/sacrednumberblueprint/ ...", flush=True)
    await page.goto("https://www.instagram.com/sacrednumberblueprint/", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(4.5)

    reel_hrefs = await page.evaluate(
        """() => {
            return Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]'))
                .map(a => a.getAttribute('href'))
                .filter(Boolean)
                .slice(0, 6);
        }"""
    )
    print(f"  Found top grid Reels: {reel_hrefs[:4]}", flush=True)

    pinned_count = 0
    for href in reel_hrefs[:3]:
        loc = page.locator(f'a[href="{href}"]').first
        if await loc.count() == 0:
            continue
        await loc.click(force=True)
        await asyncio.sleep(3.5)

        more_btn = page.locator('svg[aria-label="More options"], button:has(svg[aria-label="More options"])').first
        if await more_btn.count() > 0 and await more_btn.is_visible():
            await more_btn.click(force=True)
            await asyncio.sleep(1.5)
            menu_items = await page.evaluate("""() => Array.from(document.querySelectorAll('div[role="dialog"] button')).map(b => (b.innerText || '').trim()).filter(Boolean)""")
            print(f"  [IG More Options for {href}]: {menu_items}", flush=True)
            pin_btn = page.locator('button:has-text("Pin to your profile"), button:has-text("Pin to your main grid"), div[role="button"]:has-text("Pin")').first
            if await pin_btn.count() > 0 and await pin_btn.is_visible():
                txt = await pin_btn.inner_text()
                if "Unpin" not in txt:
                    await pin_btn.click(force=True)
                    pinned_count += 1
                    print(f"  ✓ [IG Pin] Pinned {href} to profile grid!", flush=True)
                    await asyncio.sleep(2.0)
                else:
                    print(f"  ✓ [IG Pin] {href} is already pinned.", flush=True)
            else:
                # Close menu
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.8)

        close_btn = page.locator('svg[aria-label="Close"], button:has(svg[aria-label="Close"])').first
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await close_btn.click(force=True)
        else:
            await page.keyboard.press("Escape")
        await asyncio.sleep(1.5)

    await page.goto("https://www.instagram.com/sacrednumberblueprint/", wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(4.0)
    await page.screenshot(path=os.path.join(BASE_DIR, "ig_profile_final_grid.png"))
    print("  ✓ Saved final Instagram profile screenshot: ig_profile_final_grid.png", flush=True)


async def main():
    to_repost = check_upgraded_reels_needed()
    print(f"Upgraded 68px Reels needing IG cross-post: {to_repost}", flush=True)

    if to_repost:
        from ig_reels_auto_uploader import InstagramReelsUploader
        uploader = InstagramReelsUploader(profile_dir=IG_PROFILE_DIR)
        await uploader.run(videos=to_repost, force=True, headless=False)

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=IG_PROFILE_DIR,
            headless=False,
            viewport={"width": 1366, "height": 920},
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await update_ig_bio_and_name(page)
            await pin_top_ig_reels(page)
        finally:
            await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
