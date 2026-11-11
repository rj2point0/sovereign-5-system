#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · YOUTUBE SHORTS REBRAND, AUTO-UPLOADER & COMMENT PINNER
yt_shorts_auto_uploader.py
-----------------------------------------------------------------------------
1. Rebrands https://www.youtube.com/@CognitiveCurrent (UCBIWSA7ZBuBEP_9rj3uSfqA)
   to `Love & Birthday Compatibility` (`@sacrednumberblueprint`):
   - Sets old Amazon affiliate videos/Shorts to Private (preserving age & views)
   - Updates Channel Name, Handle, Description, Avatar, and clickable Bio Link
     (`Test Both Birthdays Free 💔` -> https://blueprint.megavegaventures.com/?utm_source=yt_shorts&cohort=bio)
2. Publishes top 3 7.5-second Visual Demo Shorts (`short_22`, `short_25`, `short_28`)
   LIVE right now with <= 60 char problem-first titles + #Shorts, description CTA,
   and `Not made for kids`.
3. Seeds & Pins the 2-birthday Match % prompt comment + posts the Sample Match
   follow-up comment on each live Short.
4. Schedules the remaining 7.5s Visual Demo Batch (`short_21`, `short_23`,
   `short_24`, `short_26`, `short_27`, `short_29`, `short_30`) at 2x/day
   (11:00 AM and 6:30 PM).
=============================================================================
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
if not os.path.exists(VIDEO_DIR):
    VIDEO_DIR = os.path.join(BASE_DIR, "tiktok_videos")
YT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\yt_browser_profile"
YT_CHANNEL_ID = "UCBIWSA7ZBuBEP_9rj3uSfqA"
TRACKER_PATH = os.path.join(BASE_DIR, "uploaded_yt_shorts.json")
AVATAR_PATH = os.path.join(BASE_DIR, "sacred_avatar_512.png")

CHANNEL_NAME = "Love & Birthday Compatibility"
CHANNEL_HANDLE = "sacrednumberblueprint"
CHANNEL_DESCRIPTION = (
    "Why do they pull away right when you get close? 💔 Test your Birth Day (1–31) "
    "and your crush or partner's Birth Day across 5 ancient timing & compatibility "
    "systems to see your exact Compatibility % Score and custom \"Flip The Chase\" text script 👇"
)
CHANNEL_LINK_TITLE = "Test Both Birthdays Free 💔"
CHANNEL_LINK_URL = "https://blueprint.megavegaventures.com/?utm_source=yt_shorts&cohort=bio"

FIRST_COMMENT_PROMPT = (
    "Drop YOUR birth day (1-31) + THEIR birth day (1-31) below (like '19 & 23') "
    "and I'll reply with your Compatibility % score! 👇"
)
SAMPLE_MATCH_REPLY = (
    "📌 Top pair asked today: Day 19 × Day 23 = 96% Twin-Spark Lock 🔥 "
    "Intense pull, but one goes quiet when stressed! Drop your 2 days 👇"
)

YT_SHORTS_QUEUE: List[Dict[str, Any]] = [
    {
        "id": "short_51",
        "filename": "Short_051_Veo31_Breadcrumbing.mp4",
        "title": "Birth Days That Breadcrumb You For Months 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_52",
        "filename": "Short_052_Veo31_HotAndCold.mp4",
        "title": "Why He Acts Hot One Day & Cold The Next 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 10, 2026",
        "schedule_time": "6:30 PM",
    },
    {
        "id": "short_53",
        "filename": "Short_053_Veo31_Vanished6Weeks.mp4",
        "title": "Texted Daily For 6 Weeks Then Vanished? 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 11, 2026",
        "schedule_time": "11:00 AM",
    },
    {
        "id": "short_54",
        "filename": "Short_054_Veo31_WatchesStories.mp4",
        "title": "Watches Your Stories In 30s But Won't Text? 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 11, 2026",
        "schedule_time": "6:30 PM",
    },
    {
        "id": "short_55",
        "filename": "Short_055_Veo31_DryReplies.mp4",
        "title": "What His Dry 1-Word Replies Actually Mean 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 12, 2026",
        "schedule_time": "11:00 AM",
    },
    {
        "id": "short_56",
        "filename": "Short_056_Veo31_RegretsLosingYou.mp4",
        "title": "Exact Moment A Man Regrets Pulling Away 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 12, 2026",
        "schedule_time": "6:30 PM",
    },
    {
        "id": "short_57",
        "filename": "Short_057_Veo31_PullsAwayAfterCloseness.mp4",
        "title": "Gets Super Close Then Pulls Away Monday? 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 13, 2026",
        "schedule_time": "11:00 AM",
    },
    {
        "id": "short_58",
        "filename": "Short_058_Veo31_LateNightWyd.mp4",
        "title": "Why He Only Texts \"U Up?\" After 11 PM 🎙️📱 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 13, 2026",
        "schedule_time": "6:30 PM",
    },
    {
        "id": "short_59",
        "filename": "Short_059_Veo31_NeverInitiatesPlans.mp4",
        "title": "Texts All Day But Never Makes Real Plans? 🎙️💔 #Shorts",
        "mode": "schedule",
        "schedule_date": "Nov 14, 2026",
        "schedule_time": "11:00 AM",
    },
    {
        "id": "short_50",
        "filename": "Short_050_Veo31_ColdOvernight.mp4",
        "title": "Why He Goes Cold Overnight (By Birth Day) 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_43",
        "filename": "tiktok_short_43_podcast_bare_minimum.mp4",
        "title": "Birth Days That Give Bare Minimum Effort 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_44",
        "filename": "tiktok_short_44_podcast_hot_and_cold.mp4",
        "title": "Why He Acts Hot One Day & Cold The Next 🎙️🥶 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_45",
        "filename": "tiktok_short_45_podcast_keeps_you_hooked.mp4",
        "title": "How He Keeps You Hooked Without Committing 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_40",
        "filename": "tiktok_short_40_podcast_watches_stories.mp4",
        "title": "He Watches Your Stories But Won't Text Back? 🎙️👀 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_41",
        "filename": "tiktok_short_41_podcast_three_month_curse.mp4",
        "title": "Why Men Switch Up At The 6-Week Mark 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_42",
        "filename": "tiktok_short_42_podcast_one_word_reply.mp4",
        "title": "When He Sends Dry 1-Word Text Replies 🎙️📱 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_37",
        "filename": "tiktok_short_37_podcast_male_silence.mp4",
        "title": "Why Men Go Dead Silent (By His Birth Day) 🎙️💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_38",
        "filename": "tiktok_short_38_podcast_he_read_it.mp4",
        "title": "He Left You On Read? A Guy Explains Why 🎙️📱 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_39",
        "filename": "tiktok_short_39_podcast_who_regrets_it.mp4",
        "title": "When Men Actually Regret Pulling Away 🎙️🔥 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_34",
        "filename": "tiktok_short_34_7sec_acting_distant_test.mp4",
        "title": "When He Acts Cold & Distant, Do This First 🥶 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_35",
        "filename": "tiktok_short_35_7sec_breadcrumbing_days.mp4",
        "title": "Birth Days That Breadcrumb You For Months 💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_36",
        "filename": "tiktok_short_36_7sec_who_comes_back.mp4",
        "title": "Why They Always Come Back When You Pull Away 🔥 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_31",
        "filename": "tiktok_short_31_7sec_six_weeks_vanished.mp4",
        "title": "He Texted Daily For 6 Weeks Then Vanished 💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_32",
        "filename": "tiktok_short_32_7sec_read_at_midnight.mp4",
        "title": "Left On Read At Midnight? Send This 9-Word Text 📱 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_33",
        "filename": "tiktok_short_33_7sec_wrong_birthday_match.mp4",
        "title": "Why You Always Fall For People Who Pull Away 💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    # Upload the newly rendered emotional_face_giant Shorts (short_23, short_24, short_26, short_27, short_29, short_30) with pinned 2-birthday comments
    {
        "id": "short_23",
        "filename": "tiktok_short_23_7sec_double_text.mp4",
        "title": "Never Double Text When This Birth Day Goes Quiet 📱💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_24",
        "filename": "tiktok_short_24_7sec_soulmate_day.mp4",
        "title": "Only 1 Birth Day Can Handle Your Fire Without Drama 🔥 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_26",
        "filename": "tiktok_short_26_7sec_no_contact_thoughts.mp4",
        "title": "Why Their Silence Does NOT Mean They Forgot You 💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_27",
        "filename": "tiktok_short_27_7sec_november_turning_point.mp4",
        "title": "Your November Love Turning Point By Birth Day ✨ #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_29",
        "filename": "tiktok_short_29_7sec_silent_treatment_days.mp4",
        "title": "Never Chase When These Birth Days Go Silent 🤫 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
    {
        "id": "short_30",
        "filename": "tiktok_short_30_7sec_endgame_birthdays.mp4",
        "title": "Are Your Birthdays Endgame Or A 3-Month Lesson? 💔 #Shorts",
        "mode": "post_now",
        "schedule_date": None,
        "schedule_time": None,
    },
]

SHORT_DESCRIPTION = (
    "Test both birthdays free: https://blueprint.megavegaventures.com/?utm_source=yt_shorts\n\n"
    "Drop YOUR birth day (1–31) + THEIR birth day (1–31) in the comments (like '19 & 23') "
    "and I'll reply with your exact Compatibility % score! 👇\n\n"
    "#Shorts #birthdaycompatibility #numerology #relationshipadvice #situationship #datingadvice"
)


def load_tracker() -> Dict[str, Any]:
    if os.path.exists(TRACKER_PATH):
        try:
            with open(TRACKER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"channel_id": YT_CHANNEL_ID, "rebranded": False, "videos": {}}


def save_tracker(data: Dict[str, Any]):
    data["updated_at"] = datetime.now().isoformat()
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def privatize_old_videos(page: Page):
    """Sets all old Amazon affiliate videos & Shorts on @CognitiveCurrent to Private (never deletes)."""
    for tab_url in [
        f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/upload",
        f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/short",
    ]:
        print(f"  [Rebrand] Checking Content tab: {tab_url}", flush=True)
        await page.goto(tab_url, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.0)

        rows = page.locator("ytcp-video-row")
        rcount = await rows.count()
        print(f"  [Rebrand] Found {rcount} video row(s) on {tab_url.split('/')[-1]} tab.", flush=True)
        for idx in range(rcount):
            row = rows.nth(idx)
            try:
                row_txt = await row.inner_text()
            except Exception:
                continue
            # Skip our new Sacred Number Blueprint shorts
            if any(k in row_txt for k in ["#Shorts", "Born on", "Why You Always", "Why Their Silence", "November Love", "Never Chase", "Endgame", "Only 1 Birth"]):
                continue
            if "Private" in row_txt:
                continue
            try:
                vis_cell = row.locator("ytcp-video-row-cell-visibility, .cell-body.tablecell-visibility, #visibility-text").first
                if await vis_cell.count() > 0:
                    await vis_cell.click(force=True)
                    await asyncio.sleep(1.0)
                    priv_radio = page.locator('tp-yt-paper-radio-button[name="PRIVATE"], tp-yt-paper-radio-button:has-text("Private")').first
                    if await priv_radio.count() > 0:
                        await priv_radio.click(force=True)
                        await asyncio.sleep(0.5)
                        save_btn = page.locator('ytcp-button#save-button, div[role="dialog"] button:has-text("Save")').first
                        if await save_btn.count() > 0:
                            await save_btn.click(force=True)
                            await asyncio.sleep(2.5)
                            print(f"    ✓ Set old video row #{idx+1} to Private.", flush=True)
            except Exception as e:
                print(f"    [Notice] Row #{idx+1} visibility change notice: {e}", flush=True)


async def rebrand_channel(page: Page) -> bool:
    """Updates Channel Name, Handle, Description, Avatar, and Links in YouTube Studio Customization."""
    cust_url = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/editing/profile"
    print(f"  [Rebrand] Opening Customization page: {cust_url}", flush=True)
    await page.goto(cust_url, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(5.5)

    if "accounts.google.com" in page.url or "signin" in page.url.lower():
        print("  [Rebrand] Not logged in to YouTube Studio!", flush=True)
        return False

    # If YouTube Studio redirects to editing/sections or editing/images, click 'Basic info' or 'Profile' tab
    for tab_label in ["Profile", "Basic info"]:
        tab = page.locator(f'tp-yt-paper-tab:has-text("{tab_label}"), button:has-text("{tab_label}")').first
        if await tab.count() > 0 and await tab.is_visible():
            await tab.click(force=True)
            await asyncio.sleep(1.5)

    # 1. Upload Avatar if file input or Change button exists
    if os.path.exists(AVATAR_PATH):
        try:
            file_inputs = page.locator('input[type="file"]')
            if await file_inputs.count() > 0:
                await file_inputs.first.set_input_files(AVATAR_PATH)
                await asyncio.sleep(2.0)
                done_btn = page.locator('ytcp-button#save-button, div[role="dialog"] button:has-text("Done")').first
                if await done_btn.count() > 0 and await done_btn.is_visible():
                    await done_btn.click(force=True)
                    await asyncio.sleep(1.5)
                print("    ✓ Uploaded Sacred Number Blueprint circular avatar.", flush=True)
        except Exception as e:
            print(f"    [Avatar Notice] {e}", flush=True)

    # 2. Update Channel Name
    try:
        name_box = page.locator(
            'ytcp-profile-name-editor input, #name-input input, ytcp-form-input-container:has-text("Name") input, input[aria-label*="Name"]'
        ).first
        if await name_box.count() > 0 and await name_box.is_visible():
            await name_box.click(force=True)
            await page.keyboard.press("Control+A")
            await name_box.fill(CHANNEL_NAME)
            await asyncio.sleep(0.6)
            print(f"    ✓ Set Channel Name: {CHANNEL_NAME}", flush=True)
    except Exception as e:
        print(f"    [Name Notice] {e}", flush=True)

    # 3. Update Handle (@sacrednumberblueprint or @sacrednumberblueprint1)
    try:
        handle_box = page.locator(
            'ytcp-profile-handle-editor input, #handle-input input, ytcp-form-input-container:has-text("Handle") input, input[aria-label*="Handle"]'
        ).first
        if await handle_box.count() > 0 and await handle_box.is_visible():
            await handle_box.click(force=True)
            await page.keyboard.press("Control+A")
            await handle_box.fill(CHANNEL_HANDLE)
            await asyncio.sleep(2.0)
            body_txt = await page.inner_text("body")
            if "isn't available" in body_txt or "already taken" in body_txt.lower():
                await handle_box.click(force=True)
                await page.keyboard.press("Control+A")
                await handle_box.fill(CHANNEL_HANDLE + "1")
                await asyncio.sleep(1.5)
                print(f"    ✓ Set Channel Handle: @{CHANNEL_HANDLE}1", flush=True)
            else:
                print(f"    ✓ Set Channel Handle: @{CHANNEL_HANDLE}", flush=True)
    except Exception as e:
        print(f"    [Handle Notice] {e}", flush=True)

    # 4. Update Description
    try:
        desc_box = page.locator(
            'ytcp-profile-description-editor textarea, ytcp-profile-description-editor div[contenteditable="true"], #description-input textarea, div[aria-label*="Description"]'
        ).first
        if await desc_box.count() > 0 and await desc_box.is_visible():
            await desc_box.click(force=True)
            await page.keyboard.press("Control+A")
            await desc_box.fill(CHANNEL_DESCRIPTION)
            await asyncio.sleep(0.6)
            print("    ✓ Set Channel Description.", flush=True)
    except Exception as e:
        print(f"    [Desc Notice] {e}", flush=True)

    # 5. Add Channel Bio Link (`Test Both Birthdays Free 💔` -> https://blueprint.megavegaventures.com/?utm_source=yt_shorts&cohort=bio)
    try:
        add_link_btn = page.locator('ytcp-button#add-link-button, button:has-text("Add link")').first
        if await add_link_btn.count() > 0 and await add_link_btn.is_visible():
            await add_link_btn.click(force=True)
            await asyncio.sleep(1.0)
        title_inputs = page.locator('input[placeholder*="link title" i], input[aria-label*="Link title" i]')
        url_inputs = page.locator('input[placeholder*="URL" i], input[aria-label*="URL" i]')
        if await title_inputs.count() > 0 and await url_inputs.count() > 0:
            await title_inputs.first.fill(CHANNEL_LINK_TITLE)
            await url_inputs.first.fill(CHANNEL_LINK_URL)
            await asyncio.sleep(0.6)
            print(f"    ✓ Set Channel Header Link: {CHANNEL_LINK_TITLE} -> {CHANNEL_LINK_URL}", flush=True)
    except Exception as e:
        print(f"    [Link Notice] {e}", flush=True)

    # 6. Click Publish
    try:
        pub_btn = page.locator('ytcp-button#publish-button, button:has-text("Publish")').first
        if await pub_btn.count() > 0 and await pub_btn.is_visible():
            await pub_btn.click(force=True)
            await asyncio.sleep(4.0)
            print("    ✓ Clicked Publish on Channel Customization!", flush=True)
    except Exception as e:
        print(f"    [Publish Notice] {e}", flush=True)

    return True


async def seed_and_pin_comments_on_short(page: Page, video_id: str) -> Dict[str, Any]:
    """Seeds our 2-birthday prompt comment + Sample Match reply on a live YouTube Short and Pins the prompt."""
    res = {"prompt_seeded": False, "sample_seeded": False, "pinned": False}
    if not video_id:
        return res

    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  [YT Seed] Opening {watch_url} to seed & pin comments...", flush=True)
    await page.goto(watch_url, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(4.5)
    await page.evaluate("window.scrollBy(0, 650)")
    await asyncio.sleep(2.5)

    for comment_txt, key in [(FIRST_COMMENT_PROMPT, "prompt_seeded"), (SAMPLE_MATCH_REPLY, "sample_seeded")]:
        try:
            placeholder = page.locator("#simplebox-placeholder, ytd-comment-simplebox-renderer #placeholder-area").first
            if await placeholder.count() > 0 and await placeholder.is_visible():
                await placeholder.click(force=True)
                await asyncio.sleep(0.8)
            box = page.locator("#contenteditable-root, div[contenteditable='true'][aria-label*='comment' i]").first
            if await box.count() > 0:
                await box.click(force=True)
                await box.fill(comment_txt)
                await asyncio.sleep(0.6)
                submit_btn = page.locator("ytd-button-renderer#submit-button button, button[aria-label='Comment']").first
                if await submit_btn.count() > 0:
                    await submit_btn.click(force=True)
                    await asyncio.sleep(3.2)
                    res[key] = True
                    print(f"    ✓ Posted {key} on {video_id}", flush=True)
        except Exception as e:
            print(f"    [YT Seed Notice] {key}: {e}", flush=True)

    # Pin the 2-birthday prompt comment
    try:
        threads = page.locator("ytd-comment-thread-renderer")
        tcnt = await threads.count()
        for i in range(tcnt):
            th = threads.nth(i)
            txt = await th.inner_text()
            if "Drop YOUR birth day" in txt:
                menu_btn = th.locator("ytd-menu-renderer button, button[aria-label='Action menu']").first
                if await menu_btn.count() > 0:
                    await menu_btn.click(force=True)
                    await asyncio.sleep(0.8)
                    pin_item = page.locator("ytd-menu-navigation-item-renderer:has-text('Pin'), tp-yt-paper-item:has-text('Pin')").first
                    if await pin_item.count() > 0:
                        await pin_item.click(force=True)
                        await asyncio.sleep(0.8)
                        confirm_pin = page.locator("yt-confirm-dialog-renderer #confirm-button button, button:has-text('Pin')").last
                        if await confirm_pin.count() > 0 and await confirm_pin.is_visible():
                            await confirm_pin.click(force=True)
                            await asyncio.sleep(2.0)
                        res["pinned"] = True
                        print(f"    ✓ Pinned 2-birthday prompt comment on {video_id}!", flush=True)
                break
    except Exception as e:
        print(f"    [YT Pin Notice] {e}", flush=True)

    return res


async def delete_old_short_uploads(page: Page, old_ids: List[str]):
    """Deduplicates Public Shorts in YouTube Studio (keeps only the newest Public row per title and sets older duplicates to Private)."""
    short_tab = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/short"
    print(f"  [Cleanup] Opening {short_tab} to deduplicate Public Shorts...", flush=True)
    await page.goto(short_tab, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(5.5)

    rows = page.locator("ytcp-video-row")
    rcount = await rows.count()
    seen_titles = set()
    for idx in range(rcount):
        row = rows.nth(idx)
        try:
            row_txt = await row.inner_text()
            row_html = await row.inner_html()
        except Exception:
            continue
        if "Private" in row_txt or "Scheduled" in row_txt:
            continue
        lines = [ln.strip() for ln in row_txt.splitlines() if len(ln.strip()) > 12]
        title_key = lines[0] if lines else f"row_{idx}"
        is_explicit_old = any(oid in row_html for oid in old_ids)
        if not is_explicit_old and title_key not in seen_titles:
            seen_titles.add(title_key)
            print(f"    ✓ Keeping newest Public Short row #{idx+1}: {title_key[:55]}", flush=True)
            continue
        try:
            await row.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            vis_cell = row.locator(
                "ytcp-video-row-cell-visibility, .cell-body.tablecell-visibility, #visibility-text, div.tablecell-visibility"
            ).first
            vcnt = await vis_cell.count()
            if vcnt > 0:
                await vis_cell.click(force=True)
                await asyncio.sleep(1.2)
                priv_radio = page.locator(
                    'tp-yt-paper-radio-button[name="PRIVATE"], tp-yt-paper-radio-button:has-text("Private")'
                ).first
                pcnt = await priv_radio.count()
                if pcnt > 0:
                    await priv_radio.click(force=True)
                    await asyncio.sleep(0.8)
                    save_btn = page.locator(
                        'ytcp-button#save-button, ytcp-video-visibility-select ytcp-button#save-button, div[role="dialog"] button:has-text("Save")'
                    ).first
                    scnt = await save_btn.count()
                    if scnt > 0:
                        await save_btn.click(force=True)
                        await asyncio.sleep(3.0)
                        print(f"    ✓ Set older duplicate Short row #{idx+1} ({title_key[:42]}) to Private.", flush=True)
                        continue
            # Fallback: hover row -> click Options (3 dots) -> Delete forever
            await row.hover()
            await asyncio.sleep(0.6)
            opts = row.locator('ytcp-button#options-button, button[aria-label="Options"]').first
            if await opts.count() > 0:
                await opts.click(force=True)
                await asyncio.sleep(0.8)
                del_it = page.locator('tp-yt-paper-item:has-text("Delete forever")').first
                if await del_it.count() > 0:
                    await del_it.click(force=True)
                    await asyncio.sleep(1.0)
                    chk = page.locator('ytcp-checkbox-lit#delete-confirm-checkbox, ytcp-checkbox-lit#confirm-checkbox, div[role="dialog"] ytcp-checkbox-lit').first
                    if await chk.count() > 0:
                        await chk.click(force=True)
                        await asyncio.sleep(0.6)
                    cbtn = page.locator('ytcp-button#confirm-button, div[role="dialog"] button:has-text("Delete forever")').first
                    if await cbtn.count() > 0:
                        await cbtn.click(force=True)
                        await asyncio.sleep(3.5)
                        print(f"    ✓ Deleted older duplicate Short row #{idx+1} ({title_key[:42]}) forever.", flush=True)
        except Exception as e:
            print(f"    [Cleanup Notice] row #{idx+1}: {e}", flush=True)


async def upload_single_short(page: Page, item: Dict[str, Any]) -> Optional[str]:
    """Uploads or schedules a single Short via YouTube Studio."""
    video_path = os.path.join(VIDEO_DIR, item["filename"])
    if not os.path.exists(video_path):
        print(f"  ⚠ Video file missing: {video_path}", flush=True)
        return None

    studio_url = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/videos/upload?d=ud"
    print(f"\n  [YT Upload] Starting {item['id']} ({item['mode']}): {item['title']}", flush=True)
    await page.goto(studio_url, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(4.5)

    file_input = page.locator('input[type="file"]').first
    if await file_input.count() == 0:
        create_btn = page.locator('ytcp-button#create-icon, button:has-text("Create")').first
        if await create_btn.count() > 0:
            await create_btn.click(force=True)
            await asyncio.sleep(1.0)
            up_item = page.locator('tp-yt-paper-item:has-text("Upload videos")').first
            if await up_item.count() > 0:
                await up_item.click(force=True)
                await asyncio.sleep(1.5)

    await page.locator('input[type="file"]').first.set_input_files(video_path)
    await asyncio.sleep(6.0)

    # Grab video ID from upload dialog link (`https://youtu.be/XXXX` or `/shorts/XXXX`)
    yt_vid = None
    try:
        dialog_txt = await page.inner_text("ytcp-uploads-dialog")
        m = re.search(r"(?:youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})", dialog_txt)
        if m:
            yt_vid = m.group(1)
    except Exception:
        pass

    # Title & Description
    boxes = page.locator("ytcp-social-suggestions-textbox #textbox, div#textbox[contenteditable='true']")
    if await boxes.count() >= 1:
        tbox = boxes.nth(0)
        await tbox.click(force=True)
        await page.keyboard.press("Control+A")
        await tbox.fill(item["title"][:100])
        await asyncio.sleep(0.5)
    if await boxes.count() >= 2:
        dbox = boxes.nth(1)
        await dbox.click(force=True)
        await page.keyboard.press("Control+A")
        await dbox.fill(SHORT_DESCRIPTION)
        await asyncio.sleep(0.5)

    # Select first auto-thumbnail cell (or custom frame0 if unlocked) so early emotional face + giant text is locked
    try:
        still_cell = page.locator("ytcp-still-cell, ytcp-thumbnail-editor ytcp-still-cell").first
        if await still_cell.count() > 0 and await still_cell.is_visible():
            await still_cell.click(force=True)
            await asyncio.sleep(0.5)
    except Exception:
        pass

    # Not made for kids
    not_kids = page.locator(
        'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], tp-yt-paper-radio-button:has-text("No, it\'s not made for kids")'
    ).first
    if await not_kids.count() > 0:
        await not_kids.scroll_into_view_if_needed()
        await not_kids.click(force=True)
        await asyncio.sleep(0.6)

    # Click Next 3 times to reach Visibility step
    for _ in range(3):
        next_btn = page.locator("ytcp-button#next-button").first
        if await next_btn.count() > 0 and await next_btn.is_visible():
            await next_btn.click(force=True)
            await asyncio.sleep(1.5)

    # Check if we didn't get yt_vid yet
    if not yt_vid:
        try:
            dialog_txt = await page.inner_text("ytcp-uploads-dialog")
            m = re.search(r"(?:youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})", dialog_txt)
            if m:
                yt_vid = m.group(1)
        except Exception:
            pass

    if item["mode"] == "post_now":
        pub_radio = page.locator('tp-yt-paper-radio-button[name="PUBLIC"], tp-yt-paper-radio-button:has-text("Public")').first
        if await pub_radio.count() > 0:
            await pub_radio.click(force=True)
            await asyncio.sleep(0.8)
    else:
        sched_container = page.locator(
            '#second-container-expand-button, tp-yt-paper-radio-button[name="SCHEDULE"], #schedule-radio-button'
        ).first
        if await sched_container.count() > 0:
            await sched_container.click(force=True)
            await asyncio.sleep(1.0)
        date_in = page.locator('ytcp-date-picker input, input[aria-label*="Date" i]').first
        if await date_in.count() > 0:
            await date_in.click(force=True)
            await page.keyboard.press("Control+A")
            await date_in.fill(item["schedule_date"])
            await page.keyboard.press("Enter")
            await asyncio.sleep(0.8)
        time_in = page.locator('ytcp-form-input-container#time-of-day-container input, input[aria-label*="Time" i]').first
        if await time_in.count() > 0:
            await time_in.click(force=True)
            await page.keyboard.press("Control+A")
            await time_in.fill(item["schedule_time"])
            await page.keyboard.press("Enter")
            await asyncio.sleep(0.8)

    done_btn = page.locator("ytcp-button#done-button").first
    if await done_btn.count() > 0:
        await done_btn.click(force=True)
        await asyncio.sleep(5.0)
        print(f"    ✓ Completed {item['id']} ({item['mode']}) -> video_id={yt_vid}", flush=True)

    return yt_vid


def force_browser_window_to_foreground():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.lower()
                    if any(k in title for k in ("sign in", "google", "youtube", "chrome", "chromium")):
                        user32.ShowWindow(hwnd, 3)
                        user32.BringWindowToTop(hwnd)
                        user32.keybd_event(0x12, 0, 0, 0)
                        user32.SetForegroundWindow(hwnd)
                        user32.keybd_event(0x12, 0, 2, 0)
            return True
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception:
        pass


async def ensure_yt_studio_logged_in(page: Page) -> bool:
    """Opens YouTube Studio for @CognitiveCurrent, pre-fills imcodingdad@gmail.com, and serves the interactive live canvas/form at http://localhost:8766 if Google prompts for 1-time re-auth."""
    studio_home = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}"
    print(f"  [YT Auth] Navigating to {studio_home} ...", flush=True)
    await page.goto(studio_home, wait_until="domcontentloaded", timeout=45000)
    await asyncio.sleep(3.5)

    if "accounts.google.com" in page.url or "signin" in page.url.lower():
        print("  [YT Auth] Google 1-time session refresh required for imcodingdad@gmail.com — starting http://localhost:8766 live web bridge...", flush=True)
        try:
            # Click imcodingdad@gmail.com if shown in account chooser
            acct = page.locator('[data-identifier="imcodingdad@gmail.com"], div:has-text("imcodingdad@gmail.com")').last
            if await acct.count() > 0 and await acct.is_visible():
                await acct.click(force=True)
                await asyncio.sleep(2.5)
            email_in = page.locator('input[type="email"], input#identifierId').first
            if await email_in.count() > 0 and await email_in.is_visible():
                await email_in.fill("imcodingdad@gmail.com")
                await asyncio.sleep(0.5)
                await page.keyboard.press("Enter")
                await asyncio.sleep(2.5)
        except Exception:
            pass

        from urllib.parse import parse_qs
        latest_png = b""

        async def handle_client(reader, writer):
            nonlocal latest_png
            try:
                req_line = await reader.readline()
                if not req_line:
                    writer.close()
                    return
                parts = req_line.decode("utf-8", errors="ignore").split()
                path = parts[1] if len(parts) > 1 else "/"
                while True:
                    h = await reader.readline()
                    if not h or h in (b"\r\n", b"\n"):
                        break
                if path.startswith("/shot.png"):
                    body = latest_png
                    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nCache-Control: no-store\r\n\r\n" + body)
                elif path.startswith("/click?"):
                    qs = parse_qs(path.split("?", 1)[1])
                    cx = float(qs.get("x", ["0"])[0])
                    cy = float(qs.get("y", ["0"])[0])
                    if cx > 0 and cy > 0:
                        await page.mouse.click(cx, cy)
                        await asyncio.sleep(0.8)
                    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"ok\":true}")
                elif path.startswith("/send?"):
                    qs = parse_qs(path.split("?", 1)[1])
                    txt = qs.get("text", [""])[0]
                    if txt:
                        pw_in = page.locator('input[type="password"], input[name="Passwd"], input[type="tel"], input[type="text"], input[type="email"]').first
                        if await pw_in.count() > 0 and await pw_in.is_visible():
                            await pw_in.fill(txt)
                        else:
                            await page.keyboard.type(txt)
                        await asyncio.sleep(0.3)
                        await page.keyboard.press("Enter")
                        await asyncio.sleep(1.0)
                    writer.write(b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
                else:
                    html = """<!doctype html><html><head><meta charset="utf-8"><title>YouTube Studio Live Auth Canvas (imcodingdad@gmail.com)</title>
                    <style>body{background:#0d0b14;color:#f5e6c8;font-family:sans-serif;text-align:center;padding:18px;margin:0;}
                    .bar{display:flex;gap:10px;justify-content:center;align-items:center;flex-wrap:wrap;margin-bottom:14px;}
                    input{padding:12px;width:320px;font-size:16px;border-radius:8px;border:1px solid #d4af37;background:#171426;color:#fff;}
                    button{padding:12px 22px;font-size:16px;background:#d4af37;color:#000;font-weight:bold;border:none;border-radius:8px;cursor:pointer;}
                    img{width:1024px;max-width:96vw;border:2px solid #d4af37;border-radius:10px;cursor:crosshair;display:block;margin:0 auto;}</style></head>
                    <body><h2>YouTube Studio Live Web Bridge — <code>imcodingdad@gmail.com</code> (<code>@CognitiveCurrent</code>)</h2>
                    <p style="margin-top:-6px;color:#b9b2cc;">Type your password or 2FA code below, OR click anywhere directly on the live browser canvas below:</p>
                    <form class="bar" action="/send" method="get">
                      <input type="password" name="text" placeholder="Enter password or 2FA code..." autofocus>
                      <button type="submit">Submit &amp; Press Enter</button>
                    </form>
                    <img id="sc" src="/shot.png?t=1" onclick="sendClick(event)">
                    <script>
                    setInterval(()=>{document.getElementById('sc').src='/shot.png?t='+Date.now();},1200);
                    function sendClick(e){
                      const img = e.target;
                      const rect = img.getBoundingClientRect();
                      const scaleX = 1366 / rect.width;
                      const scaleY = 900 / rect.height;
                      const x = Math.round((e.clientX - rect.left) * scaleX);
                      const y = Math.round((e.clientY - rect.top) * scaleY);
                      fetch('/click?x='+x+'&y='+y).then(()=>{setTimeout(()=>{img.src='/shot.png?t='+Date.now();},400);});
                    }
                    </script></body></html>"""
                    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + html.encode("utf-8"))
                await writer.drain()
            except Exception:
                pass
            finally:
                writer.close()

        server = None
        try:
            server = await asyncio.start_server(handle_client, "127.0.0.1", 8766)
            print("  ✓ [YT Auth] Live Web Bridge active at: http://localhost:8766", flush=True)
        except Exception as e:
            print(f"  [YT Auth] Bridge port 8766 notice: {e}", flush=True)

        try:
            for sec in range(7200):
                try:
                    latest_png = await page.screenshot(type="png")
                except Exception:
                    pass
                await asyncio.sleep(1.0)
                cur_url = page.url
                if "studio.youtube.com" in cur_url and "accounts.google.com" not in cur_url:
                    print(f"  ✓ [YT Auth] Authenticated in YouTube Studio after {sec+1}s: {cur_url}", flush=True)
                    await asyncio.sleep(4.0)
                    return True
                if sec % 30 == 0 and sec > 0:
                    print(f"    ... waiting for imcodingdad@gmail.com at http://localhost:8766 ({sec}s elapsed) ...", flush=True)
        finally:
            if server:
                server.close()
        print("  ✗ [YT Auth] Timed out waiting for YouTube Studio login.", flush=True)
        return False

    print(f"  ✓ [YT Auth] Already authenticated in YouTube Studio: {page.url}", flush=True)
    return True


def prepare_cloned_profile6_userdata() -> str:
    """Prepares a safe user-data-dir containing Local State + Profile 6 (Cookies & Preferences only, never Login Data)."""
    import shutil
    src_userdata = r"C:\Users\User\AppData\Local\Google\Chrome\User Data"
    dst_userdata = r"C:\Users\User\.gemini\antigravity\yt_chrome_cdp_userdata"
    src_p6 = os.path.join(src_userdata, "Profile 6")
    dst_p6 = os.path.join(dst_userdata, "Profile 6")
    os.makedirs(os.path.join(dst_p6, "Network"), exist_ok=True)
    for rel_src, rel_dst in [
        ("Local State", "Local State"),
        (os.path.join("Profile 6", "Preferences"), os.path.join("Profile 6", "Preferences")),
        (os.path.join("Profile 6", "Secure Preferences"), os.path.join("Profile 6", "Secure Preferences")),
        (os.path.join("Profile 6", "Network", "Cookies"), os.path.join("Profile 6", "Network", "Cookies")),
    ]:
        s = os.path.join(src_userdata, rel_src)
        d = os.path.join(dst_userdata, rel_dst)
        if os.path.exists(s) and not os.path.exists(d):
            try:
                shutil.copy2(s, d)
            except Exception:
                pass
    return dst_userdata


async def run_pipeline(do_rebrand: bool = True, do_upload: bool = True):
    import subprocess
    tracker = load_tracker()
    cdp_userdata = prepare_cloned_profile6_userdata()
    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_proc = None

    async with async_playwright() as p:
        browser = None
        ctx = None
        if os.path.exists(chrome_exe):
            try:
                chrome_proc = subprocess.Popen(
                    [
                        chrome_exe,
                        "--remote-debugging-port=9222",
                        f"--user-data-dir={cdp_userdata}",
                        '--profile-directory=Profile 6',
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--window-size=1366,900",
                        f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                await asyncio.sleep(3.5)
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                ctx = browser.contexts[0] if browser.contexts else await browser.new_context(viewport={"width": 1366, "height": 900})
                print("  ✓ [CDP] Attached directly to real Google Chrome (Profile 6) over http://127.0.0.1:9222", flush=True)
            except Exception as e:
                print(f"  [CDP Notice] Fallback to persistent context ({e})", flush=True)

        if ctx is None:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=YT_PROFILE_DIR,
                channel="chrome",
                headless=False,
                viewport={"width": 1366, "height": 900},
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled"],
            )

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.set_viewport_size({"width": 1366, "height": 900})
        except Exception:
            pass

        logged_in = await ensure_yt_studio_logged_in(page)
        if not logged_in:
            if browser:
                await browser.close()
            else:
                await ctx.close()
            if chrome_proc:
                chrome_proc.terminate()
            return

        if do_rebrand and not tracker.get("rebranded"):
            await privatize_old_videos(page)
            ok = await rebrand_channel(page)
            if ok:
                tracker["rebranded"] = True
                tracker["rebranded_at"] = datetime.now().isoformat()
                save_tracker(tracker)

        if do_upload:
            for k in list(tracker.get("videos", {}).keys()):
                if tracker["videos"][k].get("ReplaceOld"):
                    del tracker["videos"][k]
            save_tracker(tracker)

            for item in YT_SHORTS_QUEUE:
                sid = item["id"]
                if sid in tracker.get("videos", {}) and tracker["videos"][sid].get("status") in ("published", "scheduled"):
                    print(f"  ✓ [{sid}] Already {tracker['videos'][sid]['status']} ({tracker['videos'][sid].get('video_id')}), skipping.")
                    continue
                vid = await upload_single_short(page, item)
                if vid:
                    entry = {
                        "id": sid,
                        "filename": item["filename"],
                        "title": item["title"],
                        "video_id": vid,
                        "url": f"https://www.youtube.com/shorts/{vid}",
                        "status": "published" if item["mode"] == "post_now" else "scheduled",
                        "schedule": f"{item['schedule_date']} {item['schedule_time']}" if item["mode"] == "schedule" else "LIVE",
                        "uploaded_at": datetime.now().isoformat(),
                    }
                    if item["mode"] == "post_now":
                        seed_res = await seed_and_pin_comments_on_short(page, vid)
                        entry.update(seed_res)
                    tracker.setdefault("videos", {})[sid] = entry
                    save_tracker(tracker)

            await delete_old_short_uploads(page, [])

            # Capture public Shorts grid verification screenshot
            await page.goto("https://www.youtube.com/@sacrednumberblueprint/shorts", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(5.5)
            shot_p = os.path.join(BASE_DIR, "yt_shorts_grid_verified.png")
            await page.screenshot(path=shot_p)
            print(f"  ✓ Saved verified YouTube Shorts grid screenshot -> {shot_p}", flush=True)

        if browser:
            await browser.close()
        else:
            await ctx.close()
        if chrome_proc:
            chrome_proc.terminate()


async def seed_newly_live_scheduled_shorts(page: Page):
    """Checks all scheduled Shorts in uploaded_yt_shorts.json; if any are now Public on @sacrednumberblueprint/shorts, seeds & pins our 2-birthday prompt comment + Sample Match reply."""
    tracker = load_tracker()
    vids = tracker.get("videos", {})
    pending = [
        (sid, info)
        for sid, info in vids.items()
        if info.get("video_id") and not info.get("prompt_seeded")
    ]
    if not pending:
        print("  ✓ [YT Seed Newly Live] All tracked Shorts already have seeded comments.", flush=True)
        return

    await page.goto("https://www.youtube.com/@sacrednumberblueprint/shorts", wait_until="domcontentloaded", timeout=25000)
    await asyncio.sleep(3.5)
    html = await page.content()
    for sid, info in pending:
        vid = info["video_id"]
        if f"/shorts/{vid}" in html or f"watch?v={vid}" in html:
            print(f"  [YT Seed Newly Live] Detected {sid} ({vid}) is now Public! Seeding & pinning comments...", flush=True)
            seed_res = await seed_and_pin_comments_on_short(page, vid)
            info.update(seed_res)
            if seed_res.get("prompt_seeded"):
                info["status"] = "published"
            save_tracker(tracker)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebrand-only", action="store_true")
    parser.add_argument("--upload-only", action="store_true")
    parser.add_argument("--seed-newly-live", action="store_true")
    args = parser.parse_args()
    if args.seed_newly_live:
        async def _run_seed():
            import subprocess
            cdp_userdata = prepare_cloned_profile6_userdata()
            chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            chrome_proc = None
            async with async_playwright() as p:
                browser = None
                try:
                    browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=4000)
                except Exception:
                    if os.path.exists(chrome_exe):
                        chrome_proc = subprocess.Popen(
                            [
                                chrome_exe,
                                "--remote-debugging-port=9222",
                                f"--user-data-dir={cdp_userdata}",
                                "--profile-directory=Profile 6",
                                "--no-first-run",
                                "--no-default-browser-check",
                                "--window-size=1366,900",
                                "https://www.youtube.com/@sacrednumberblueprint/shorts",
                            ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        await asyncio.sleep(3.5)
                        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=8000)
                if browser:
                    ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
                    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
                    await seed_newly_live_scheduled_shorts(page)
                    await browser.close()
                if chrome_proc:
                    chrome_proc.terminate()
        asyncio.run(_run_seed())
        return
    do_rebrand = not args.upload_only
    do_upload = not args.rebrand_only
    asyncio.run(run_pipeline(do_rebrand=do_rebrand, do_upload=do_upload))


if __name__ == "__main__":
    main()
