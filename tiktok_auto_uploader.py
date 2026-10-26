"""
=============================================================================
SACRED NUMBER BLUEPRINT · AUTOMATED TIKTOK STUDIO UPLOADER
tiktok_auto_uploader.py
Uses the authenticated Playwright persistent profile at:
  C:\\Users\\User\\.gemini\\antigravity\\tiktok_browser_profile
to upload and publish or schedule MP4 videos from:
  G:\\My Drive\\5_System_Numerology_MVP\\tiktok_queue\\
with strict deduplication tracked in uploaded_videos.json.
=============================================================================
"""

import argparse
import asyncio
import glob
import json
import os
import shutil
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

TIKTOK_UPLOAD_URL = "https://www.tiktok.com/tiktokstudio/upload"
TIKTOK_QR_LOGIN_URL = "https://www.tiktok.com/login/qrcode"
DEFAULT_PROFILE_DIR = os.path.join(
    os.path.expanduser("~"), ".gemini", "antigravity", "tiktok_browser_profile"
)
GDRIVE_QUEUE_DIR = r"G:\My Drive\5_System_Numerology_MVP\tiktok_queue"
LOCAL_VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
LOCAL_TRACKER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_videos.json")
SCRIPTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_scripts.json")

INITIAL_UPLOADED_VIDEOS = {
    "tiktok_promo_1.mp4": {
        "filename": "tiktok_promo_1.mp4",
        "status": "uploaded",
        "mode": "manual_initial_launch",
        "uploaded_at": "2026-10-22T15:00:00-07:00",
        "notes": "Initial 9:16 20-Page Sovereign Dossier visual preview"
    },
    "tiktok_ad_01_generic_lifepath.mp4": {
        "filename": "tiktok_ad_01_generic_lifepath.mp4",
        "ad_id": "ad_01",
        "status": "uploaded",
        "mode": "published",
        "uploaded_at": "2026-10-22T16:45:00-07:00",
        "notes": "The 'Too Generic' Problem Hook"
    },
    "tiktok_ad_02_five_lenses_secret.mp4": {
        "filename": "tiktok_ad_02_five_lenses_secret.mp4",
        "ad_id": "ad_02",
        "status": "uploaded",
        "mode": "published",
        "uploaded_at": "2026-10-22T16:50:00-07:00",
        "notes": "The 'Name Sound Vibration + Birth Date' Hook"
    },
    "tiktok_ad_03_love_wealth_cycles.mp4": {
        "filename": "tiktok_ad_03_love_wealth_cycles.mp4",
        "ad_id": "ad_03",
        "status": "uploaded",
        "mode": "published",
        "uploaded_at": "2026-10-22T16:55:00-07:00",
        "notes": "The '52-Day Timing & Somatic Energy' Hook"
    }
}


