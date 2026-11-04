#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · YOUTUBE STUDIO COMMENT AUTO-RESPONDER
yt_comment_responder.py
-----------------------------------------------------------------------------
Automated Playwright worker for YouTube Studio Comments
(https://studio.youtube.com/channel/UCBIWSA7ZBuBEP_9rj3uSfqA/comments/inbox).
Polls viewer comments on YouTube Shorts, parses 1 or 2 birth days using
`parse_birth_days_from_comment()`, computes real Compatibility % scores via
`CommentReplyEngine`, likes comments, posts personalized replies, and records
state in `replied_yt_comments.json`.
=============================================================================
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from playwright.async_api import async_playwright

from comment_reply_engine import (
    CommentReplyEngine,
    parse_birth_days_from_comment,
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\yt_chrome_cdp_userdata"
YT_CHANNEL_ID = "UCBIWSA7ZBuBEP_9rj3uSfqA"
YT_STUDIO_COMMENTS_URL = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}/comments/inbox"
DEDUP_PATH = os.path.join(BASE_DIR, "replied_yt_comments.json")


def load_dedup() -> Dict[str, Any]:
    if os.path.exists(DEDUP_PATH):
        try:
            with open(DEDUP_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_dedup(data: Dict[str, Any]):
    with open(DEDUP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def make_cid(author: str, text: str) -> str:
    raw = f"{author.strip().lower()}::{text.strip()}"
    return "yt_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


async def run_yt_responder(live: bool = False, limit: int = 10):
    if not os.path.exists(YT_PROFILE_DIR):
        print(f"[YT Responder] Profile dir {YT_PROFILE_DIR} not initialized yet; skipping.")
        return

    engine = CommentReplyEngine()
    dedup = load_dedup()
    replied = 0
    loaded = 0

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=YT_PROFILE_DIR,
            channel="chrome",
            headless=False,
            viewport={"width": 1366, "height": 900},
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled", "--profile-directory=Profile 6"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        try:
            await page.goto(YT_STUDIO_COMMENTS_URL, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(5.0)
        except Exception as e:
            print(f"[YT Responder] Navigation notice: {e}")
            await ctx.close()
            return

        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            print("[YT Responder] Not authenticated in YouTube Studio.")
            await ctx.close()
            return

        threads = page.locator("ytcp-comment-thread")
        cnt = await threads.count()
        loaded = cnt
        print(f"[YT Responder] Loaded {cnt} comment thread(s) in YouTube Studio.")

        for i in range(cnt):
            if replied >= limit:
                break
            th = threads.nth(i)
            try:
                author_el = th.locator("#author-text, a.author-text, ytcp-comment #author-name").first
                content_el = th.locator("#content-text, ytcp-comment #content").first
                author = (await author_el.inner_text()).strip() if await author_el.count() > 0 else "viewer"
                text = (await content_el.inner_text()).strip() if await content_el.count() > 0 else ""
            except Exception:
                continue

            if not text:
                continue

            low = text.lower()
            if (
                "drop your birth day" in low
                or "top pair asked" in low
                or "sacrednumberblueprint" in author.lower()
                or "love & birthday compatibility" in author.lower()
                or "cognitivecurrent" in author.lower()
            ):
                continue

            cid = make_cid(author, text)
            if cid in dedup:
                continue

            plan = engine.generate_reply_plan(text, username=author.lstrip("@"))
            reply_text = plan["reply_text"]
            days = parse_birth_days_from_comment(text)
            print(f"  [YT Comment] {author}: {text!r} (days={days}) -> {reply_text!r}")

            if live:
                try:
                    reply_btn = th.locator('ytcp-button#reply-button, button:has-text("Reply")').first
                    if await reply_btn.count() > 0 and await reply_btn.is_visible():
                        await reply_btn.click(force=True)
                        await asyncio.sleep(0.8)
                        textarea = th.locator("textarea, #textarea, div[contenteditable='true']").first
                        if await textarea.count() > 0:
                            await textarea.click(force=True)
                            await textarea.fill(reply_text)
                            await asyncio.sleep(0.6)
                            submit_btn = th.locator('ytcp-button#submit-button, button:has-text("Reply")').last
                            await submit_btn.click(force=True)
                            await asyncio.sleep(2.5)
                            replied += 1
                            dedup[cid] = {
                                "author": author,
                                "comment": text,
                                "reply": reply_text,
                                "days": days,
                                "replied_at": datetime.now(timezone.utc).isoformat(),
                            }
                            save_dedup(dedup)
                except Exception as e:
                    print(f"  [YT Reply Error] {e}")

        await ctx.close()

    print(f"[YT Responder Summary] loaded={loaded} | replied={replied}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    asyncio.run(run_yt_responder(live=args.live, limit=args.limit))


if __name__ == "__main__":
    main()
