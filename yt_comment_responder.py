#!/usr/bin/env python3
r"""
=============================================================================
SACRED NUMBER BLUEPRINT · YOUTUBE STUDIO & SHORTS COMMENT AUTO-RESPONDER
yt_comment_responder.py
-----------------------------------------------------------------------------
Automated Playwright/CDP worker for YouTube Studio Comments
(https://studio.youtube.com/channel/UCBIWSA7ZBuBEP_9rj3uSfqA/comments/inbox)
and live YouTube Shorts watch pages (from `uploaded_yt_shorts.json`).
Attaches to authenticated real Google Chrome (`Profile 6` in
`C:\Users\User\.gemini\antigravity\yt_chrome_cdp_userdata`), parses 1 or 2
birth days (1-31) via `parse_birth_days_from_comment()`, computes real
Compatibility % scores via `CommentReplyEngine`, likes comments, posts
personalized replies with the `@sacrednumberblueprint` bio-link CTA, and
records state in `replied_yt_comments.json`.
=============================================================================
"""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

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
UPLOADED_SHORTS_PATH = os.path.join(BASE_DIR, "uploaded_yt_shorts.json")
DEDUP_PATH = os.path.join(BASE_DIR, "replied_yt_comments.json")

YT_CTA_SUFFIX = (
    "Tap @sacrednumberblueprint above -> tap our bio link "
    "(Blueprint.MegaVegaVentures.com) for your custom text script! 👆"
)


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


def is_own_or_seeded_comment(author: str, text: str) -> bool:
    low = text.lower()
    alow = author.lower()
    if (
        "drop your birth day" in low
        or "top pair asked" in low
        or "sacrednumberblueprint" in alow
        or "love & birthday compatibility" in alow
        or "cognitivecurrent" in alow
    ):
        return True
    return False


def build_yt_reply(engine: CommentReplyEngine, text: str, author: str) -> str:
    plan = engine.generate_reply_plan(text, username=author.lstrip("@"))
    bucket = plan.get("bucket", "")
    meta = plan.get("meta", {})
    if bucket == "A_PAIR_COMPAT":
        d1 = meta.get("day1")
        d2 = meta.get("day2")
        score = meta.get("score")
        label = meta.get("label")
        return (
            f"Day {d1} × Day {d2} is a {score}% {label} 🔥 "
            f"Intense chemistry, but one pulls back! {YT_CTA_SUFFIX}"
        )
    if bucket == "A_SINGLE_DAY_COMPAT":
        d1 = meta.get("day1")
        arch = meta.get("archetype")
        soulmate = meta.get("soulmate_days")
        trap = meta.get("karmic_trap_days")
        return (
            f"Day {d1} is {arch}! Soulmate days: {soulmate} ❤️ "
            f"Karmic trap: {trap} 🔥 {YT_CTA_SUFFIX}"
        )
    return plan["reply_text"]