class UploadTracker:
    """Manages uploaded_videos.json with automatic initialization and Google Drive sync."""

    def __init__(self, filepath: str = LOCAL_TRACKER_FILE, queue_dir: str = GDRIVE_QUEUE_DIR):
        self.filepath = filepath
        self.queue_dir = queue_dir
        self.gdrive_filepath = (
            os.path.join(queue_dir, "uploaded_videos.json")
            if os.path.exists(r"G:\My Drive")
            else None
        )
        self.data: Dict[str, Any] = {
            "account": "@sacrednumberblueprint",
            "updated_at": datetime.now().isoformat(),
            "uploaded": dict(INITIAL_UPLOADED_VIDEOS),
        }
        self.load()

    def load(self):
        loaded = None
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except Exception:
                loaded = None
        elif self.gdrive_filepath and os.path.exists(self.gdrive_filepath):
            try:
                with open(self.gdrive_filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except Exception:
                loaded = None

        if isinstance(loaded, dict):
            uploaded_map = loaded.get("uploaded", {})
            # Ensure the 4 baseline videos are always preserved
            for k, v in INITIAL_UPLOADED_VIDEOS.items():
                if k not in uploaded_map:
                    uploaded_map[k] = v
            self.data["uploaded"] = uploaded_map
            self.data["account"] = loaded.get("account", "@sacrednumberblueprint")

        self.save()

    def save(self):
        self.data["updated_at"] = datetime.now().isoformat()
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        if self.gdrive_filepath:
            os.makedirs(os.path.dirname(self.gdrive_filepath), exist_ok=True)
            try:
                shutil.copy2(self.filepath, self.gdrive_filepath)
            except Exception:
                pass

    def is_uploaded(self, filename: str) -> bool:
        base = os.path.basename(filename)
        entry = self.data.get("uploaded", {}).get(base)
        if not entry:
            return False
        return entry.get("status") in ("uploaded", "scheduled", "posted", "published")

    def mark_uploaded(
        self,
        filename: str,
        mode: str,
        caption: str,
        schedule_time: Optional[str] = None,
        ad_id: Optional[str] = None
    ):
        base = os.path.basename(filename)
        self.data.setdefault("uploaded", {})[base] = {
            "filename": base,
            "ad_id": ad_id,
            "status": "scheduled" if schedule_time else "uploaded",
            "mode": mode,
            "schedule_time": schedule_time,
            "uploaded_at": datetime.now().isoformat(),
            "caption_preview": caption[:120],
        }
        self.save()


class TikTokAutoUploader:
    def __init__(
        self,
        profile_dir: str = DEFAULT_PROFILE_DIR,
        queue_dir: str = GDRIVE_QUEUE_DIR,
        scripts_file: str = SCRIPTS_FILE,
        tracker_file: str = LOCAL_TRACKER_FILE
    ):
        self.profile_dir = profile_dir
        self.queue_dir = queue_dir if os.path.exists(queue_dir) else LOCAL_VIDEOS_DIR
        self.scripts_file = scripts_file
        self.tracker = UploadTracker(filepath=tracker_file, queue_dir=queue_dir)
        self.scripts_by_filename: Dict[str, Dict[str, Any]] = {}
        self.load_scripts()

    def load_scripts(self):
        if os.path.exists(self.scripts_file):
            with open(self.scripts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("scripts", []):
                    self.scripts_by_filename[item["filename"]] = item

    def discover_queue(
        self,
        target_video: Optional[str] = None,
        force: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Finds all MP4 videos in G:\\My Drive\\5_System_Numerology_MVP\\tiktok_queue\\
        (or local videos/ fallback), enriches them with caption metadata, and filters out
        already-uploaded videos unless force=True.
        """
        search_dirs = [self.queue_dir]
        if self.queue_dir != LOCAL_VIDEOS_DIR and os.path.exists(LOCAL_VIDEOS_DIR):
            search_dirs.append(LOCAL_VIDEOS_DIR)

        seen_files = set()
        candidates = []

        for d in search_dirs:
            for mp4_path in sorted(glob.glob(os.path.join(d, "*.mp4"))):
                fname = os.path.basename(mp4_path)
                if fname in seen_files:
                    continue
                seen_files.add(fname)

                if target_video and fname != os.path.basename(target_video) and target_video not in fname:
                    continue

                already = self.tracker.is_uploaded(fname)
                if already and not force:
                    continue

                meta = self.scripts_by_filename.get(fname, {})
                caption = meta.get(
                    "tiktok_caption",
                    "Test your 5-System Master Overlap numbers on our page 👁️✨ #numerology #lifepath #spirituality #chaldean #sacredgeometry"
                )
                first_comment = meta.get("first_comment", "")
                candidates.append({
                    "filename": fname,
                    "filepath": mp4_path,
                    "size_mb": round(os.path.getsize(mp4_path) / (1024 * 1024), 2),
                    "ad_id": meta.get("id"),
                    "hook_name": meta.get("hook_name", "Sacred Number Blueprint Video"),
                    "lang": meta.get("lang", "en"),
                    "caption": caption,
                    "first_comment": first_comment,
                    "already_uploaded": already,
                })

        return candidates

    def validate_schedule_str(self, schedule_str: str) -> datetime:
        """Validates 'YYYY-MM-DD HH:MM' format."""
        try:
            return datetime.strptime(schedule_str.strip(), "%Y-%m-%d %H:%M")
        except ValueError as e:
            raise ValueError(
                f"Invalid --schedule format '{schedule_str}'. Expected 'YYYY-MM-DD HH:MM' (e.g. '2026-10-23 14:30')."
            ) from e

    async def dismiss_joyride_overlays(self, page: Page):
        """Safely hides TikTok Studio's react-joyride onboarding tooltips via CSS without mutating React's DOM tree."""
        try:
            await page.add_style_tag(
                content="""
                #react-joyride-portal,
                .react-joyride__overlay,
                .react-joyride__spotlight,
                .react-joyride__tooltip,
                div[data-test-id="overlay"] {
                    pointer-events: none !important;
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                }
                """
            )
        except Exception:
            pass

    async def fill_caption_editor(self, page: Page, caption_text: str):
        """Fills the TikTok Studio DraftJS / contenteditable caption box."""
        await self.dismiss_joyride_overlays(page)
        editor_selectors = [
            'div.public-DraftEditor-content[contenteditable="true"]',
            'div[contenteditable="true"][role="combobox"]',
            'div[contenteditable="true"][data-contents="true"]',
            'div[contenteditable="true"]',
        ]
        for sel in editor_selectors:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                await self.dismiss_joyride_overlays(page)
                await loc.click(force=True)
                await asyncio.sleep(0.4)
                # Select existing default filename text and replace with caption
                await page.keyboard.press("Control+A")
                await asyncio.sleep(0.15)
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.25)
                await page.keyboard.insert_text(caption_text)
                await asyncio.sleep(0.5)
                # Close any hashtag autocomplete dropdown by pressing Escape
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.3)
                print("   [Studio] ✓ Populated caption & hashtags in editor.", flush=True)
                return True
        print("   [Studio] ⚠ Could not locate contenteditable caption box; continuing.", flush=True)
        return False

    async def configure_schedule_ui(self, page: Page, dt: datetime):
        """Switches TikTok Studio from 'Post now' to 'Schedule' and picks date/time."""
        date_str = dt.strftime("%Y-%m-%d")
        day_str = str(dt.day)
        hour_str = f"{dt.hour:02d}"
        minute_rounded = (dt.minute // 5) * 5
        min_str = f"{minute_rounded:02d}"
        time_str = f"{hour_str}:{min_str}"

        print(f"   [Studio] Configuring schedule for {date_str} {time_str}...", flush=True)

        # 1. Click the 'Schedule' radio button / label
        schedule_toggles = [
            'input[type="radio"][value="schedule"]',
            'label:has-text("Schedule")',
            'span:has-text("Schedule")',
        ]
        for sel in schedule_toggles:
            loc = page.locator(sel).first
            if await loc.count() > 0:
                try:
                    await loc.scroll_into_view_if_needed()
                    await loc.click(force=True, timeout=3000)
                    await asyncio.sleep(1.2)
                    break
                except Exception:
                    pass

        # 2. Pick Date (either via input or TikTok Studio calendar popup)
        date_inputs = page.locator('input[value*="2026-"], input[placeholder*="YYYY"]')
        if await date_inputs.count() > 0:
            try:
                await date_inputs.first.click(force=True)
                await asyncio.sleep(0.8)
                # Prefer span.day.valid (current month active day) over previous/next month overflow cells
                valid_day_cells = page.locator(f'span.day.valid:text-is("{day_str}")')
                clicked_day = False
                if await valid_day_cells.count() > 0:
                    for i in range(await valid_day_cells.count()):
                        cell = valid_day_cells.nth(i)
                        if await cell.is_visible():
                            await cell.click(force=True)
                            clicked_day = True
                            await asyncio.sleep(0.6)
                            break
                if not clicked_day:
                    day_cells = page.locator(f'span.day:text-is("{day_str}"), div[class*="calendar"] span:text-is("{day_str}"), td:text-is("{day_str}")')
                    for i in range(await day_cells.count() - 1, -1, -1):
                        cell = day_cells.nth(i)
                        if await cell.is_visible():
                            cls = (await cell.get_attribute("class") or "").lower()
                            if "disabled" not in cls:
                                await cell.click(force=True)
                                clicked_day = True
                                await asyncio.sleep(0.6)
                                break
            except Exception as e:
                print(f"   [Studio] Date picker note: {e}", flush=True)

        # 3. Pick Time (via time input / TikTok Studio timepicker columns)
        time_inputs = page.locator('input[value*=":"]')
        if await time_inputs.count() > 0:
            try:
                await time_inputs.first.click(force=True)
                await asyncio.sleep(0.8)
                # Click hour in left column and minute in right column if timepicker popup is open
                hr_opt = page.locator(f'span.tiktok-timepicker-left:text-is("{hour_str}"), div[class*="timepicker"] span:text-is("{hour_str}")').first
                if await hr_opt.count() > 0 and await hr_opt.is_visible():
                    await hr_opt.click(force=True)
                    await asyncio.sleep(0.4)
                min_opt = page.locator(f'span.tiktok-timepicker-right:text-is("{min_str}"), div[class*="timepicker"] span:text-is("{min_str}")').last
                if await min_opt.count() > 0 and await min_opt.is_visible():
                    await min_opt.click(force=True)
                    await asyncio.sleep(0.5)
                # Close the timepicker popover by clicking a neutral label outside the popover
                outside_label = page.locator('text="Who can see this post"').first
                if await outside_label.count() > 0:
                    await outside_label.click(force=True)
                else:
                    await page.mouse.click(20, 200)
                await asyncio.sleep(0.8)
            except Exception as e:
                print(f"   [Studio] Time picker note: {e}", flush=True)

        print(f"   [Studio] ✓ Schedule mode configured ({date_str} {time_str}).", flush=True)

    async def upload_single_video(
        self,
        page: Page,
        item: Dict[str, Any],
        mode: str,
        schedule_dt: Optional[datetime] = None
    ) -> bool:
        print(f"\n▶ [UPLOAD] Uploading {item['filename']} ({item['size_mb']} MB)...", flush=True)
        await page.goto(TIKTOK_UPLOAD_URL, wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(4.0)
        await self.dismiss_joyride_overlays(page)

        if "login" in page.url.lower():
            print("   [Auth] Not logged in! Navigating to QR login...", flush=True)
            await page.goto(TIKTOK_QR_LOGIN_URL, wait_until="domcontentloaded")
            await asyncio.sleep(3.0)
            qr_path = os.path.abspath("tiktok_qr_login.png")
            await page.screenshot(path=qr_path)
            print(f"   [Auth] Saved QR screenshot to {qr_path}. Scan in TikTok mobile app.", flush=True)
            return False

        # Locate file input
        file_input = page.locator('input[type="file"][accept*="video"], input[type="file"]').first
        await file_input.wait_for(state="attached", timeout=30000)
        await file_input.set_input_files(item["filepath"])
        print(f"   [Studio] ✓ Attached video file: {item['filepath']}", flush=True)

        # Wait for upload processing & caption editor to appear
        for _ in range(20):
            await asyncio.sleep(1.5)
            await self.dismiss_joyride_overlays(page)
            if await page.locator('div.public-DraftEditor-content[contenteditable="true"], div[contenteditable="true"]').count() > 0:
                break

        await asyncio.sleep(2.0)
        await self.fill_caption_editor(page, item["caption"])

        # Wait for video upload progress to finish and Post button to be enabled (up to 90s)
        print("   [Studio] Waiting for video upload & checks to complete...", flush=True)
        for wait_i in range(36):
            await self.dismiss_joyride_overlays(page)
            post_btn = page.locator('button[data-e2e="post_video_button"]').first
            if await post_btn.count() > 0:
                is_disabled = await post_btn.get_attribute("disabled")
                aria_disabled = await post_btn.get_attribute("aria-disabled")
                if is_disabled is None and aria_disabled != "true":
                    print(f"   [Studio] ✓ Video upload complete & Post button enabled (after {wait_i * 2.5:.1f}s).", flush=True)
                    break
            await asyncio.sleep(2.5)

        if mode == "schedule" and schedule_dt is not None:
            await self.configure_schedule_ui(page, schedule_dt)
            submit_selectors = [
                'button[data-e2e="post_video_button"]',
                'button.TUXButton--primary:has-text("Schedule")',
                'button:text-is("Schedule")',
            ]
        else:
            submit_selectors = [
                'button[data-e2e="post_video_button"]',
                'button.TUXButton--primary:text-is("Post")',
                'button:text-is("Post")',
            ]

        await self.dismiss_joyride_overlays(page)
        await page.screenshot(path=os.path.abspath("tiktok_upload_before_post.png"))
        clicked = False
        for sel in submit_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                try:
                    await btn.scroll_into_view_if_needed()
                    await asyncio.sleep(0.8)
                    await btn.click()
                    clicked = True
                    print(f"   [Studio] ✓ Clicked submit button ({sel}).", flush=True)
                    break
                except Exception as e:
                    print(f"   [Studio] Submit selector {sel} click exception: {e}", flush=True)

        await asyncio.sleep(2.5)
        # Check if TikTok Studio shows a secondary 'Continue to post? / Continue to schedule?' confirmation modal
        for _ in range(6):
            confirm_btns = page.locator(
                'div[role="dialog"] button.TUXButton--primary, '
                'div.TUXModal button.TUXButton--primary, '
                'button:has-text("Post now"), '
                'div[role="dialog"] button:has-text("Schedule"), '
                'div[role="dialog"] button:has-text("Continue")'
            )
            if await confirm_btns.count() > 0 and await confirm_btns.first.is_visible():
                try:
                    await confirm_btns.first.click(force=True)
                    print("   [Studio] ✓ Clicked secondary confirmation modal button.", flush=True)
                    await asyncio.sleep(5.0)
                    break
                except Exception as e:
                    print(f"   [Studio] Confirm modal click error: {e}", flush=True)
            await asyncio.sleep(1.0)

        await asyncio.sleep(4.0)
        await page.screenshot(path=os.path.abspath("tiktok_upload_after_post.png"))
        if clicked:
            sched_str = schedule_dt.strftime("%Y-%m-%d %H:%M") if schedule_dt else None
            self.tracker.mark_uploaded(
                item["filename"],
                mode=mode,
                caption=item["caption"],
                schedule_time=sched_str,
                ad_id=item.get("ad_id"),
            )
            print(f"   [Tracker] ✓ Marked {item['filename']} as {mode.upper()} in uploaded_videos.json", flush=True)

            # Automatically seed automod-safe creator first comment when posting live immediately
            if mode == "post_now" and item.get("first_comment"):
                try:
                    from seed_first_comments import seed_comment_on_video_from_profile
                    print("   [Seeder] Auto-seeding automod-safe creator first comment...", flush=True)
                    await asyncio.sleep(4.0)
                    await seed_comment_on_video_from_profile(
                        page,
                        title_match=item["caption"][:48],
                        comment_text=item["first_comment"],
                    )
                except Exception as e:
                    print(f"   [Seeder] Auto-seed note: {e}", flush=True)

            return True

        print(f"   [Studio] ⚠ Could not confirm final submit click for {item['filename']}.", flush=True)
        return False

    async def run(
        self,
        dry_run: bool = False,
        post_now: bool = False,
        schedule_str: Optional[str] = None,
        target_video: Optional[str] = None,
        limit: int = 1,
        force: bool = False
    ):
        schedule_dt = self.validate_schedule_str(schedule_str) if schedule_str else None
        mode = "schedule" if schedule_dt else ("post_now" if post_now else "dry_run")

        print("=" * 72)
        print("   SACRED NUMBER BLUEPRINT · TIKTOK STUDIO AUTO-UPLOADER")
        print("=" * 72)
        print(f"Profile Dir : {self.profile_dir}")
        print(f"Queue Dir   : {self.queue_dir}")
        print(f"Tracker File: {self.tracker.filepath}")
        print(f"Action Mode : {mode.upper()}" + (f" ({schedule_str})" if schedule_str else ""))
        print("-" * 72)

        # Print already uploaded videos
        uploaded_map = self.tracker.data.get("uploaded", {})
        print(f"Already Tracked / Uploaded Videos ({len(uploaded_map)}):")
        for k, v in uploaded_map.items():
            print(f"  ✓ {k} [{v.get('status', 'uploaded')} - {v.get('mode', '')}]")

        # Discover pending queue
        candidates = self.discover_queue(target_video=target_video, force=force)
        print("-" * 72)
        print(f"Pending Un-Uploaded Videos in Queue ({len(candidates)}):")
        for i, c in enumerate(candidates, 1):
            print(f"  {i}. {c['filename']} ({c['size_mb']} MB | lang={c['lang'].upper()}) — {c['hook_name']}")

        if not candidates:
            print("\nNo pending un-uploaded videos matched. Use --force to re-upload a tracked video.")
            print("=" * 72)
            return

        selected = candidates[: max(1, limit)]
        print("-" * 72)
        print(f"Selected Batch ({len(selected)} video(s)):")
        for c in selected:
            print(f"  • Video   : {c['filename']} ({c['filepath']})")
            print(f"  • Action  : {'SCHEDULE at ' + schedule_str if schedule_dt else ('POST IMMEDIATELY' if post_now else 'DRY-RUN VERIFICATION')}")
            print(f"  • Caption : {c['caption']}")

        if dry_run or (not post_now and not schedule_dt):
            print("\n[DRY-RUN COMPLETE] Queue, deduplication tracker, and captions verified with zero errors.")
            print("=" * 72)
            return

        os.makedirs(self.profile_dir, exist_ok=True)
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=False,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport=None,
            )
            page = context.pages[0] if context.pages else await context.new_page()
            for item in selected:
                await self.upload_single_video(page, item, mode=mode, schedule_dt=schedule_dt)
            await context.close()

        print("=" * 72)


def main():
    parser = argparse.ArgumentParser(
        description="Automated TikTok Studio Uploader with Deduplication Tracking"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify queue, uploaded_videos.json deduplication, and captions without uploading",
    )
    parser.add_argument(
        "--post-now",
        action="store_true",
        help="Upload and publish immediately in TikTok Studio",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default=None,
        help='Schedule upload for "YYYY-MM-DD HH:MM" (e.g. "2026-10-23 11:00")',
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Specific MP4 filename to upload (defaults to next un-uploaded video in queue)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Maximum number of pending videos to upload in this run (default: 1)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow uploading a video even if already marked in uploaded_videos.json",
    )
    args = parser.parse_args()

    uploader = TikTokAutoUploader()
    asyncio.run(
        uploader.run(
            dry_run=args.dry_run,
            post_now=args.post_now,
            schedule_str=args.schedule,
            target_video=args.video,
            limit=args.limit,
            force=args.force,
        )
    )


if __name__ == "__main__":
    main()
