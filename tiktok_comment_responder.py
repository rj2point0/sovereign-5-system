"""
=============================================================================
SACRED NUMBER BLUEPRINT · TIKTOK STUDIO COMMENT AUTO-RESPONDER
tiktok_comment_responder.py
Automated Playwright worker for https://www.tiktok.com/tiktokstudio/comment
Polls comments, calculates real Pythagorean/Vedic numerology on the fly,
likes comments, posts personalized replies with randomized human delays,
and logs all actions to Google Drive with strict deduplication.
=============================================================================
"""

import argparse
import asyncio
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, BrowserContext, Page

from comment_reply_engine import CommentReplyEngine

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TIKTOK_STUDIO_URL = "https://www.tiktok.com/tiktokstudio/comment"
TIKTOK_QR_LOGIN_URL = "https://www.tiktok.com/login/qrcode"
DEFAULT_PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "tiktok_browser_profile")
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
LOCAL_LOG_FILE = "comment_replies_log.json"
LOCAL_DEDUP_FILE = "replied_comments.json"
TASK_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comment_task.log")


def force_browser_window_to_foreground():
    """Uses Win32 API on Windows to force the Chromium/TikTok window to the very front and maximized."""
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
                    if any(k in title for k in ("tiktok", "chromium", "chrome", "about:blank")):
                        # SW_RESTORE = 9, SW_SHOWMAXIMIZED = 3
                        user32.ShowWindow(hwnd, 3)
                        user32.BringWindowToTop(hwnd)
                        # Simulate Alt key state trick so Windows allows SetForegroundWindow from background console
                        user32.keybd_event(0x12, 0, 0, 0)
                        user32.SetForegroundWindow(hwnd)
                        user32.keybd_event(0x12, 0, 2, 0)
            return True

        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception:
        pass