def load_active_short_ids() -> List[str]:
    if not os.path.exists(UPLOADED_SHORTS_PATH):
        return []
    try:
        with open(UPLOADED_SHORTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        vids = []
        for k, v in data.get("videos", {}).items():
            if v.get("status") == "published" and v.get("video_id"):
                vids.append(v["video_id"])
        return vids
    except Exception:
        return []


async def run_yt_responder(live: bool = False, limit: int = 15):
    if not os.path.exists(YT_PROFILE_DIR):
        print(f"[YT Responder] Profile dir {YT_PROFILE_DIR} not initialized yet; skipping.")
        return

    engine = CommentReplyEngine()
    dedup = load_dedup()
    replied = 0
    loaded = 0

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
                        "--remote-debugging-port=9223",
                        f"--user-data-dir={YT_PROFILE_DIR}",
                        "--profile-directory=Profile 6",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--window-size=1366,900",
                        YT_STUDIO_COMMENTS_URL,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                await asyncio.sleep(3.5)
                browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9223")
                ctx = browser.contexts[0] if browser.contexts else await browser.new_context(viewport={"width": 1366, "height": 900})
            except Exception as e:
                print(f"[YT Responder] CDP port 9223 notice ({e}); falling back to persistent context.")

        if ctx is None:
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
            if YT_STUDIO_COMMENTS_URL not in page.url:
                await page.goto(YT_STUDIO_COMMENTS_URL, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(5.0)
        except Exception as e:
            print(f"[YT Responder] Studio navigation notice: {e}")

        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            print("[YT Responder] Not authenticated in YouTube Studio.")
            if browser:
                await browser.close()
            else:
                await ctx.close()
            if chrome_proc:
                chrome_proc.terminate()
            return

        # 1. Check YouTube Studio Comments Inbox (`ytcp-comment-thread`)
        threads = page.locator("ytcp-comment-thread")
        cnt = await threads.count()
        loaded += cnt
        print(f"[YT Responder] Loaded {cnt} comment thread(s) in YouTube Studio Inbox.")

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

            if not text or is_own_or_seeded_comment(author, text):
                continue

            cid = make_cid(author, text)
            if cid in dedup:
                continue

            reply_text = build_yt_reply(engine, text, author)
            days = parse_birth_days_from_comment(text)
            print(f"  [YT Studio Comment] {author}: {text!r} (days={days}) -> {reply_text!r}")

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
                                "source": "studio_inbox",
                                "author": author,
                                "comment": text,
                                "reply": reply_text,
                                "days": days,
                                "replied_at": datetime.now(timezone.utc).isoformat(),
                            }
                            save_dedup(dedup)
                except Exception as e:
                    print(f"  [YT Studio Reply Error] {e}")

        # 2. Check active YouTube Shorts watch pages directly (`ytd-comment-thread-renderer`)
        short_ids = load_active_short_ids()
        for vid in short_ids:
            if replied >= limit:
                break
            wurl = f"https://www.youtube.com/watch?v={vid}"
            try:
                await page.goto(wurl, wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(3.5)
                await page.evaluate("window.scrollBy(0, 650)")
                await asyncio.sleep(2.5)
            except Exception:
                continue

            w_threads = page.locator("ytd-comment-thread-renderer")
            w_cnt = await w_threads.count()
            loaded += w_cnt
            for j in range(w_cnt):
                if replied >= limit:
                    break
                wth = w_threads.nth(j)
                try:
                    a_el = wth.locator("#author-text").first
                    c_el = wth.locator("#content-text").first
                    author = (await a_el.inner_text()).strip() if await a_el.count() > 0 else "viewer"
                    text = (await c_el.inner_text()).strip() if await c_el.count() > 0 else ""
                except Exception:
                    continue

                if not text or is_own_or_seeded_comment(author, text):
                    continue

                cid = make_cid(author, text)
                if cid in dedup:
                    continue

                reply_text = build_yt_reply(engine, text, author)
                days = parse_birth_days_from_comment(text)
                print(f"  [YT Watch {vid}] {author}: {text!r} (days={days}) -> {reply_text!r}")

                if live:
                    try:
                        r_btn = wth.locator('ytd-button-renderer#reply-button-end button, button[aria-label="Reply"]').first
                        if await r_btn.count() > 0:
                            await r_btn.click(force=True)
                            await asyncio.sleep(0.8)
                            r_box = wth.locator("#contenteditable-root, div[contenteditable='true']").first
                            if await r_box.count() > 0:
                                await r_box.click(force=True)
                                await page.keyboard.type(reply_text, delay=8)
                                await asyncio.sleep(0.6)
                                sub_btn = wth.locator('ytd-button-renderer#submit-button button, button[aria-label="Reply"]').last
                                await sub_btn.click(force=True)
                                await asyncio.sleep(2.5)
                                replied += 1
                                dedup[cid] = {
                                    "source": f"watch_{vid}",
                                    "video_id": vid,
                                    "author": author,
                                    "comment": text,
                                    "reply": reply_text,
                                    "days": days,
                                    "replied_at": datetime.now(timezone.utc).isoformat(),
                                }
                                save_dedup(dedup)
                    except Exception as e:
                        print(f"  [YT Watch Reply Error] {vid}: {e}")

        if browser:
            await browser.close()
        else:
            await ctx.close()
        if chrome_proc:
            chrome_proc.terminate()

    print(f"[YT Responder Summary] loaded={loaded} | replied={replied}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()
    asyncio.run(run_yt_responder(live=args.live, limit=args.limit))


if __name__ == "__main__":
    main()
