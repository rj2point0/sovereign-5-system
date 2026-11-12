#!/usr/bin/env python3
r"""
=============================================================================
SACRED NUMBER BLUEPRINT · AUTOMATED SOCIAL RELEASE & SYNC RUNNER
social_auto_sync.py
-----------------------------------------------------------------------------
Invoked every 30 minutes by Windows Scheduled Task `\Sovereign5SocialAutoSync`.
Executes in sequence:
0. Auto-publishes any due scheduled Instagram Reels (`Short_055`–`Short_059`+)
   via `ig_reels_auto_uploader.py --video <filename>` as soon as their PST
   release window arrives (since IG Web has no native scheduled queue).
1a. `seed_first_comments.py --wait-seconds 15` (TikTok 2-birthday prompt)
1b. `seed_sample_reading_replies.py --platform all` (TikTok + dynamic IG sample reply)
1c. `yt_shorts_auto_uploader.py --seed-newly-live` (YT Shorts prompt + sample + pin)
2. `tiktok_comment_responder.py --live --limit 15`
3. `ig_comment_responder.py --live --limit 15`
4. `yt_comment_responder.py --live --limit 15`
5. `lead_capture_worker.py --poll-once`
=============================================================================
"""

import json
import os
import subprocess
import sys
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
LOG_PATH = os.path.join(BASE_DIR, "social_auto_sync.log")
YT_TRACKER_PATH = os.path.join(BASE_DIR, "uploaded_yt_shorts.json")
IG_TRACKER_PATH = os.path.join(BASE_DIR, "uploaded_ig_reels.json")


def run_step(label: str, cmd: list) -> int:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n[{ts}] ▶ {label}: {' '.join(cmd)}\n"
    print(header, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as lf:
        lf.write(header)
        lf.flush()
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            stdout=lf,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lf.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ {label} exited with code {proc.returncode}\n")
        return proc.returncode


def get_due_ig_reels(now_dt: datetime | None = None) -> list[tuple[str, str, str]]:
    """
    Returns [(short_id, filename, schedule_str), ...] for any episode in
    uploaded_yt_shorts.json whose scheduled local release window has arrived
    (now_dt >= scheduled_dt) and that has NOT yet been shared in uploaded_ig_reels.json.
    """
    now = now_dt or datetime.now()
    if not os.path.exists(YT_TRACKER_PATH):
        return []
    try:
        yt_videos = json.load(open(YT_TRACKER_PATH, "r", encoding="utf-8")).get("videos", {})
    except Exception:
        return []

    ig_uploaded = {}
    if os.path.exists(IG_TRACKER_PATH):
        try:
            ig_uploaded = json.load(open(IG_TRACKER_PATH, "r", encoding="utf-8")).get("uploaded_reels", {})
        except Exception:
            ig_uploaded = {}

    due: list[tuple[str, str, str]] = []
    for sid in sorted(yt_videos.keys()):
        if sid < "short_50":
            continue
        info = yt_videos[sid]
        fname = str(info.get("filename") or "").strip()
        sched_str = str(info.get("schedule") or "").strip()
        if not fname:
            continue
        if fname in ig_uploaded and ig_uploaded[fname].get("status") == "shared":
            continue
        if sched_str == "LIVE":
            is_due = True
        else:
            try:
                sched_dt = datetime.strptime(sched_str, "%b %d, %Y %I:%M %p")
                is_due = now >= sched_dt
            except Exception:
                is_due = False
        if is_due:
            due.append((sid, fname, sched_str))
    return due


def auto_publish_due_ig_reels():
    due = get_due_ig_reels()
    if not due:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] ✓ [0. IG Scheduled Auto-Publisher] 0 due IG Reels right now (next release waiting for schedule window).\n"
        print(msg.strip(), flush=True)
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(msg)
        return
    for sid, fname, sched_str in due:
        run_step(
            f"0. Auto-Publish Due IG Reel [{sid} · {sched_str}]",
            [PYTHON_EXE, os.path.join(BASE_DIR, "ig_reels_auto_uploader.py"), "--video", fname],
        )


def main():
    if "--check-due-only" in sys.argv:
        due = get_due_ig_reels()
        print(f"Due IG Reels right now ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}): {due}")
        if os.path.exists(YT_TRACKER_PATH):
            yt_v = json.load(open(YT_TRACKER_PATH, "r", encoding="utf-8")).get("videos", {})
            ig_u = json.load(open(IG_TRACKER_PATH, "r", encoding="utf-8")).get("uploaded_reels", {}) if os.path.exists(IG_TRACKER_PATH) else {}
            for sid in sorted(k for k in yt_v if k >= "short_54"):
                fn = yt_v[sid].get("filename")
                st = "SHARED" if (fn in ig_u and ig_u[fn].get("status") == "shared") else f"AUTO-QUEUED ({yt_v[sid].get('schedule')})"
                print(f"  • {sid}: {fn} -> {st}")
        return

    auto_publish_due_ig_reels()
    run_step(
        "1a. TikTok First-Comment Seeder (Newly Live Videos)",
        [PYTHON_EXE, os.path.join(BASE_DIR, "seed_first_comments.py"), "--wait-seconds", "15"],
    )
    run_step(
        "1b. Social Proof Sample Match Follow-Up Seeder (TikTok + IG)",
        [PYTHON_EXE, os.path.join(BASE_DIR, "seed_sample_reading_replies.py"), "--platform", "all"],
    )
    run_step(
        "1c. YouTube Shorts Newly-Live Scheduled Seeder & Pinner",
        [PYTHON_EXE, os.path.join(BASE_DIR, "yt_shorts_auto_uploader.py"), "--seed-newly-live"],
    )
    run_step(
        "2. TikTok Comment Auto-Responder",
        [PYTHON_EXE, os.path.join(BASE_DIR, "tiktok_comment_responder.py"), "--live", "--limit", "15"],
    )
    run_step(
        "3. Instagram Comment Auto-Responder",
        [PYTHON_EXE, os.path.join(BASE_DIR, "ig_comment_responder.py"), "--live", "--limit", "15"],
    )
    run_step(
        "4. YouTube Shorts Comment Auto-Responder",
        [PYTHON_EXE, os.path.join(BASE_DIR, "yt_comment_responder.py"), "--live", "--limit", "15"],
    )
    run_step(
        "5. Lead Capture Telemetry & Email Worker Poll",
        [PYTHON_EXE, os.path.join(BASE_DIR, "lead_capture_worker.py"), "--poll-once"],
    )


if __name__ == "__main__":
    main()
