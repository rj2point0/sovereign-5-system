#!/usr/bin/env python3
"""
SACRED NUMBER BLUEPRINT — SOCIAL PROOF SAMPLE READING COMMENT SEEDER
====================================================================
Posts a 138-char automod-safe creator follow-up comment on our active live
TikToks (short_20, short_22, short_25, short_28) and Instagram Reels showing
a real example 2-birthday reading so cold scrollers see immediate social proof:
  "📌 Top pair asked in DMs today: Day 19 × Day 23 = 96% Twin-Spark Lock 🔥 Intense pull, but one goes quiet when stressed! Drop your 2 days 👇"
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\tiktok_browser_profile"
IG_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"
TRACKER_PATH = os.path.join(BASE_DIR, "seeded_sample_replies.json")

SAMPLE_MATCH_COMMENT = (
    "📌 Top pair asked in DMs today: Day 19 × Day 23 = 96% Twin-Spark Lock 🔥 "
    "Intense pull, but one goes quiet when stressed! Drop your 2 days 👇"
)

TIKTOK_TARGETS = [
    {
        "id": "short_33",
        "video_id": None,
        "title_match": "Why you keep falling for people who pull away",
    },
    {
        "id": "short_32",
        "video_id": None,
        "title_match": "Left on read at 11:42 PM? Instead of sending a long paragraph",
    },
    {
        "id": "short_31",
        "video_id": "7704784636659961102",
        "title_match": "He texted me every morning for 6 weeks, then went cold on a Tuesday",
    },
    {
        "id": "short_30",
        "video_id": None,
        "title_match": "Are your birthdays endgame—or just a 3-month karmic lesson?",
    },
    {
        "id": "short_29",
        "video_id": None,
        "title_match": "Dating someone born on the 4th, 7th, 8th, 13th, 16th, 17th, 22nd, 25th, 26th, or 31st?",
    },
    {
        "id": "short_28",
        "video_id": "7704068444592950541",
        "title_match": "Born on the 2nd, 6th, 9th, 11th, 15th, 18th, 20th, 24th, 27th, or 29th? Why you always care more first",
    },
    {
        "id": "short_27",
        "video_id": None,
        "title_match": "Born on the 3rd, 4th, 8th, 9th, 12th, 13th, 17th, 18th, 21st, 22nd, 26th, 27th, 30th, or 31st?",
    },
    {
        "id": "short_26",
        "video_id": None,
        "title_match": "If they were born on the 2nd, 6th, 7th, 11th, 15th, 16th, 20th, 24th, or 25th, silence does not mean",
    },
    {
        "id": "short_25",
        "video_id": "7703630255013104910",
        "title_match": "Born on the 1st, 5th, 10th, 14th, 19th, 23rd, or 28th? Intense chemistry can be a karmic trap",
    },
    {
        "id": "short_24",
        "video_id": None,
        "title_match": "Born on the 1st, 3rd, 5th, 10th, 12th, 14th, 19th, 21st, 23rd, 28th, or 30th",
    },
    {
        "id": "short_23",
        "video_id": "7704542849571900685",
        "title_match": "Born on the 2nd, 6th, 9th, 11th, 15th, 20th, 24th, or 29th? Stop double texting",
    },
    {
        "id": "short_22",
        "video_id": "7703622747489963278",
        "title_match": "Born on the 4th, 7th, 8th, 16th, 17th, 25th, or 26th? Why they act obsessed",
    },
    {
        "id": "short_21",
        "video_id": None,
        "title_match": "Born on the 1st, 4th, 7th, 8th, 9th, 10th, 13th, 16th, 17th",
    },
    {
        "id": "short_20",
        "video_id": "7704137393049308430",
        "title_match": "Every birthday has 3 natural soulmate dates—and 3 dates that drain your energy",
    },
]

IG_TARGETS = [
    {"id": "short_33", "shortcode": "DfX4Mdsuqc1"},
    {"id": "short_32", "shortcode": "DfX4E4QOsUB"},
    {"id": "short_31", "shortcode": "DfX39C3Owgn"},
    {"id": "short_24", "shortcode": "DfWMtB2OLJc"},
    {"id": "short_23", "shortcode": "DfWMlPuumkQ"},
    {"id": "short_30", "shortcode": "DfVoPn9u4rG"},
    {"id": "short_29", "shortcode": "DfVoH1Lu2xB"},
    {"id": "short_27", "shortcode": "DfVoASXOCCL"},
    {"id": "short_26", "shortcode": "DfVn4f2uqDa"},
    {"id": "short_28", "shortcode": "DfS6Iu5OEhv"},
    {"id": "short_25", "shortcode": "DfP3a8aOUPF"},
    {"id": "short_22", "shortcode": "DfPp_HOOJS3"},
    {"id": "short_21", "shortcode": "DfTR1XxublV"},
    {"id": "short_20", "shortcode": "DfN3fVRul_X"},
]


def load_tracker() -> Dict[str, Any]:
    if os.path.exists(TRACKER_PATH):
        try:
            with open(TRACKER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tiktok": {}, "instagram": {}}


def save_tracker(data: Dict[str, Any]):
    data["updated_at"] = datetime.now().isoformat()
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def delete_tiktok_video_by_id(page, vid: str):
    if not vid:
        return
    try:
        await page.goto(f"https://www.tiktok.com/@sacrednumberblueprint/video/{vid}", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.0)
        more_btn = page.locator('[data-e2e="video-setting"], [aria-label*="More"], svg[class*=" Ellipsis"]').first
        if await more_btn.count() > 0:
            await more_btn.hover()
            await asyncio.sleep(0.6)
            await more_btn.click(force=True)
            await asyncio.sleep(1.0)
        del_btn = page.locator('[data-e2e="video-delete"], li:has-text("Delete"), button:has-text("Delete"), span:text-is("Delete")').first
        if await del_btn.count() > 0 and await del_btn.is_visible():
            await del_btn.click(force=True)
            await asyncio.sleep(1.2)
            confirm_btn = page.locator('button[data-e2e="video-modal-delete"], div[role="dialog"] button:has-text("Delete")').first
            if await confirm_btn.count() > 0 and await confirm_btn.is_visible():
                await confirm_btn.click(force=True)
                await asyncio.sleep(3.0)
                print(f"  ✓ [TT Cleanup] Deleted old 13.9s scheduled video {vid}!", flush=True)
    except Exception as e:
        print(f"  ⚠ [TT Cleanup] Note while deleting {vid}: {e}", flush=True)


async def seed_tiktok_sample_replies(delete_old_short_21_vid: str = ""):
    assert len(SAMPLE_MATCH_COMMENT) <= 140, f"Comment too long: {len(SAMPLE_MATCH_COMMENT)}"
    tracker = load_tracker()
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=TT_PROFILE_DIR,
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        if delete_old_short_21_vid:
            await delete_tiktok_video_by_id(page, delete_old_short_21_vid)

        for t in TIKTOK_TARGETS:
            tid = t["id"]
            if tid in tracker.get("tiktok", {}):
                print(f"  ✓ [TT {tid}] Sample match comment already seeded ({tracker['tiktok'][tid]['video_id']}), skipping.", flush=True)
                continue

            await page.goto("https://www.tiktok.com/@sacrednumberblueprint", wait_until="domcontentloaded", timeout=45000)
            try:
                await page.locator('a[href*="/video/"]').first.wait_for(state="attached", timeout=20000)
            except Exception:
                pass
            await asyncio.sleep(3.0)

            vid = t.get("video_id")
            prof_videos = await page.evaluate(
                """() => Array.from(document.querySelectorAll('a[href*="/video/"]')).map(a => {
                    const card = a.closest('[data-e2e="user-post-item"]') || a.parentElement || a;
                    return {
                        href: a.href,
                        imgAlt: a.querySelector('img') ? (a.querySelector('img').alt || '') : '',
                        cardText: card ? (card.innerText || '') : ''
                    };
                })"""
            )
            matched_live_vid = None
            for v in prof_videos:
                if (vid and vid in v.get("href", "")) or (t["title_match"].lower()[:45] in v.get("imgAlt", "").lower()):
                    c_txt = v.get("cardText", "").lower()
                    if "schedule" in c_txt or re.search(r"202\d\s*-\s*\d+", c_txt):
                        continue
                    m = re.search(r"/video/(\d+)", v.get("href", ""))
                    if m:
                        matched_live_vid = m.group(1)
                        break

            if not matched_live_vid:
                print(f"  ⚠ [TT {tid}] Video not found live on profile grid yet.", flush=True)
                continue

            box = await page.evaluate(
                """(v) => {
                    const a = document.querySelector(`a[href*="${v}"]`);
                    if (!a) return null;
                    const card = a.closest('[data-e2e="user-post-item"]') || a.parentElement || a;
                    card.scrollIntoView({block: 'center'});
                    const r = card.getBoundingClientRect();
                    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                }""",
                matched_live_vid,
            )
            if not box:
                continue
            await asyncio.sleep(0.4)
            await page.mouse.click(box["x"], box["y"])
            await asyncio.sleep(4.2)

            already = await page.evaluate(
                """() => {
                    const items = Array.from(document.querySelectorAll('[data-e2e="comment-level-1"], [class*="DivCommentItemContainer"], [class*="CommentText"]'));
                    return items.some(el => (el.innerText || '').includes('Top pair asked in DMs today'));
                }"""
            )
            if already:
                print(f"  ✓ [TT {tid}] Sample match comment already present on {matched_live_vid}.", flush=True)
                tracker.setdefault("tiktok", {})[tid] = {
                    "video_id": matched_live_vid,
                    "comment": SAMPLE_MATCH_COMMENT,
                    "seeded_at": datetime.now().isoformat(),
                }
                save_tracker(tracker)
                continue

            input_selectors = [
                'div[data-e2e="comment-input"] div[contenteditable="true"]',
                'div[data-e2e="comment-text"]',
                'div.public-DraftEditor-content[contenteditable="true"]',
            ]
            target_input = None
            for sel in input_selectors:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click()
                    await asyncio.sleep(0.4)
                    target_input = loc
                    break

            if target_input is None:
                print(f"  ⚠ [TT {tid}] Could not focus comment box on {matched_live_vid}.", flush=True)
                continue

            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await asyncio.sleep(0.2)
            await target_input.press_sequentially(SAMPLE_MATCH_COMMENT, delay=15)
            await asyncio.sleep(1.0)

            post_btn = page.locator('button[data-e2e="comment-post"]').first
            if await post_btn.count() > 0 and await post_btn.is_visible():
                await post_btn.click(force=True)
            else:
                await page.keyboard.press("Enter")

            await asyncio.sleep(4.2)
            print(f"  ✓ [TT {tid}] Posted Sample Match follow-up comment ({len(SAMPLE_MATCH_COMMENT)} chars) on {matched_live_vid}!", flush=True)
            tracker.setdefault("tiktok", {})[tid] = {
                "video_id": matched_live_vid,
                "comment": SAMPLE_MATCH_COMMENT,
                "seeded_at": datetime.now().isoformat(),
            }
            save_tracker(tracker)

        await ctx.close()


async def seed_ig_sample_replies():
    assert len(SAMPLE_MATCH_COMMENT) <= 140, f"Comment too long: {len(SAMPLE_MATCH_COMMENT)}"
    tracker = load_tracker()
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=IG_PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.instagram.com/sacrednumberblueprint/reels/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.0)
        await page.evaluate("window.scrollBy(0, 1200)")
        await asyncio.sleep(2.5)

        for t in IG_TARGETS:
            tid = t["id"]
            sc = t["shortcode"]
            if tid in tracker.get("instagram", {}) and tracker["instagram"][tid].get("shortcode") == sc:
                print(f"  ✓ [IG {tid}] Sample match comment already seeded ({sc}), skipping.", flush=True)
                continue

            link = page.locator(f'a[href*="/{sc}/"]').first
            if await link.count() == 0:
                print(f"  ⚠ [IG {tid}] Shortcode {sc} not visible in grid.", flush=True)
                continue

            await link.click(force=True)
            await asyncio.sleep(3.5)

            for sel in ['textarea[aria-label*="Add a comment"]', 'textarea[placeholder*="Add a comment"]', 'form textarea']:
                box = page.locator(sel).first
                if await box.count() > 0 and await box.is_visible():
                    dialog_txt = await page.inner_text('div[role="dialog"]') if await page.locator('div[role="dialog"]').count() > 0 else await page.inner_text("body")
                    if "Top pair asked in DMs today" in dialog_txt:
                        print(f"  ✓ [IG {tid}] Sample match comment already present on {sc}.", flush=True)
                    else:
                        await box.click(force=True)
                        await asyncio.sleep(0.3)
                        await box.fill(SAMPLE_MATCH_COMMENT)
                        await asyncio.sleep(0.5)
                        post_btn = page.locator('div[role="button"]:text-is("Post"), button:text-is("Post"), form button[type="submit"]').first
                        if await post_btn.count() > 0 and await post_btn.is_visible():
                            await post_btn.click(force=True)
                        else:
                            await page.keyboard.press("Enter")
                        await asyncio.sleep(3.2)
                        print(f"  ✓ [IG {tid}] Posted Sample Match follow-up comment ({len(SAMPLE_MATCH_COMMENT)} chars) on /reel/{sc}/!", flush=True)

                    tracker.setdefault("instagram", {})[tid] = {
                        "shortcode": sc,
                        "comment": SAMPLE_MATCH_COMMENT,
                        "seeded_at": datetime.now().isoformat(),
                    }
                    save_tracker(tracker)
                    break

            close_btn = page.locator('svg[aria-label="Close"]').first
            if await close_btn.count() > 0:
                await close_btn.click(force=True)
            else:
                await page.keyboard.press("Escape")
            await asyncio.sleep(1.2)

        await ctx.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["tiktok", "ig", "all"], default="all")
    parser.add_argument("--delete-vid", default="")
    args = parser.parse_args()
    if args.platform in ("tiktok", "all"):
        asyncio.run(seed_tiktok_sample_replies(delete_old_short_21_vid=args.delete_vid))
    if args.platform in ("ig", "all"):
        asyncio.run(seed_ig_sample_replies())


if __name__ == "__main__":
    main()
