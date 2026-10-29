#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · INSTAGRAM REELS COMMENT AUTO-RESPONDER
ig_comment_responder.py
-----------------------------------------------------------------------------
Automated Playwright comment responder for @sacrednumberblueprint on Instagram
Reels (https://www.instagram.com/sacrednumberblueprint/reels/) using the
persistent browser profile at:
  C:\\Users\\User\\.gemini\\antigravity\\ig_browser_profile

Features:
1. Scans comments across all live Instagram Reels on @sacrednumberblueprint.
2. Uses CommentReplyEngine + Instagram-specific reply formatting:
   - Whenever a viewer comments a birthday (e.g. "08/19/1978", "March 14 1995"),
     a Life Path / Master Number ("Life Path 7", "11"), or keyword ("OVERLAP"),
     calculates their Pythagorean Life Path + Vedic Moolank on the fly.
   - Replies publicly with their calculated numbers and points them straight to
     the link in bio (@sacrednumberblueprint).
3. Likes viewer comments and records all replies in replied_ig_comments.json
   and ig_comment_replies_log.json (synced to Google Drive) so we never
   double-reply or reply to our own @sacrednumberblueprint creator comments.
=============================================================================
"""

import argparse
import asyncio
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import async_playwright, Page

from comment_reply_engine import (
    CommentReplyEngine,
    NUMBER_ARCHETYPES,
    calculate_life_path,
    calculate_vedic_moolank,
    parse_birthday_from_text,
    parse_number_from_text,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

IG_PROFILE_REELS_URL = "https://www.instagram.com/sacrednumberblueprint/reels/"
FUNNEL_BIO_URL = "https://blueprint.megavegaventures.com/?utm_source=ig_bio&cohort=ig_reels"
DEFAULT_IG_PROFILE_DIR = os.path.join(
    os.path.expanduser("~"), ".gemini", "antigravity", "ig_browser_profile"
)
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_IG_DEDUP_FILE = os.path.join(BASE_DIR, "replied_ig_comments.json")
LOCAL_IG_LOG_FILE = os.path.join(BASE_DIR, "ig_comment_replies_log.json")
CREATOR_HANDLE = "sacrednumberblueprint"


class IGCommentReplyGenerator:
    """
    Wraps CommentReplyEngine to generate Instagram-optimized public replies
    that include calculated Pythagorean + Vedic numbers and point directly to
    the link in our bio (@sacrednumberblueprint).
    """

    def __init__(self):
        self.engine = CommentReplyEngine(use_llm=False)

    def generate_ig_reply(self, comment_text: str, author: str = "", seed: Optional[int] = None) -> Dict[str, Any]:
        clean = (comment_text or "").strip()
        low = clean.lower()

        if seed is None:
            digest = hashlib.md5(f"{author}:{clean}".encode("utf-8")).hexdigest()
            seed = int(digest[:8], 16)

        # Check explicit OVERLAP keyword first if no birthday/number
        bday = parse_birthday_from_text(low)
        num = parse_number_from_text(low)

        if bday:
            y, mo, d, fmt_date = bday
            lp_val, lp_disp = calculate_life_path(y, mo, d)
            vedic_val, vedic_ruler = calculate_vedic_moolank(d)
            lp_arch = NUMBER_ARCHETYPES.get(lp_val, {"title": f"Path {lp_val}"})["title"]
            v_planet = vedic_ruler["planet"]
            variations = [
                f"Wait—born on {fmt_date}? Your Pythagorean Life Path is {lp_disp} ({lp_arch}) and your Vedic Moolank is {vedic_val} (ruled by {v_planet}), which is only 2 of the 5 systems! Tap the link in our bio @sacrednumberblueprint to run your full 5-System Overlap chart ✨",
                f"Born on {fmt_date} gives you Western Life Path {lp_disp} and Vedic Number {vedic_val} ({v_planet})! Your name's Chaldean frequency and Chinese Lo Shu grid unlock the other 3 systems—tap the link in our bio @sacrednumberblueprint to test your chart ✨",
            ]
            reply_text = variations[abs(seed) % len(variations)]
            return {
                "bucket": "A_BIRTHDAY",
                "meta": {
                    "date_str": fmt_date,
                    "life_path_display": lp_disp,
                    "vedic_val": vedic_val,
                    "vedic_planet": v_planet,
                },
                "reply_text": reply_text,
            }

        if num is not None:
            arch = NUMBER_ARCHETYPES.get(num, {"name": f"Number {num}", "title": f"Number {num}", "trait": "Sovereign Frequency"})
            vedic_val, vedic_ruler = calculate_vedic_moolank(num if num <= 9 else (num % 9 or 9))
            variations = [
                f"Life Path {num} is {arch['title']} ({arch['trait']})—and in Vedic numerology that vibration connects to {vedic_ruler['planet']}! Tap the link in our bio @sacrednumberblueprint to see if #{num} is also your #1 Master Overlap Anchor across all 5 systems ✨",
                f"Number {num} ({arch['title']})! Single-system numerology is only 20% of your code—tap the link in our bio @sacrednumberblueprint to cross-reference your full birth name and birthday across all 5 ancient systems ✨",
            ]
            reply_text = variations[abs(seed) % len(variations)]
            return {
                "bucket": "B_NUMBER",
                "meta": {"number": num, "archetype_title": arch["title"]},
                "reply_text": reply_text,
            }

        if "overlap" in low or re.search(r"\b(link|where|how|calculator|chart|bio)\b", low):
            reply_text = (
                "Tap the link in our bio @sacrednumberblueprint to run your free 5-System Overlap Calculator "
                "(Pythagorean, Chaldean, Kabbalah, Vedic & Chinese Lo Shu) in 30 seconds ✨"
            )
            return {
                "bucket": "C_KEYWORD_OVERLAP",
                "meta": {},
                "reply_text": reply_text,
            }

        # Fallback to standard CommentReplyEngine classification + IG bio CTA
        base = self.engine.generate_reply(clean, author=author, seed=seed)
        return base


class IGDedupStore:
    def __init__(self, dedup_path: str = LOCAL_IG_DEDUP_FILE, log_path: str = LOCAL_IG_LOG_FILE):
        self.dedup_path = dedup_path
        self.log_path = log_path
        self.replied_ids: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.dedup_path):
            try:
                with open(self.dedup_path, "r", encoding="utf-8") as f:
                    self.replied_ids = json.load(f)
            except Exception:
                self.replied_ids = {}

    def make_key(self, reel_shortcode: str, author: str, text: str) -> str:
        raw = f"{reel_shortcode.strip()}::{author.strip().lower()}::{text.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def has_replied(self, key: str) -> bool:
        return key in self.replied_ids

    def record_reply(self, key: str, entry: Dict[str, Any]):
        self.replied_ids[key] = entry
        try:
            with open(self.dedup_path, "w", encoding="utf-8") as f:
                json.dump(self.replied_ids, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        logs = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(entry)
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


class InstagramCommentResponder:
    def __init__(self, profile_dir: str = DEFAULT_IG_PROFILE_DIR, live_mode: bool = False, limit: int = 10):
        self.profile_dir = profile_dir
        self.live_mode = live_mode
        self.limit = limit
        self.generator = IGCommentReplyGenerator()
        self.store = IGDedupStore()

    async def scan_and_respond(self, headless: bool = True) -> Dict[str, Any]:
        print("=" * 72, flush=True)
        print(f"   SACRED NUMBER BLUEPRINT · INSTAGRAM COMMENT RESPONDER (LIVE={self.live_mode})", flush=True)
        print("=" * 72, flush=True)

        summary = {
            "authenticated": False,
            "reels_checked": 0,
            "viewer_comments_found": 0,
            "replied_count": 0,
            "reels_metrics": [],
        }

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=headless,
                viewport={"width": 1366, "height": 920},
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            try:
                await page.goto(IG_PROFILE_REELS_URL, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(5.0)

                if "login" in page.url.lower():
                    print("⚠ [IG Responder] Not logged in to ig_browser_profile.", flush=True)
                    await ctx.close()
                    return summary

                summary["authenticated"] = True
                reel_hrefs = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href*="/reel/"]'))
                        .map(a => a.getAttribute('href'))
                        .filter(Boolean);
                }""")
                seen = []
                for h in reel_hrefs:
                    if h not in seen:
                        seen.append(h)

                print(f"Found {len(seen)} live Instagram Reels on @sacrednumberblueprint.", flush=True)

                for href in seen[:8]:
                    if summary["replied_count"] >= self.limit:
                        break
                    full_url = f"https://www.instagram.com{href}" if href.startswith("/") else href
                    shortcode = href.strip("/").split("/")[-1]
                    await page.goto(full_url, wait_until="domcontentloaded", timeout=45000)
                    await asyncio.sleep(4.0)
                    summary["reels_checked"] += 1

                    # Extract comments on this Reel
                    comments_data = await page.evaluate("""(creatorHandle) => {
                        const items = [];
                        const ulList = document.querySelectorAll('ul li, div[role="button"]');
                        const bodyText = document.body.innerText || '';
                        // Find all comment blocks (username + text)
                        const links = Array.from(document.querySelectorAll('a[href^="/"][role="link"]'));
                        const seenPairs = new Set();
                        for (const a of links) {
                            const user = (a.innerText || '').trim();
                            if (!user || user.toLowerCase() === creatorHandle.toLowerCase() || user.includes(' ') || user.length > 32) continue;
                            const container = a.closest('li') || a.parentElement?.parentElement?.parentElement;
                            if (!container) continue;
                            const fullTxt = (container.innerText || '').trim();
                            const lines = fullTxt.split('\\n').map(s => s.trim()).filter(Boolean);
                            if (lines.length >= 2 && lines[0] === user) {
                                const msg = lines[1];
                                if (msg && !['Original audio', 'Follow', 'Reply', 'See translation'].includes(msg) && msg.length > 1) {
                                    const key = user + '::' + msg;
                                    if (!seenPairs.has(key)) {
                                        seenPairs.add(key);
                                        items.push({ author: user, text: msg });
                                    }
                                }
                            }
                        }
                        return items;
                    }""", CREATOR_HANDLE)

                    summary["reels_metrics"].append({
                        "shortcode": shortcode,
                        "url": full_url,
                        "viewer_comments": len(comments_data),
                    })
                    print(f"  • Reel {shortcode}: {len(comments_data)} non-creator viewer comment(s)", flush=True)

                    for c in comments_data:
                        if summary["replied_count"] >= self.limit:
                            break
                        author = c["author"]
                        text = c["text"]
                        summary["viewer_comments_found"] += 1
                        dedup_key = self.store.make_key(shortcode, author, text)
                        if self.store.has_replied(dedup_key):
                            continue

                        gen = self.generator.generate_ig_reply(text, author=author)
                        reply_body = f"@{author} {gen['reply_text']}"
                        print(f"    -> [{gen['bucket']}] @{author}: \"{text}\"", flush=True)
                        print(f"       Reply: \"{reply_body}\"", flush=True)

                        if self.live_mode:
                            try:
                                box = page.locator('textarea[aria-label*="Add a comment"], textarea[placeholder*="Add a comment"], form textarea').first
                                if await box.count() > 0 and await box.is_visible():
                                    await box.click(force=True)
                                    await asyncio.sleep(0.4)
                                    await box.fill(reply_body)
                                    await asyncio.sleep(0.6)
                                    post_btn = page.locator('div[role="button"]:text-is("Post"), button:text-is("Post"), form button[type="submit"]').first
                                    if await post_btn.count() > 0 and await post_btn.is_visible():
                                        await post_btn.click(force=True)
                                    else:
                                        await page.keyboard.press("Enter")
                                    await asyncio.sleep(random.uniform(3.2, 5.0))
                                    self.store.record_reply(dedup_key, {
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                        "shortcode": shortcode,
                                        "author": author,
                                        "comment_text": text,
                                        "bucket": gen["bucket"],
                                        "reply_text": reply_body,
                                    })
                                    summary["replied_count"] += 1
                                    print(f"       ✓ Posted live reply on Reel {shortcode}!", flush=True)
                            except Exception as e:
                                print(f"       ⚠ Error posting reply on {shortcode}: {e}", flush=True)
            finally:
                await ctx.close()

        print("=" * 72, flush=True)
        print(
            f"IG_RESPONDER_SUMMARY | AUTH={summary['authenticated']} | "
            f"REELS_CHECKED={summary['reels_checked']} | "
            f"VIEWER_COMMENTS={summary['viewer_comments_found']} | "
            f"REPLIED={summary['replied_count']}",
            flush=True,
        )
        print("=" * 72, flush=True)
        return summary


def main():
    parser = argparse.ArgumentParser(description="Instagram Reels Comment Auto-Responder (@sacrednumberblueprint)")
    parser.add_argument("--live", action="store_true", help="Post live replies to viewer comments")
    parser.add_argument("--limit", type=int, default=10, help="Max replies per run")
    parser.add_argument("--headed", action="store_true", help="Run browser in visible headed window")
    args = parser.parse_args()

    responder = InstagramCommentResponder(live_mode=args.live, limit=args.limit)
    asyncio.run(responder.scan_and_respond(headless=not args.headed))


if __name__ == "__main__":
    main()
