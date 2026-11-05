#!/usr/bin/env python3
r"""
=============================================================================
SACRED NUMBER BLUEPRINT · UNIFIED 19x23 (96% MATCH) AVATAR UPLOADER
sync_19x23_avatar_all_platforms.py
-----------------------------------------------------------------------------
Uploads `sacred_avatar_512.png` (19×23 · 96% MATCH) as the profile picture on:
1. TikTok (`https://www.tiktok.com/@sacrednumberblueprint` -> `Edit profile`)
2. Instagram (`https://www.instagram.com/sacrednumberblueprint/` -> `Change photo`
   or Meta Accounts Center `https://accountscenter.instagram.com/profiles/`)
=============================================================================
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright

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


async def upload_tiktok_avatar():
    print("\n▶ [TikTok Avatar] Uploading sacred_avatar_512.png to @sacrednumberblueprint...", flush=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=TT_PROFILE_DIR,
            headless=False,
            viewport={"width": 1366, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.0)

        edit_btn = page.locator('[data-e2e="edit-profile-entrance"], button:has-text("Edit profile")').first
        if await edit_btn.count() == 0:
            print("  ⚠ [TikTok Avatar] 'Edit profile' button not found on profile page.", flush=True)
            await ctx.close()
            return False

        await edit_btn.click(force=True)
        await asyncio.sleep(2.5)

        uploaded = False
        file_inputs = page.locator('input[type="file"]')
        if await file_inputs.count() > 0:
            try:
                await file_inputs.first.set_input_files(AVATAR_PATH)
                await asyncio.sleep(2.5)
                uploaded = True
                print("  ✓ [TikTok Avatar] Attached sacred_avatar_512.png via file input.", flush=True)
            except Exception as e:
                print(f"  [TikTok Avatar] Direct file input notice: {e}", flush=True)

        if not uploaded:
            try:
                avatar_edit = page.locator('[data-e2e="edit-profile-avatar"], div[class*="Avatar"] svg, div[aria-label*="Profile photo"]').first
                if await avatar_edit.count() > 0:
                    async with page.expect_file_chooser(timeout=8000) as fc_info:
                        await avatar_edit.click(force=True)
                    fc = await fc_info.value
                    await fc.set_files(AVATAR_PATH)
                    await asyncio.sleep(2.5)
                    uploaded = True
                    print("  ✓ [TikTok Avatar] Attached sacred_avatar_512.png via file chooser.", flush=True)
            except Exception as e:
                print(f"  [TikTok Avatar] File chooser notice: {e}", flush=True)

        # Click Apply in cropper modal if shown
        apply_btn = page.locator('button:has-text("Apply"), [data-e2e="edit-profile-avatar-apply"]').first
        if await apply_btn.count() > 0 and await apply_btn.is_visible():
            await apply_btn.click(force=True)
            await asyncio.sleep(2.0)
            print("  ✓ [TikTok Avatar] Clicked 'Apply' on avatar cropper.", flush=True)

        # Click Save in Edit Profile modal
        save_btn = page.locator('[data-e2e="edit-profile-save"], button:has-text("Save")').last
        if await save_btn.count() > 0 and await save_btn.is_visible():
            await save_btn.click(force=True)
            await asyncio.sleep(5.0)
            print("  ✓ [TikTok Avatar] Clicked 'Save' on Edit Profile modal!", flush=True)

        await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
        shot_path = os.path.join(BASE_DIR, "tiktok_avatar_19x23_verified.png")
        await page.screenshot(path=shot_path)
        print(f"  ✓ [TikTok Avatar] Saved verification screenshot -> {shot_path}", flush=True)
        await ctx.close()
        return uploaded


async def upload_instagram_avatar():
    print("\n▶ [Instagram Avatar] Uploading sacred_avatar_512.png to @sacrednumberblueprint...", flush=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=IG_PROFILE_DIR,
            headless=False,
            viewport={"width": 1366, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Attempt 1: Direct profile page avatar click or /accounts/edit/
        await page.goto("https://www.instagram.com/accounts/edit/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)

        uploaded = False
        # Check if there is an input[type="file"] directly on /accounts/edit/
        f_in = page.locator('input[type="file"]')
        if await f_in.count() > 0:
            try:
                await f_in.first.set_input_files(AVATAR_PATH)
                await asyncio.sleep(4.5)
                uploaded = True
                print("  ✓ [Instagram Avatar] Uploaded sacred_avatar_512.png directly on /accounts/edit/!", flush=True)
            except Exception as e:
                print(f"  [Instagram Avatar] /accounts/edit/ input notice: {e}", flush=True)

        if not uploaded:
            change_btn = page.locator('button:has-text("Change photo"), div[role="button"]:has-text("Change photo"), img[alt*="Change profile photo"]').first
            if await change_btn.count() > 0 and await change_btn.is_visible():
                try:
                    await change_btn.click(force=True)
                    await asyncio.sleep(1.5)
                    # Check if a modal with 'Upload Photo' appeared or if file input appeared
                    up_btn = page.locator('button:has-text("Upload Photo"), button:has-text("Upload photo")').first
                    if await up_btn.count() > 0 and await up_btn.is_visible():
                        async with page.expect_file_chooser(timeout=8000) as fc_info:
                            await up_btn.click(force=True)
                        fc = await fc_info.value
                        await fc.set_files(AVATAR_PATH)
                        await asyncio.sleep(5.0)
                        uploaded = True
                        print("  ✓ [Instagram Avatar] Uploaded sacred_avatar_512.png via 'Upload Photo' dialog!", flush=True)
                    elif await page.locator('input[type="file"]').count() > 0:
                        await page.locator('input[type="file"]').first.set_input_files(AVATAR_PATH)
                        await asyncio.sleep(5.0)
                        uploaded = True
                        print("  ✓ [Instagram Avatar] Uploaded sacred_avatar_512.png via modal file input!", flush=True)
                except Exception as e:
                    print(f"  [Instagram Avatar] Change photo button notice: {e}", flush=True)

        # Attempt 2: Profile page header avatar click
        if not uploaded:
            await page.goto("https://www.instagram.com/sacrednumberblueprint/", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4.5)
            f_in2 = page.locator('input[type="file"]')
            if await f_in2.count() > 0:
                try:
                    await f_in2.first.set_input_files(AVATAR_PATH)
                    await asyncio.sleep(5.0)
                    uploaded = True
                    print("  ✓ [Instagram Avatar] Uploaded sacred_avatar_512.png on profile page file input!", flush=True)
                except Exception:
                    pass
            if not uploaded:
                try:
                    hdr_av = page.locator('header img[alt*="profile picture"], header button[title*="Change Profile Photo"], header canvas').first
                    if await hdr_av.count() > 0:
                        await hdr_av.click(force=True)
                        await asyncio.sleep(1.5)
                        up_btn = page.locator('button:has-text("Upload Photo"), button:has-text("Upload photo")').first
                        if await up_btn.count() > 0 and await up_btn.is_visible():
                            async with page.expect_file_chooser(timeout=8000) as fc_info:
                                await up_btn.click(force=True)
                            fc = await fc_info.value
                            await fc.set_files(AVATAR_PATH)
                            await asyncio.sleep(5.0)
                            uploaded = True
                            print("  ✓ [Instagram Avatar] Uploaded sacred_avatar_512.png from profile header!", flush=True)
                except Exception as e:
                    print(f"  [Instagram Avatar] Profile header notice: {e}", flush=True)

        # Attempt 3: Meta Accounts Center (https://accountscenter.instagram.com/profiles/)
        if not uploaded:
            print("  [Instagram Avatar] Opening Meta Accounts Center (https://accountscenter.instagram.com/profiles/)...", flush=True)
            await page.goto("https://accountscenter.instagram.com/profiles/", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4.5)
            prof_row = page.locator('a[href*="/profiles/"], div[role="button"]:has-text("sacrednumberblueprint"), div[role="button"]:has-text("Love & Birthday")').first
            if await prof_row.count() > 0:
                await prof_row.click(force=True)
                await asyncio.sleep(3.0)
                pic_row = page.locator('div[role="button"]:has-text("Profile picture"), a:has-text("Profile picture")').first
                if await pic_row.count() > 0:
                    await pic_row.click(force=True)
                    await asyncio.sleep(2.5)
                    f_ac = page.locator('input[type="file"]')
                    if await f_ac.count() > 0:
                        await f_ac.first.set_input_files(AVATAR_PATH)
                        await asyncio.sleep(3.5)
                    else:
                        up_new = page.locator('div[role="button"]:has-text("Upload new photo"), span:has-text("Upload new photo")').first
                        if await up_new.count() > 0:
                            async with page.expect_file_chooser(timeout=8000) as fc_info:
                                await up_new.click(force=True)
                            fc = await fc_info.value
                            await fc.set_files(AVATAR_PATH)
                            await asyncio.sleep(3.5)
                    save_ac = page.locator('div[role="button"]:has-text("Save"), button:has-text("Save")').last
                    if await save_ac.count() > 0 and await save_ac.is_visible():
                        await save_ac.click(force=True)
                        await asyncio.sleep(6.0)
                        uploaded = True
                        print("  ✓ [Instagram Avatar] Saved sacred_avatar_512.png via Meta Accounts Center!", flush=True)

        await page.goto("https://www.instagram.com/sacrednumberblueprint/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
        shot_path = os.path.join(BASE_DIR, "ig_avatar_19x23_verified.png")
        await page.screenshot(path=shot_path)
        print(f"  ✓ [Instagram Avatar] Saved verification screenshot -> {shot_path}", flush=True)
        await ctx.close()
        return uploaded


async def main():
    await upload_tiktok_avatar()
    await upload_instagram_avatar()


if __name__ == "__main__":
    asyncio.run(main())
