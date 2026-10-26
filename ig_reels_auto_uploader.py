#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · INSTAGRAM REELS DESKTOP WEB AUTO-UPLOADER
ig_reels_auto_uploader.py
-----------------------------------------------------------------------------
Automated Playwright uploader for @sacrednumberblueprint on Instagram Web
(https://www.instagram.com/) using a persistent browser profile at:
  C:\\Users\\User\\.gemini\\antigravity\\ig_browser_profile

Features:
- Persistent Chromium profile with foreground window bring-to-front + screenshot
  fallback if login / 2FA is needed (waits up to 120s for authentication).
- Native desktop web Reels upload flow:
  1. Clicks 'Create' ('+' / svg[aria-label="New post"]) in the left sidebar
     (and clicks 'Post' if a dropdown submenu appears).
  2. Uploads the vertical 1080x1920 .mp4 from G:\\My Drive\\5_System_Numerology_MVP\\tiktok_queue\\.
  3. In the Crop modal, clicks 'Select crop' and chooses '9:16' (or 'Original')
     so Instagram preserves full vertical 9:16 video, then clicks Next -> Next.
  4. Fills the caption box (div[aria-label="Write a caption..."]) with an
     Instagram-optimized caption + hashtags ending with:
     "Tap the link in our bio @sacrednumberblueprint to run your free 5-System Overlap Calculator ✨ Or drop your birth month and day in the comments below 👇"
  5. Clicks 'Share' and waits for "Your reel has been shared." confirmation.
  6. Seeds the matching engagement question as the first comment on the Reel.
- Tracks all uploaded Reels in uploaded_ig_reels.json so we never double-post.
=============================================================================
"""

import argparse
import asyncio
import glob
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, BrowserContext, Page

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

IG_HOME_URL = "https://www.instagram.com/"
IG_PROFILE_URL = "https://www.instagram.com/sacrednumberblueprint/"
DEFAULT_IG_PROFILE_DIR = os.path.join(
    os.path.expanduser("~"), ".gemini", "antigravity", "ig_browser_profile"
)
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
SCRIPTS_JSON_PATH = os.path.join(BASE_DIR, "tiktok_scripts.json")
UPLOADED_IG_TRACKER_PATH = os.path.join(BASE_DIR, "uploaded_ig_reels.json")
GDRIVE_IG_TRACKER_PATH = os.path.join(GDRIVE_QUEUE_DIR, "uploaded_ig_reels.json")

IG_CTA_FOOTER = (
    "\n\nTap the link in our bio @sacrednumberblueprint to run your free 5-System "
    "Overlap Calculator ✨ Or drop your birth month and day in the comments below 👇"
)


def force_ig_window_to_foreground():
    """Uses Win32 API on Windows to bring the Instagram Chromium window to the very front (topmost briefly)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        HWND_TOPMOST = -1
        HWND_NOTOPMOST = -2
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040

        def enum_cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value.lower()
                    if any(k in title for k in ("instagram", "chromium", "chrome", "about:blank")):
                        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                        user32.ShowWindow(hwnd, 3)  # SW_SHOWMAXIMIZED
                        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                        user32.BringWindowToTop(hwnd)
                        user32.keybd_event(0x12, 0, 0, 0)
                        user32.SetForegroundWindow(hwnd)
                        user32.keybd_event(0x12, 0, 2, 0)
                        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
            return True

        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    except Exception:
        pass


class UploadedIGReelsTracker:
    """Tracks published Instagram Reels in uploaded_ig_reels.json (local + Google Drive)."""

    def __init__(self, filepath: str = UPLOADED_IG_TRACKER_PATH, sync_gdrive: bool = True):
        self.filepath = filepath
        self.sync_gdrive = sync_gdrive
        self.data: Dict[str, Any] = {"uploaded_reels": {}, "history": []}
        self._load_or_init()

    def _load_or_init(self):
        loaded = False
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    loaded = True
            except Exception:
                loaded = False

        if not loaded and self.sync_gdrive and os.path.exists(GDRIVE_IG_TRACKER_PATH):
            try:
                with open(GDRIVE_IG_TRACKER_PATH, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                    loaded = True
            except Exception:
                loaded = False

        if "uploaded_reels" not in self.data or not isinstance(self.data["uploaded_reels"], dict):
            self.data["uploaded_reels"] = {}
        if "history" not in self.data or not isinstance(self.data["history"], list):
            self.data["history"] = []
        self.save()

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Tracker] Warning: failed to save {self.filepath}: {e}", flush=True)

        if self.sync_gdrive and os.path.exists(GDRIVE_QUEUE_DIR):
            try:
                with open(GDRIVE_IG_TRACKER_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    def is_uploaded(self, filename: str) -> bool:
        key = os.path.basename(filename)
        entry = self.data["uploaded_reels"].get(key)
        if not entry:
            return False
        return entry.get("status") in ("shared", "uploaded", "published")

    def mark_uploaded(
        self,
        filename: str,
        caption: str = "",
        first_comment: str = "",
        reel_url: str = "",
    ):
        key = os.path.basename(filename)
        now_iso = datetime.now(timezone.utc).isoformat()
        record = {
            "filename": key,
            "status": "shared",
            "updated_at": now_iso,
            "caption": caption,
            "first_comment": first_comment,
            "reel_url": reel_url,
        }
        self.data["uploaded_reels"][key] = record
        self.data["history"].append(record)
        self.save()


def load_scripts_metadata() -> Dict[str, Dict[str, Any]]:
    mapping: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(SCRIPTS_JSON_PATH):
        return mapping
    try:
        with open(SCRIPTS_JSON_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for s in raw.get("scripts", []):
            fname = s.get("filename")
            if fname:
                mapping[fname] = s
    except Exception as e:
        print(f"[Scripts] Warning: could not parse {SCRIPTS_JSON_PATH}: {e}", flush=True)
    return mapping


def build_ig_caption(meta: Dict[str, Any]) -> str:
    """Builds an Instagram-optimized caption with our @sacrednumberblueprint bio link CTA."""
    base_caption = (meta.get("tiktok_caption") or "").strip()
    if not base_caption:
        hook = (meta.get("hook_name") or "Discover your 5-System Master Overlap Numbers").strip()
        tags = " ".join(meta.get("hashtags") or ["#numerology", "#lifepath", "#spiritualawakening", "#loshugrid", "#chaldean"])
        base_caption = f"{hook} ✨\n\n{tags}"

    # Split hashtags to the very bottom so the CTA sits cleanly above hashtags
    words = base_caption.split()
    body_tokens = [w for w in words if not w.startswith("#")]
    tag_tokens = [w for w in words if w.startswith("#")]
    for extra_tag in ("#instagramreels", "#numerologyreading", "#sacrednumberblueprint"):
        if extra_tag not in [t.lower() for t in tag_tokens]:
            tag_tokens.append(extra_tag)

    body_text = " ".join(body_tokens).strip()
    tags_text = " ".join(tag_tokens).strip()
    return f"{body_text}{IG_CTA_FOOTER}\n\n{tags_text}".strip()


class InstagramReelsUploader:
    def __init__(self, profile_dir: str = DEFAULT_IG_PROFILE_DIR):
        self.profile_dir = profile_dir
        self.tracker = UploadedIGReelsTracker()
        self.scripts_by_filename = load_scripts_metadata()

    def discover_video(self, target_video: str, force: bool = False) -> Optional[Dict[str, Any]]:
        fname = os.path.basename(target_video)
        if self.tracker.is_uploaded(fname) and not force:
            print(f"  [Skip] {fname} is already marked as shared in uploaded_ig_reels.json (use --force to re-post).", flush=True)
            return None

        search_paths = [
            os.path.join(GDRIVE_QUEUE_DIR, fname),
            os.path.join(LOCAL_VIDEOS_DIR, fname),
            target_video,
        ]
        found_path = None
        for p in search_paths:
            if os.path.exists(p) and os.path.isfile(p):
                found_path = os.path.abspath(p)
                break

        if not found_path:
            raise FileNotFoundError(f"Could not find video file '{target_video}' in {GDRIVE_QUEUE_DIR} or {LOCAL_VIDEOS_DIR}")

        meta = self.scripts_by_filename.get(fname, {})
        ig_caption = build_ig_caption(meta)
        first_comment = (meta.get("first_comment") or "What is your birth month and day—and which number keeps repeating in your life? 👇").strip()
        return {
            "filename": fname,
            "filepath": found_path,
            "size_mb": round(os.path.getsize(found_path) / (1024 * 1024), 2),
            "ad_id": meta.get("id", fname),
            "hook_name": meta.get("hook_name", fname),
            "ig_caption": ig_caption,
            "first_comment": first_comment,
        }

    async def is_authenticated(self, page: Page) -> bool:
        """Checks if Instagram Web shows the authenticated left sidebar ('New post' / 'Create' / 'Direct' / 'Profile')."""
        try:
            auth_selectors = [
                'svg[aria-label="New post"]',
                'svg[aria-label="Create"]',
                'a[href*="/direct/inbox/"]',
                'svg[aria-label="Home"]',
                'span:text-is("Create")',
                'a[href="/sacrednumberblueprint/"]',
            ]
            for sel in auth_selectors:
                if await page.locator(sel).count() > 0:
                    return True
        except Exception:
            pass
        return False

    async def dismiss_ig_popups(self, page: Page):
        """Dismisses 'Save your login info?' or 'Turn on Notifications' modals after login."""
        dismiss_buttons = [
            'button:text-is("Not Now")',
            'div[role="button"]:text-is("Not now")',
            'button:text-is("Not now")',
            'button:has-text("Save info")',
        ]
        for sel in dismiss_buttons:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click(force=True)
                    await asyncio.sleep(1.0)
            except Exception:
                pass

    async def ensure_authenticated(self, page: Page, wait_seconds: int = 120) -> bool:
        print(f"Navigating to {IG_HOME_URL}...", flush=True)
        await page.goto(IG_HOME_URL, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.0)
        await self.dismiss_ig_popups(page)

        if await self.is_authenticated(page):
            print("✓ [IG Auth] Already authenticated into Instagram Web!", flush=True)
            await page.screenshot(path="ig_auth_verified.png")
            return True

        # Optional auto-fill if IG_USERNAME & IG_PASSWORD are set in environment
        ig_user = os.environ.get("IG_USERNAME", "").strip()
        ig_pass = os.environ.get("IG_PASSWORD", "").strip()
        if ig_user and ig_pass:
            try:
                user_inp = page.locator('input[name="username"], input[aria-label*="username"], input[type="text"]').first
                pass_inp = page.locator('input[name="password"], input[type="password"]').first
                if await user_inp.count() > 0 and await pass_inp.count() > 0:
                    await user_inp.fill(ig_user)
                    await asyncio.sleep(0.4)
                    await pass_inp.fill(ig_pass)
                    await asyncio.sleep(0.4)
                    submit_btn = page.locator('button[type="submit"], div[role="button"]:has-text("Log in")').first
                    if await submit_btn.count() > 0:
                        await submit_btn.click(force=True)
                        print(f"   [IG Auth] Auto-filled login for {ig_user}; waiting for redirect or 2FA...", flush=True)
            except Exception as e:
                print(f"   [IG Auth] Auto-fill note: {e}", flush=True)

        print("=" * 72, flush=True)
        print("⚠ [IG Auth] Instagram is not logged in yet in ig_browser_profile.", flush=True)
        print(f"Waiting up to {wait_seconds}s for you to sign in to @sacrednumberblueprint in the open Chromium window...", flush=True)
        print("=" * 72, flush=True)

        try:
            await page.bring_to_front()
        except Exception:
            pass
        force_ig_window_to_foreground()
        await page.screenshot(path="ig_login_prompt.png")

        start = time.time()
        last_shot = 0.0
        while time.time() - start < wait_seconds:
            await asyncio.sleep(2.5)
            await self.dismiss_ig_popups(page)
            if await self.is_authenticated(page):
                print("✓ [IG Auth] Login detected! Saving persistent session...", flush=True)
                await asyncio.sleep(2.0)
                await self.dismiss_ig_popups(page)
                await page.screenshot(path="ig_auth_verified.png")
                return True
            if time.time() - last_shot >= 15.0:
                last_shot = time.time()
                try:
                    await page.screenshot(path="ig_login_prompt.png")
                except Exception:
                    pass

        print("✗ [IG Auth] Timed out waiting for Instagram login.", flush=True)
        return False

    async def upload_reel(self, page: Page, item: Dict[str, Any], seed_comment: bool = True) -> bool:
        print("\n" + "=" * 72, flush=True)
        print(f"▶ [IG REELS] Uploading {item['filename']} ({item['size_mb']} MB)...", flush=True)
        print("=" * 72, flush=True)

        await page.goto(IG_HOME_URL, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.0)
        await self.dismiss_ig_popups(page)

        # 1. Click 'Create' ('+' / svg[aria-label="New post"]) in the left navigation bar
        clicked_create = False
        create_selectors = [
            'svg[aria-label="New post"]',
            'svg[aria-label="Create"]',
            'span:text-is("Create")',
            'a:has(svg[aria-label="New post"])',
        ]
        for sel in create_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                try:
                    await loc.click(force=True)
                    clicked_create = True
                    print(f"   [IG] ✓ Clicked Create button ({sel}).", flush=True)
                    await asyncio.sleep(1.8)
                    break
                except Exception:
                    pass

        if not clicked_create:
            raise RuntimeError("Could not find 'Create' / 'New post' button in Instagram sidebar.")

        # If a submenu dropdown appears with 'Post', click 'Post' (unless file input is already present)
        if await page.locator('input[type="file"]').count() == 0:
            post_sub_selectors = [
                'span:text-is("Post")',
                'a:has-text("Post")',
                'div[role="menuitem"]:has-text("Post")',
                'svg[aria-label="Post"]',
            ]
            for sel in post_sub_selectors:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click(force=True)
                    print("   [IG] ✓ Clicked 'Post' in Create dropdown menu.", flush=True)
                    await asyncio.sleep(1.8)
                    break

        # 2. Attach .mp4 via hidden <input type="file">
        file_inputs = page.locator('input[type="file"]')
        await file_inputs.first.wait_for(state="attached", timeout=20000)
        # Prefer the input that accepts video/mp4 if multiple exist
        target_input = file_inputs.first
        for i in range(await file_inputs.count()):
            inp = file_inputs.nth(i)
            accept_attr = (await inp.get_attribute("accept") or "").lower()
            if "video" in accept_attr or "mp4" in accept_attr:
                target_input = inp
                break

        await target_input.set_input_files(item["filepath"])
        print(f"   [IG] ✓ Attached 9:16 video: {item['filepath']}", flush=True)
        await asyncio.sleep(3.5)

        # Dismiss any "Video posts are now shared as reels" -> "OK" modal inside the upload dialog
        ok_btns = [
            'button:text-is("OK")',
            'div[role="button"]:text-is("OK")',
            'button:has-text("OK")',
        ]
        for sel in ok_btns:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(force=True)
                print("   [IG] ✓ Dismissed 'Video posts are now shared as reels' OK notice.", flush=True)
                await asyncio.sleep(1.0)
                break

        # 3. Select Crop -> 9:16 (or Original) so Instagram never crops vertical video into 1:1
        crop_btn_selectors = [
            'svg[aria-label="Select crop"]',
            'button:has(svg[aria-label="Select crop"])',
            'div[role="button"]:has(svg[aria-label="Select crop"])',
        ]
        clicked_crop = False
        for sel in crop_btn_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(force=True)
                clicked_crop = True
                await asyncio.sleep(1.0)
                break

        if clicked_crop:
            aspect_selectors = [
                'span:text-is("9:16")',
                'div[role="button"]:has-text("9:16")',
                'button:has-text("9:16")',
                'span:text-is("Original")',
                'div[role="button"]:has-text("Original")',
            ]
            for sel in aspect_selectors:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click(force=True)
                    print(f"   [IG] ✓ Selected vertical aspect ratio ({sel}).", flush=True)
                    await asyncio.sleep(1.0)
                    break

        await page.screenshot(path=f"ig_step1_crop_{item['ad_id']}.png")

        # Click 'Next' (Crop -> Edit/Trim) and 'Next' (Edit/Trim -> Caption)
        for step_num in (1, 2):
            next_clicked = False
            next_selectors = [
                'div[role="dialog"] div[role="button"]:text-is("Next")',
                'div[role="dialog"] button:text-is("Next")',
                'div[role="button"]:text-is("Next")',
                'button:text-is("Next")',
            ]
            for sel in next_selectors:
                loc = page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click(force=True)
                    next_clicked = True
                    print(f"   [IG] ✓ Clicked Next (Step {step_num}/2).", flush=True)
                    await asyncio.sleep(2.2)
                    break
            if not next_clicked:
                print(f"   [IG] ⚠ Could not find Next button on step {step_num}; checking if already on Caption view.", flush=True)

        # 4. Fill Caption in div[aria-label="Write a caption..."]
        caption_selectors = [
            'div[aria-label="Write a caption..."][contenteditable="true"]',
            'div[aria-label="Write a caption..."]',
            'div[role="dialog"] div[contenteditable="true"][ role="textbox"]',
            'div[role="dialog"] div[contenteditable="true"]',
        ]
        caption_filled = False
        for sel in caption_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(force=True)
                await asyncio.sleep(0.4)
                await page.keyboard.insert_text(item["ig_caption"])
                await asyncio.sleep(0.6)
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.4)
                caption_filled = True
                print("   [IG] ✓ Populated Instagram Reel caption & hashtags.", flush=True)
                break

        if not caption_filled:
            print("   [IG] ⚠ Warning: Could not locate caption input box.", flush=True)

        await page.screenshot(path=f"ig_step2_caption_{item['ad_id']}.png")

        # 5. Click 'Share' button in top-right of modal
        share_selectors = [
            'div[role="dialog"] div[role="button"]:text-is("Share")',
            'div[role="dialog"] button:text-is("Share")',
            'div[role="button"]:text-is("Share")',
            'button:text-is("Share")',
        ]
        shared_clicked = False
        for sel in share_selectors:
            loc = page.locator(sel).last
            if await loc.count() > 0 and await loc.is_visible():
                await loc.click(force=True)
                shared_clicked = True
                print("   [IG] ✓ Clicked 'Share' button! Waiting for 'Your reel has been shared.'...", flush=True)
                break

        if not shared_clicked:
            raise RuntimeError("Could not find 'Share' button in Instagram upload dialog.")

        # Wait up to 90s for "Your reel has been shared." or "Reel shared" confirmation
        confirmed = False
        for wait_i in range(45):
            await asyncio.sleep(2.0)
            body_txt = (await page.inner_text("body")).lower()
            if (
                "your reel has been shared" in body_txt
                or "reel shared" in body_txt
                or "your post has been shared" in body_txt
            ):
                confirmed = True
                print(f"   [IG] ✓ Confirmed: 'Your reel has been shared.' (after {(wait_i + 1) * 2}s)!", flush=True)
                break

        await page.screenshot(path=f"ig_step3_shared_{item['ad_id']}.png")
        if not confirmed:
            print("   [IG] ⚠ Did not see literal 'Your reel has been shared.' text within 90s; verifying on profile...", flush=True)

        # 6. Navigate to profile / reels tab to verify & seed first comment
        reel_url = ""
        if seed_comment and item.get("first_comment"):
            reel_url = await self.seed_first_comment_on_latest_reel(page, item["first_comment"], item["ad_id"])

        self.tracker.mark_uploaded(
            item["filename"],
            caption=item["ig_caption"],
            first_comment=item.get("first_comment", ""),
            reel_url=reel_url,
        )
        print(f"   [Tracker] ✓ Marked {item['filename']} as SHARED in uploaded_ig_reels.json", flush=True)
        return True

    async def seed_first_comment_on_latest_reel(self, page: Page, comment_text: str, ad_id: str) -> str:
        """Opens the newest Reel on @sacrednumberblueprint and posts the engagement question first comment."""
        print(f"   [IG Seed] Navigating to {IG_PROFILE_URL}reels/ to seed first comment...", flush=True)
        try:
            await page.goto(f"{IG_PROFILE_URL}reels/", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(5.0)
            reel_links = page.locator('a[href*="/reel/"], a[href*="/p/"]')
            if await reel_links.count() == 0:
                await page.goto(IG_PROFILE_URL, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4.5)
                reel_links = page.locator('a[href*="/reel/"], a[href*="/p/"]')

            if await reel_links.count() == 0:
                print("   [IG Seed] ⚠ Could not find Reel link on profile yet.", flush=True)
                return ""

            first_href = await reel_links.first.get_attribute("href") or ""
            full_url = f"https://www.instagram.com{first_href}" if first_href.startswith("/") else first_href
            await reel_links.first.click(force=True)
            await asyncio.sleep(4.0)

            comment_box_selectors = [
                'textarea[aria-label*="Add a comment"]',
                'textarea[placeholder*="Add a comment"]',
                'form textarea',
            ]
            for sel in comment_box_selectors:
                box = page.locator(sel).first
                if await box.count() > 0 and await box.is_visible():
                    await box.click(force=True)
                    await asyncio.sleep(0.4)
                    await box.fill(comment_text)
                    await asyncio.sleep(0.6)
                    post_btn = page.locator('div[role="button"]:text-is("Post"), button:text-is("Post"), form button[type="submit"]').first
                    if await post_btn.count() > 0 and await post_btn.is_visible():
                        await post_btn.click(force=True)
                    else:
                        await page.keyboard.press("Enter")
                    await asyncio.sleep(3.5)
                    await page.screenshot(path=f"ig_seeded_comment_{ad_id}.png")
                    print(f"   [IG Seed] ✓ Seeded first comment on {full_url}: \"{comment_text}\"", flush=True)
                    return full_url
        except Exception as e:
            print(f"   [IG Seed] ⚠ Note while seeding first comment: {e}", flush=True)
        return ""

    async def run(
        self,
        videos: List[str],
        auth_only: bool = False,
        dry_run: bool = False,
        force: bool = False,
        headless: bool = False,
        wait_login_seconds: int = 120,
    ) -> int:
        os.makedirs(self.profile_dir, exist_ok=True)
        items_to_upload: List[Dict[str, Any]] = []
        if not auth_only:
            for v in videos:
                disc = self.discover_video(v, force=force)
                if disc:
                    items_to_upload.append(disc)

        if dry_run:
            print("========================================================================", flush=True)
            print("   INSTAGRAM REELS AUTO-UPLOADER (DRY-RUN VERIFICATION)", flush=True)
            print("========================================================================", flush=True)
            for it in items_to_upload:
                print(f"  • Video   : {it['filename']} ({it['size_mb']} MB)", flush=True)
                print(f"  • Path    : {it['filepath']}", flush=True)
                print(f"  • Caption : {it['ig_caption'][:160]}...", flush=True)
                print(f"  • Comment : {it['first_comment']}", flush=True)
            return 0

        async with async_playwright() as p:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=headless,
                viewport={"width": 1366, "height": 920},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                ],
            )
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            try:
                authed = await self.ensure_authenticated(page, wait_seconds=wait_login_seconds)
                if not authed:
                    await ctx.close()
                    return 2

                if auth_only:
                    print("✓ [IG Auth] Persistent session verified and cached.", flush=True)
                    await ctx.close()
                    return 0

                for idx, item in enumerate(items_to_upload):
                    await self.upload_reel(page, item, seed_comment=True)
                    if idx < len(items_to_upload) - 1:
                        print("   [IG] Waiting 8s before uploading next Reel...", flush=True)
                        await asyncio.sleep(8.0)

                # Take final profile Reels grid screenshot
                await page.goto(f"{IG_PROFILE_URL}reels/", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(5.0)
                await page.screenshot(path="ig_profile_reels_verified.png")
                print("✓ Saved final Instagram Reels grid screenshot: ig_profile_reels_verified.png", flush=True)
            finally:
                await ctx.close()
        return 0


def main():
    parser = argparse.ArgumentParser(description="Instagram Reels Desktop Web Auto-Uploader (@sacrednumberblueprint)")
    parser.add_argument(
        "--video",
        action="append",
        default=[],
        help="Video filename(s) to upload (can be passed multiple times or comma-separated)",
    )
    parser.add_argument("--auth-only", action="store_true", help="Only launch & authenticate ig_browser_profile")
    parser.add_argument("--dry-run", action="store_true", help="Verify video paths, captions, and first comments without uploading")
    parser.add_argument("--force", action="store_true", help="Upload even if already present in uploaded_ig_reels.json")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (only after session is cached)")
    parser.add_argument("--wait-login", type=int, default=120, help="Seconds to wait for interactive login if not authenticated")
    args = parser.parse_args()

    video_list: List[str] = []
    for v in args.video:
        for part in v.split(","):
            if part.strip():
                video_list.append(part.strip())

    if not args.auth_only and not video_list:
        video_list = [
            "tiktok_short_02_born_7_16_25.mp4",
            "tiktok_short_01_born_8_17_26.mp4",
        ]

    uploader = InstagramReelsUploader()
    code = asyncio.run(
        uploader.run(
            videos=video_list,
            auth_only=args.auth_only,
            dry_run=args.dry_run,
            force=args.force,
            headless=args.headless,
            wait_login_seconds=args.wait_login,
        )
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
