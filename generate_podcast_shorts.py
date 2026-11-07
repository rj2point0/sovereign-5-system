#!/usr/bin/env python3
"""
Dual-Voice Split-Screen / Reaction Podcast Renderer (`podcast_duet_giant`)
for @sacrednumberblueprint (Mega Vega Ventures LLC).

Renders 1080x1920 30fps Dual-Host AI Podcast Shorts featuring:
- Host #1 ("Maya" · en-US-AvaMultilingualNeural at +12% rate): Late-Night Bestie / Interviewer
- Host #2 ("Julian" · en-US-AndrewMultilingualNeural at +12% rate): Male Insider / Reformed Ex
- 30fps Audio-Envelope Lip-Sync + Camera Breathing + Active Speaker Spotlight Shift
- 4-Layer Dr. Plants Studio SFX Bed + Lower-Third Interactive Reveal Dock (4.6s-7.5s)
"""

import argparse
import asyncio
from generate_broll_story_tiktoks import BrollStoryGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Dual-Host AI Podcast Shorts (podcast_duet_giant).")
    parser.add_argument(
        "--only",
        type=str,
        default="short_37,short_38,short_39",
        help="Comma-separated podcast short IDs to render (default: short_37,short_38,short_39)",
    )
    args = parser.parse_args()
    gen = BrollStoryGenerator()
    asyncio.run(gen.run(cohort="C", only_ids=args.only))


if __name__ == "__main__":
    main()
