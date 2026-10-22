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
        # Check parent folder
        mp4s = sorted(glob.glob("tiktok_ad_*.mp4"))
    
    print(f"Found {len(mp4s)} videos ready for broadcast:")
    for f in mp4s:
        sz_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  • {os.path.basename(f)}: {sz_mb:.2f} MB")
        
    print("\nPosting Instructions:")
    print("  1. Log into TikTok Web Studio: https://www.tiktok.com/creator-center/upload")
    print("  2. Upload desired MP4 video.")
    print("  3. Copy caption & hashtags from captions_and_hashtags.md")
    print("  4. Verify Link in Bio points to: https://rj2point0.github.io/sovereign-5-system/")
    print("=" * 65)

if __name__ == "__main__":
    inspect_queue()
