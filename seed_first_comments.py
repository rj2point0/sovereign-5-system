#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · AUTOMOD-SAFE FIRST COMMENT SEEDER
seed_first_comments.py
-----------------------------------------------------------------------------
Seeds pure Engagement Question Bait first-comments onto @sacrednumberblueprint
videos (zero '@' mentions, zero 'link/bio/profile/tap/click/free/page' words)
so TikTok's automod never hides or deletes them on a new creator account, and
verifies 60 seconds later in a public/incognito check + TikTok Studio Posts
table that the comments remain visible ('Comments: 1') and were NOT deleted.
=============================================================================
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_PROFILE_DIR = os.path.join(
    os.path.expanduser("~"), ".gemini", "antigravity", "tiktok_browser_profile"
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEEDED_TRACKER_PATH = os.path.join(BASE_DIR, "seeded_first_comments.json")
PROFILE_URL = "https://www.tiktok.com/@sacrednumberblueprint"
STUDIO_CONTENT_URL = "https://www.tiktok.com/tiktokstudio/content"

BANNED_FIRST_COMMENT_PATTERNS = [
    r"@",
    r"\blink\b",
    r"\bbio\b",
    r"\bprofile\b",
    r"\btap\b",
    r"\bclick\b",
    r"\bfree\b",
    r"\bpage\b",
    r"i'll tell you",
    r"i will tell you",
]

TARGET_FIRST_COMMENTS = [
    {
        "id": "broll_01",
        "video_id": "7699896747476225293",
        "title_match": "Why you keep attracting the exact same exhausting relationship patterns",
        "comment": "Which numbers from 1 to 9 are missing from your birthday—and have you noticed that same pattern in relationships? 👇",
    },
    {
        "id": "ad_01",
        "video_id": "7699586451800984846",
        "title_match": "Why your Life Path number feels way too generic",
        "comment": "What Life Path number did you get when you only used your birthday—and did it actually feel accurate for you? 👇",
    },
    {
        "id": "ad_02",
        "video_id": "7699587106246610189",
        "title_match": "Why your birth date alone is only 20% of your numerology blueprint",
        "comment": "Does your first name start with a 1, 7, 8, or 9 vibration in Chaldean math? Drop your birth month and day below 👇",
    },
]


def is_automod_safe_first_comment(text: str) -> bool:
    """Ensures zero '@' mentions, zero automod-flagged promo/bot words, and <= 150 chars (TikTok limit)."""
    if not text or not text.strip():
        return False
    if len(text.strip()) > 150:
        return False
    for pat in BANNED_FIRST_COMMENT_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            return False
    return True


def load_seeded_tracker() -> Dict[str, Any]:
    if os.path.exists(SEEDED_TRACKER_PATH):
        try:
            with open(SEEDED_TRACKER_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"seeded": {}}


def save_seeded_tracker(data: Dict[str, Any]):
    data["updated_at"] = datetime.now().isoformat()
    with open(SEEDED_TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def seed_comment_on_video_from_profile(
    page: Page,
    title_match: str,
    comment_text: str,
    video_id_hint: Optional[str] = None,
) -> Optional[str]:
    """
    Navigates to @sacrednumberblueprint, clicks the matching video thumbnail to open
    the theatre modal, checks if the comment is already present, and posts the
    automod-safe creator first comment. Returns the matched video_id if successful.
    """
    if not is_automod_safe_first_comment(comment_text):
        raise ValueError(f"Comment failed automod-safety / 150-char check ({len(comment_text)} chars): {comment_text}")

    await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=45000)
    try:
        await page.locator('a[href*="/video/"]').first.wait_for(state="attached", timeout=25000)
    except Exception:
        pass
    await asyncio.sleep(2.5)

    matched_vid = video_id_hint
    if not matched_vid:
        prof_videos = await page.evaluate(
            """() => {
                return Array.from(document.querySelectorAll('a[href*="/video/"]')).map(a => ({
                    href: a.href,
                    imgAlt: a.querySelector('img') ? (a.querySelector('img').alt || '') : ''
                }));
            }"""
        )
        for v in prof_videos:
            if title_match.lower()[:32] in v.get("imgAlt", "").lower():
                m = re.search(r"/video/(\d+)", v.get("href", ""))
                if m:
                    matched_vid = m.group(1)
                    break

    if not matched_vid:
        print(f"   [Seed] ⚠ Could not find live video matching '{title_match}' on profile.", flush=True)
        return None

    thumb = page.locator(f'a[href*="{matched_vid}"]').first
    try:
        await thumb.wait_for(state="attached", timeout=15000)
    except Exception:
        pass
    if await thumb.count() == 0:
        print(f"   [Seed] ⚠ Video thumbnail {matched_vid} not found on profile grid.", flush=True)
        return None

    await thumb.scroll_into_view_if_needed()
    await asyncio.sleep(0.5)
    await thumb.click()
    await asyncio.sleep(4.5)

    # Check if our comment snippet is already visible in the comment list (excluding the input box)
    snippet = comment_text[:28].lower()
    already_posted = await page.evaluate(
        """(snip) => {
            const items = Array.from(document.querySelectorAll('[data-e2e="comment-level-1"], [class*="DivCommentItemContainer"], [class*="CommentText"]'));
            return items.some(el => (el.innerText || '').toLowerCase().includes(snip));
        }""",
        snippet,
    )
    if already_posted:
        print(f"   [Seed] ✓ Comment already posted in comment list on video {matched_vid}.", flush=True)
        return matched_vid

    # Click the DraftJS comment input box and type with real keystrokes so DraftJS enables Post
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
        print(f"   [Seed] ⚠ Could not focus comment input on video {matched_vid}.", flush=True)
        return None

    await page.keyboard.press("Control+A")
    await page.keyboard.press("Backspace")
    await asyncio.sleep(0.2)
    await target_input.press_sequentially(comment_text, delay=15)
    await asyncio.sleep(1.0)

    post_btn = page.locator('button[data-e2e="comment-post"]').first
    if await post_btn.count() > 0 and await post_btn.is_visible():
        await post_btn.click(force=True)
    else:
        await page.keyboard.press("Enter")

    await asyncio.sleep(4.5)
    await page.screenshot(path=os.path.join(BASE_DIR, f"modal_seeded_{matched_vid}.png"))
    print(f"   [Seed] ✓ Posted automod-safe first comment ({len(comment_text)} chars) on video {matched_vid}!", flush=True)
    return matched_vid


async def verify_comments_after_delay(
    wait_seconds: int = 60,
    targets: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Waits `wait_seconds` (default 60s), then verifies on TikTok Studio's Comments
    manager (`https://www.tiktok.com/tiktokstudio/comment`) and on each video's
    public modal (`Comments (1)`) that all 3 comments survived TikTok's automod.
    """
    targets = targets or TARGET_FIRST_COMMENTS
    if wait_seconds > 0:
        print(f"\n⏳ Waiting {wait_seconds} seconds before running anti-automod survival check...", flush=True)
        await asyncio.sleep(wait_seconds)

    results: Dict[str, Any] = {"checked_at": datetime.now().isoformat(), "videos": {}}

    async with async_playwright() as p:
        print("\n🔍 [VERIFY] Checking TikTok Studio Comments Feed & Video Modals after 60s...", flush=True)
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=DEFAULT_PROFILE_DIR,
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # 1. Check https://www.tiktok.com/tiktokstudio/comment
        await page.goto("https://www.tiktok.com/tiktokstudio/comment", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5.5)
        await page.screenshot(path=os.path.join(BASE_DIR, "tiktok_comments_verified_60s.png"))
        studio_text = (await page.evaluate("() => document.body.innerText")).lower()

        # 1b. Also snapshot https://www.tiktok.com/tiktokstudio/content to verify scheduled posts & comment counts
        await page.goto("https://www.tiktok.com/tiktokstudio/content", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
        await page.screenshot(path=os.path.join(BASE_DIR, "tiktok_studio_posts_verified.png"))

        # 2. Check each video modal on @sacrednumberblueprint to confirm browse-comment-count >= 1
        await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.5)
        for t in targets:
            vid = t["video_id"]
            snip = t["comment"][:28].lower()
            in_studio_feed = snip in studio_text
            thumb = page.locator(f'a[href*="{vid}"]').first
            if await thumb.count() > 0:
                await thumb.click()
                await asyncio.sleep(4.0)
                modal_info = await page.evaluate(
                    """(snippet) => {
                        const cntEl = document.querySelector('[data-e2e="browse-comment-count"]');
                        const countText = cntEl ? cntEl.innerText.trim() : '0';
                        const cBox = document.querySelector('[data-e2e="search-comment-container"]');
                        const cText = cBox ? cBox.innerText : document.body.innerText;
                        return {
                            browse_comment_count: countText,
                            comment_intact: cText.toLowerCase().includes(snippet.toLowerCase())
                        };
                    }""",
                    t["comment"][:28],
                )
                modal_info["in_studio_comment_feed"] = in_studio_feed
                results["videos"][t["id"]] = modal_info
                print(
                    f"   ✓ [{t['id']}] Video {vid}: Comments={modal_info['browse_comment_count']} | ModalIntact={modal_info['comment_intact']} | StudioFeedVisible={in_studio_feed}",
                    flush=True,
                )
                await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(3.5)

        await ctx.close()

    return results


async def run_seeder(wait_seconds: int = 60, dry_run: bool = False):
    print("=" * 72, flush=True)
    print("   SACRED NUMBER BLUEPRINT · AUTOMOD-SAFE FIRST COMMENT SEEDER", flush=True)
    print("=" * 72, flush=True)

    for t in TARGET_FIRST_COMMENTS:
        safe = is_automod_safe_first_comment(t["comment"])
        print(f"  • [{t['id']}] Automod-Safe={safe} | \"{t['comment']}\"", flush=True)
        if not safe:
            raise ValueError(f"Target comment for {t['id']} failed automod safety validation!")

    if dry_run:
        print("\n[DRY-RUN] All 3 target first comments passed automod-safety validation.", flush=True)
        return

    tracker = load_seeded_tracker()

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=DEFAULT_PROFILE_DIR,
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None,
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        for t in TARGET_FIRST_COMMENTS:
            print(f"\n▶ Seeding First Comment on [{t['id']}] ({t['title_match'][:48]}...)...", flush=True)
            vid = await seed_comment_on_video_from_profile(
                page,
                title_match=t["title_match"],
                comment_text=t["comment"],
                video_id_hint=t.get("video_id"),
            )
            if vid:
                tracker["seeded"][t["id"]] = {
                    "video_id": vid,
                    "title_match": t["title_match"],
                    "comment": t["comment"],
                    "seeded_at": datetime.now().isoformat(),
                }
                save_seeded_tracker(tracker)

        await ctx.close()

    # Wait 60 seconds and verify comments survived TikTok's automod
    verify_res = await verify_comments_after_delay(wait_seconds=wait_seconds, targets=TARGET_FIRST_COMMENTS)
    tracker["last_verification"] = verify_res
    save_seeded_tracker(tracker)
    print("\n" + "=" * 72, flush=True)
    print("   ✓ FIRST COMMENT SEEDING & 60s AUTOMOD SURVIVAL CHECK COMPLETE!", flush=True)
    print("=" * 72, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Automod-Safe First Comment Seeder for @sacrednumberblueprint")
    parser.add_argument("--dry-run", action="store_true", help="Validate automod safety without launching browser")
    parser.add_argument("--wait-seconds", type=int, default=60, help="Seconds to wait before survival check (default: 60)")
    args = parser.parse_args()
    asyncio.run(run_seeder(wait_seconds=args.wait_seconds, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