def log_status_summary(login_status: str, loaded_comments_count: int, replied_count: int):
    """Prints and records LOGIN_STATUS, LOADED_COMMENTS_COUNT, and REPLIED_COUNT to stdout and comment_task.log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_line = (
        f"[{ts}] STATUS_SUMMARY | LOGIN_STATUS={login_status} | "
        f"LOADED_COMMENTS_COUNT={loaded_comments_count} | REPLIED_COUNT={replied_count}"
    )
    print("\n" + "=" * 68, flush=True)
    print(f"LOGIN_STATUS:          {login_status}", flush=True)
    print(f"LOADED_COMMENTS_COUNT: {loaded_comments_count}", flush=True)
    print(f"REPLIED_COUNT:         {replied_count}", flush=True)
    print(summary_line, flush=True)
    print("=" * 68, flush=True)

    try:
        with open(TASK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(summary_line + "\n")
    except Exception:
        pass


# -----------------------------------------------------------------------------
# DEDUPLICATION & AUDIT LOG STORE
# -----------------------------------------------------------------------------
class DeduplicationStore:
    def __init__(self, filepath: str = LOCAL_DEDUP_FILE, sync_gdrive: bool = True):
        self.filepath = filepath
        self.sync_gdrive = sync_gdrive and os.path.exists(r"G:\My Drive")
        self.gdrive_filepath = os.path.join(GDRIVE_QUEUE_DIR, "replied_comments.json") if self.sync_gdrive else None
        self.data: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        elif self.gdrive_filepath and os.path.exists(self.gdrive_filepath):
            try:
                with open(self.gdrive_filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        if self.sync_gdrive and os.path.exists(GDRIVE_QUEUE_DIR):
            try:
                with open(self.gdrive_filepath, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"   [Notice] Could not sync dedup to G Drive: {e}", flush=True)

    def has(self, comment_id: str) -> bool:
        return comment_id in self.data

    def record(self, comment_id: str, author: str, comment_text: str, bucket: str, reply_text: str, is_simulated: bool = False):
        self.data[comment_id] = {
            "comment_id": comment_id,
            "author": author,
            "comment": comment_text,
            "bucket": bucket,
            "reply": reply_text,
            "is_simulated": is_simulated,
            "replied_at": datetime.now(timezone.utc).isoformat()
        }
        self.save()


def log_reply_to_audit(entry: Dict[str, Any]):
    """Appends successful or simulated replies to comment_replies_log.json locally and on G: Drive."""
    logs = []
    if os.path.exists(LOCAL_LOG_FILE):
        try:
            with open(LOCAL_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(entry)
    with open(LOCAL_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    if os.path.exists(GDRIVE_QUEUE_DIR):
        g_log = os.path.join(GDRIVE_QUEUE_DIR, "comment_replies_log.json")
        try:
            with open(g_log, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# -----------------------------------------------------------------------------
# TIKTOK COMMENT RESPONDER AGENT
# -----------------------------------------------------------------------------
class TikTokCommentResponder:
    def __init__(
        self,
        engine: CommentReplyEngine,
        dedup_store: DeduplicationStore,
        dry_run: bool = True,
        max_replies: int = 15,
        like_comment: bool = True,
        profile_dir: str = DEFAULT_PROFILE_DIR,
        cdp_port: Optional[int] = None
    ):
        self.engine = engine
        self.dedup = dedup_store
        self.dry_run = dry_run
        self.max_replies = max_replies
        self.like_comment = like_comment
        self.profile_dir = profile_dir
        self.cdp_port = cdp_port

    def generate_comment_id(self, author: str, text: str, timestamp_str: str = "") -> str:
        """Creates a stable unique hash identifier for a comment."""
        raw = f"{author.strip()}::{text.strip()}::{timestamp_str.strip()}"
        return "tiktok_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    async def human_type(self, page: Page, selector: str, text: str):
        """Types text character by character with realistic human keystroke intervals."""
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char)
            await asyncio.sleep(random.uniform(0.02, 0.055))

    async def run_simulation(self, custom_comments: Optional[List[Dict[str, str]]] = None):
        """Runs dry-run simulation against sample comments and prints formatted output."""
        print("=" * 68)
        print("   TIKTOK COMMENT AUTO-RESPONDER · DRY-RUN SIMULATION MODE")
        print("=" * 68)

        samples = custom_comments or [
            {"author": "@mystic_soul77", "text": "08/19/1978"},
            {"author": "@sarah_wellness", "text": "March 14 1995! What is my code?"},
            {"author": "@alex_capital", "text": "I'm a Life Path 8"},
            {"author": "@visionary_eth", "text": "Master number 11 here 🔥"},
            {"author": "@stuck_in_loop", "text": "I work 80 hrs a week and feel so burned out and exhausted"},
            {"author": "@curious_cat", "text": "Where is the link to calculate mine?"},
            {"author": "@divine_star", "text": "Claiming this energy with full heart ✨🙏"},
            {"author": "@bday_gemini", "text": "11-22-1988"}
        ]

        print(f"Evaluating {len(samples)} incoming TikTok comments...\n")
        replies_created = 0

        for i, item in enumerate(samples, 1):
            if replies_created >= self.max_replies:
                print(f"Reached max limit of {self.max_replies} replies.")
                break

            author = item.get("author", f"@user_{i}")
            text = item.get("text", "")
            cid = self.generate_comment_id(author, text)

            if self.dedup.has(cid):
                print(f"[{i}] SKIPPED: Comment {cid} from {author} already replied to.")
                continue

            # Generate reply
            res = self.engine.generate_reply(text, author=author, seed=i)
            reply = res["reply"]
            bucket = res["bucket"]

            print(f"[{i}] User:    {author}")
            print(f"    Comment: \"{text}\"")
            print(f"    Bucket:  {bucket}")
            if "life_path_display" in res.get("meta", {}):
                m = res["meta"]
                print(f"    Math:    Date: {m.get('date_str')} | Life Path: {m.get('life_path_display')} | Vedic Moolank: {m.get('vedic_val')}")
            print(f"    Reply:   \"{reply}\"\n")

            # Record in dedup and audit log
            self.dedup.record(cid, author, text, bucket, reply, is_simulated=True)
            log_reply_to_audit({
                "comment_id": cid,
                "author": author,
                "comment": text,
                "bucket": bucket,
                "reply": reply,
                "simulated": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            replies_created += 1

        print("=" * 68)
        print(f"✓ Simulation complete: {replies_created} replies processed and logged.")
        print(f"  Dedup file: {self.dedup.filepath}")
        if self.dedup.sync_gdrive:
            print(f"  G Drive Sync: {self.dedup.gdrive_filepath}")
        print("=" * 68)

    async def run_live(self):
        """
        Connects to TikTok Studio Comment dashboard via CDP or persistent browser profile,
        scrapes unanswered comments, and posts real replies with randomized delays.
        """
        print("=" * 68)
        print(f"   STARTING TIKTOK COMMENT AUTO-RESPONDER (LIVE MODE: {not self.dry_run})")
        print("=" * 68)

        os.makedirs(self.profile_dir, exist_ok=True)

        async with async_playwright() as p:
            browser_context: Optional[BrowserContext] = None
            browser = None

            # Strategy 1: Connect via CDP if specified
            if self.cdp_port:
                cdp_url = f"http://localhost:{self.cdp_port}"
                print(f"Connecting to existing browser via CDP: {cdp_url}...", flush=True)
                try:
                    browser = await p.chromium.connect_over_cdp(cdp_url)
                    browser_context = browser.contexts[0]
                except Exception as e:
                    print(f"Error connecting to CDP port {self.cdp_port}: {e}. Falling back to persistent profile.")

            # Strategy 2: Launch persistent browser context
            if not browser_context:
                print(f"Launching persistent browser context at: {self.profile_dir}...", flush=True)
                browser_context = await p.chromium.launch_persistent_context(
                    user_data_dir=self.profile_dir,
                    headless=False,
                    no_viewport=True,
                    args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
                )

            page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
            await page.bring_to_front()
            force_browser_window_to_foreground()

            print(f"Navigating to TikTok Studio Comments: {TIKTOK_STUDIO_URL}...", flush=True)
            await page.goto(TIKTOK_STUDIO_URL, wait_until="domcontentloaded")
            await asyncio.sleep(4.0)
            await page.bring_to_front()
            force_browser_window_to_foreground()

            # Check if user needs to log in
            current_url = page.url
            if "login" in current_url.lower() or "passport" in current_url.lower():
                print("\n" + "!" * 68, flush=True)
                print("ACTION REQUIRED: You are not currently logged into TikTok Studio!", flush=True)
                print(f"Navigating directly to QR Code Login: {TIKTOK_QR_LOGIN_URL}", flush=True)
                print("Please scan the QR code in the maximized foreground browser window.", flush=True)
                print("Your session will be saved in the persistent profile for future automated runs.", flush=True)
                print("!" * 68 + "\n", flush=True)

                # In dry-run mode when not logged in, gracefully fallback to simulation
                if self.dry_run:
                    print("Falling back to local dry-run simulation mode...", flush=True)
                    log_status_summary("NOT_LOGGED_IN_DRY_RUN", 0, 0)
                    await self.run_simulation()
                    return

                await page.goto(TIKTOK_QR_LOGIN_URL, wait_until="domcontentloaded")
                await asyncio.sleep(2.0)
                await page.bring_to_front()
                force_browser_window_to_foreground()

                # In live mode, wait up to 180s for user to complete login
                total_wait_s = 180
                poll_interval_s = 5
                max_steps = total_wait_s // poll_interval_s
                print(f"Waiting up to {total_wait_s}s for QR code scan...", flush=True)
                for wait_step in range(1, max_steps + 1):
                    await asyncio.sleep(poll_interval_s)
                    elapsed = wait_step * poll_interval_s
                    current = page.url.lower()
                    if "login" not in current and "passport" not in current:
                        print(f"✓ Login detected ({elapsed}s)! Navigating to TikTok Studio Comments...", flush=True)
                        if "tiktokstudio/comment" not in current:
                            await page.goto(TIKTOK_STUDIO_URL, wait_until="domcontentloaded")
                            await asyncio.sleep(4.0)
                        break
                    if elapsed % 15 == 0:
                        remaining = total_wait_s - elapsed
                        print(f"  ...waiting for QR login: {elapsed}s elapsed, {remaining}s remaining (Current URL: {page.url})", flush=True)
                else:
                    print("Login wait timed out after 180s. Persistent profile is saved; re-run when ready. Exiting safely.", flush=True)
                    log_status_summary("LOGIN_TIMEOUT", 0, 0)
                    return

            # Locate comments on TikTok Studio dashboard
            print("Scanning TikTok Studio Comment feed...", flush=True)
            await page.wait_for_timeout(3000)

            # Extract comment elements via flexible selector query
            comment_elements = await page.query_selector_all(
                '[data-e2e="comment-item"], .comment-item, [class*="CommentItem"], [class*="comment-card"], [class*="comment-item"]'
            )
            loaded_comments_count = len(comment_elements)
            print(f"Found {loaded_comments_count} visible comment items in dashboard.", flush=True)

            if not comment_elements:
                print("No comment items found. The feed might be empty or selectors need adjustment.", flush=True)
                log_status_summary("AUTHENTICATED", 0, 0)
                if self.dry_run:
                    print("Executing simulation fallback to demonstrate engine replies...", flush=True)
                    await self.run_simulation()
                return

            replied_count = 0
            for idx, c_el in enumerate(comment_elements, 1):
                if replied_count >= self.max_replies:
                    print(f"Reached safety limit of {self.max_replies} replies for this session.")
                    break

                # Extract text & author
                text_el = await c_el.query_selector('[data-e2e="comment-content"], [class*="comment-text"], [class*="content"]')
                author_el = await c_el.query_selector('[data-e2e="comment-username"], [class*="comment-author"], [class*="username"], a[href*="/@"]')

                c_text = (await text_el.inner_text()).strip() if text_el else ""
                c_author = (await author_el.inner_text()).strip() if author_el else f"@user_{idx}"

                if not c_text:
                    continue

                cid = self.generate_comment_id(c_author, c_text)
                if self.dedup.has(cid):
                    continue

                res = self.engine.generate_reply(c_text, author=c_author, seed=idx)
                reply = res["reply"]
                bucket = res["bucket"]

                print(f"\n▶ Comment [{replied_count + 1}/{self.max_replies}] from {c_author}: \"{c_text}\"")
                print(f"  Classified: {bucket}")
                print(f"  Generated Reply: \"{reply}\"")

                if self.dry_run:
                    print("  [DRY-RUN] Simulating reply action (not posted to live feed).")
                    self.dedup.record(cid, c_author, c_text, bucket, reply, is_simulated=True)
                    log_reply_to_audit({
                        "comment_id": cid,
                        "author": c_author,
                        "comment": c_text,
                        "bucket": bucket,
                        "reply": reply,
                        "simulated": True,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    replied_count += 1
                    continue

                # LIVE POSTING FLOW:
                # 1. Random human-like pre-delay (8 to 22 seconds)
                delay_sec = random.uniform(8.0, 22.0)
                print(f"  [LIVE] Waiting {delay_sec:.1f}s human jitter delay before posting...", flush=True)
                await asyncio.sleep(delay_sec)

                # 2. Like the comment if requested
                if self.like_comment:
                    like_btn = await c_el.query_selector('[data-e2e="comment-like-icon"], [class*="like-icon"], button[class*="like"]')
                    if like_btn:
                        try:
                            await like_btn.click()
                            await asyncio.sleep(random.uniform(0.5, 1.2))
                            print("  [LIVE] Liked comment ❤️")
                        except Exception:
                            pass

                # 3. Click Reply button
                reply_btn = await c_el.query_selector('button[data-e2e="comment-reply-btn"], button:has-text("Reply"), [class*="reply-btn"]')
                if reply_btn:
                    await reply_btn.click()
                    await asyncio.sleep(random.uniform(0.8, 1.5))

                    # 4. Type reply
                    input_box = await page.query_selector('textarea[placeholder*="reply" i], div[contenteditable="true"], [data-e2e="comment-reply-input"]')
                    if input_box:
                        await input_box.fill("")
                        for ch in reply:
                            await page.keyboard.type(ch)
                            await asyncio.sleep(random.uniform(0.02, 0.05))
                        await asyncio.sleep(random.uniform(0.8, 1.5))

                        # 5. Submit reply
                        submit_btn = await page.query_selector('button[data-e2e="comment-reply-submit"], button:has-text("Post"), button:has-text("Send")')
                        if submit_btn:
                            await submit_btn.click()
                            print(f"  ✓ Successfully posted reply to {c_author}!")

                            # 6. Record deduplication and audit
                            self.dedup.record(cid, c_author, c_text, bucket, reply, is_simulated=False)
                            log_reply_to_audit({
                                "comment_id": cid,
                                "author": c_author,
                                "comment": c_text,
                                "bucket": bucket,
                                "reply": reply,
                                "simulated": False,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            })
                            replied_count += 1
                            await asyncio.sleep(2.0)

            log_status_summary("AUTHENTICATED", loaded_comments_count, replied_count)
            print("\n" + "=" * 68)
            print(f"Finished auto-responder session. Processed: {replied_count} comments.")
            print("=" * 68)


# -----------------------------------------------------------------------------
# CLI INTERFACE
# -----------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Sacred Number Blueprint TikTok Comment Auto-Responder")
    parser.add_argument("--live", action="store_true", help="Enable live posting to TikTok Studio (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate actions without posting (default: True)")
    parser.add_argument("--limit", type=int, default=15, help="Maximum comments to reply to per session (default: 15)")
    parser.add_argument("--no-like", action="store_true", help="Disable auto-liking comments before replying")
    parser.add_argument("--profile-dir", type=str, default=DEFAULT_PROFILE_DIR, help="Persistent browser profile directory")
    parser.add_argument("--port", type=int, default=None, help="Remote debugging port for CDP connection (e.g. 9222)")
    parser.add_argument("--use-llm", action="store_true", help="Enable local Ollama / Qwen model reply polishing")
    parser.add_argument("--test-comment", type=str, default=None, help="Test reply to a single custom comment string")
    return parser.parse_args()


async def main():
    args = parse_args()
    dry_run = not args.live

    engine = CommentReplyEngine(use_llm=args.use_llm)
    dedup = DeduplicationStore()

    responder = TikTokCommentResponder(
        engine=engine,
        dedup_store=dedup,
        dry_run=dry_run,
        max_replies=args.limit,
        like_comment=not args.no_like,
        profile_dir=args.profile_dir,
        cdp_port=args.port
    )

    if args.test_comment:
        print("=" * 68)
        print("   TESTING SINGLE COMMENT")
        print("=" * 68)
        res = engine.generate_reply(args.test_comment, author="@test_user")
        print(f"Comment: \"{args.test_comment}\"")
        print(f"Bucket:  {res['bucket']}")
        print(f"Reply:   \"{res['reply']}\"")
        print("=" * 68)
        return

    # If dry-run without browser connection, run simulation suite
    if dry_run and not args.port:
        await responder.run_simulation()
    else:
        await responder.run_live()


if __name__ == "__main__":
    asyncio.run(main())
