#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · 2-HOUR SOCIAL AUTO-SYNC RUNNER
social_auto_sync.py
-----------------------------------------------------------------------------
Invoked every 2 hours by the Windows Scheduled Task `\Sovereign5SocialAutoSync`.
Executes in sequence:
1. `seed_first_comments.py --wait-seconds 15` & `seed_sample_reading_replies.py --platform all`
2. `tiktok_comment_responder.py --live --limit 15`
3. `ig_comment_responder.py --live --limit 15`
4. `yt_comment_responder.py --live --limit 15`
5. `lead_capture_worker.py --poll-once`
=============================================================================
"""

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


def run_step(label: str, cmd: list):
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


def main():
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
        "5. Lead Capture Telemetry & Brevo Email Worker Poll",
        [PYTHON_EXE, os.path.join(BASE_DIR, "lead_capture_worker.py"), "--poll-once"],
    )


if __name__ == "__main__":
    main()
