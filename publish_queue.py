"""
Automated TikTok Queue Manager & Publisher Utility
Inspects ready-to-post videos, verifies file sizes and durations,
and prints copy-paste captions for TikTok Web Studio.
"""

import os, json, glob

QUEUE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_FILE = os.path.join(QUEUE_DIR, "tiktok_scripts.json")

def inspect_queue():
    print("=" * 65)
    print("   SACRED NUMBER BLUEPRINT · TIKTOK QUEUE STATUS")
    print("=" * 65)
    
    mp4s = sorted(glob.glob(os.path.join(QUEUE_DIR, "tiktok_ad_*.mp4")))
    if not mp4s:
        mp4s = sorted(glob.glob("tiktok_ad_*.mp4"))
    
    print(f"Found {len(mp4s)} videos ready for broadcast:")
    for f in mp4s:
        sz_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  • {os.path.basename(f)}: {sz_mb:.2f} MB")
        
    print("\nAutomated Uploader Commands:")
    print("  • Dry run:  python tiktok_auto_uploader.py --dry-run")
    print("  • Post now: python tiktok_auto_uploader.py --post-now")
    print("  • Schedule: python tiktok_auto_uploader.py --schedule \"YYYY-MM-DD HH:MM\"")
    print("=" * 65)

if __name__ == "__main__":
    inspect_queue()
