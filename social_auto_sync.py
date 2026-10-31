#!/usr/bin/env python3
"""
=============================================================================
SACRED NUMBER BLUEPRINT · 2-HOUR SOCIAL AUTO-SYNC RUNNER
social_auto_sync.py
-----------------------------------------------------------------------------
Invoked every 2 hours by the Windows Scheduled Task `\Sovereign5SocialAutoSync`.
Executes in sequence:
1. `tiktok_comment_responder.py --live --limit 10`
2. `ig_comment_responder.py --live --limit 10`
3. `seed_first_comments.py --wait-seconds 15` (seeds first comments on any newly
   published TikTok videos such as `short_06`, `short_07`, `short_08`, `short_09`)
4. Cross-posts the next unposted Cohort-C video (`short_08`, `short_09`) to
   Instagram Reels if its scheduled window has arrived.
=============================================================================
"""

import os
import subprocess
import sys
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
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
        "1. TikTok Comment Auto-Responder",
        [PYTHON_EXE, os.path.join(BASE_DIR, "tiktok_comment_responder.py"), "--live", "--limit", "10"],
    )
    run_step(
        "2. Instagram Comment Auto-Responder",
        [PYTHON_EXE, os.path.join(BASE_DIR, "ig_comment_responder.py"), "--live", "--limit", "10"],
    )
    run_step(
        "3. TikTok First-Comment Seeder (Newly Live Videos)",
        [PYTHON_EXE, os.path.join(BASE_DIR, "seed_first_comments.py"), "--wait-seconds", "15"],
    )
    run_step(
        "4. TikTok Top-3 Video Pinner (short_02, short_10, short_11)",
        [PYTHON_EXE, os.path.join(BASE_DIR, "pin_top_videos.py")],
    )


if __name__ == "__main__":
    main()
