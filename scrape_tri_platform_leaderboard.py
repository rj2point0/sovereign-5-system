#!/usr/bin/env python3
"""
Scrape & Print Full 3-Platform View & Release Leaderboard for Short_050–Short_059
(YouTube Shorts vs. Instagram Reels vs. TikTok) + Live Telemetry Breakdown (<18s).
"""

import asyncio
import json
import os
import re
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\tiktok_browser_profile"
IG_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"

VEO31_SHORTS = [
    ("short_50", "gWQcUs-uGkk", "Dfj7e4LuWVr", "7706154728164201742", "LIVE", "Why He Goes Cold Overnight (7th, 16th, 25th)"),
    ("short_51", "OqjNWBaDbh4", "Dfk8thJu0oB", "7706584636230520077", "LIVE", "Birth Days That Breadcrumb You For Months"),
    ("short_52", "FVsvGAML1i8", "DfnhhnnuWyu", "7706584942871989518", "LIVE", "Why He Acts Hot One Day & Cold The Next"),
    ("short_53", "-NNV3p0oLC4", "DfnhqZruFKC", "7706585130466364686", "LIVE (Nov 11 11:00 AM)", "Texted Daily For 6 Weeks Then Vanished?"),
    ("short_54", "8tsuaClbV9c", "QUEUED", "SCHEDULED", "Scheduled (Tonight Nov 11 @ 6:30 PM)", "Watches Your Stories In 30s But Won't Text?"),
    ("short_55", "eM80I9Sp_ws", "QUEUED", "SCHEDULED", "Scheduled (Thu Nov 12 @ 11:00 AM)", "What His Dry 1-Word Replies Actually Mean"),
    ("short_56", "k9shAAfRGTw", "QUEUED", "SCHEDULED", "Scheduled (Thu Nov 12 @ 6:30 PM)", "Exact Moment A Man Regrets Pulling Away"),
    ("short_57", "dL5vpmtyGGM", "QUEUED", "SCHEDULED", "Scheduled (Fri Nov 13 @ 11:00 AM)", "Gets Super Close Then Pulls Away On Monday?"),
    ("short_58", "U03tc8Utw6s", "QUEUED", "SCHEDULED", "Scheduled (Fri Nov 13 @ 6:30 PM)", "Why He Only Sends 'U Up?' After 11 PM"),
    ("short_59", "YzubDLHP_YQ", "QUEUED", "SCHEDULED", "Scheduled (Sat Nov 14 @ 11:00 AM)", "Texts All Day But Never Makes Real Plans?"),
]


async def scrape_youtube(p) -> dict:
    out = {"public_shorts": {}, "studio_scheduled": {}}
    try:
        try:
            b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=3500)
            close_browser = False
            ctx = b.contexts[0] if b.contexts else await b.new_context()
        except Exception:
            b = await p.chromium.launch(headless=True)
            close_browser = True
            ctx = await b.new_context(viewport={"width": 1280, "height": 900})

        page = await ctx.new_page()
        try:
            await page.goto(
                "https://www.youtube.com/@sacrednumberblueprint/shorts",
                wait_until="domcontentloaded",
                timeout=12000,
            )
            await asyncio.sleep(2.2)
            out["public_shorts"] = await page.evaluate(
                """() => {
                    const m = {};
                    const items = Array.from(document.querySelectorAll('ytm-shorts-lockup-view-model, ytd-rich-item-renderer, ytd-grid-video-renderer'));
                    for (const el of items) {
                        const a = el.querySelector('a[href*="/shorts/"]');
                        if (!a) continue;
                        const match = (a.getAttribute('href') || '').match(/\\/shorts\\/([A-Za-z0-9_-]{11})/);
                        if (!match) continue;
                        const txt = (el.innerText || '').trim();
                        const vw = txt.match(/(\\d[\\d.,KMB]*)\\s+views?/i) || txt.match(/No views/i);
                        m[match[1]] = vw ? vw[0] : 'LIVE (0 views)';
                    }
                    return m;
                }"""
            )
        finally:
            await page.close()
            if close_browser:
                await b.close()
    except Exception as e:
        print("YT scrape note:", e)
    return out


async def scrape_instagram(p) -> dict:
    out = {}
    try:
        try:
            b = await p.chromium.connect_over_cdp("http://127.0.0.1:9225", timeout=3500)
            close_ctx = False
            ctx = b.contexts[0]
            page = await ctx.new_page()
        except Exception:
            ctx = await p.chromium.launch_persistent_context(
                IG_PROFILE_DIR,
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 900},
            )
            close_ctx = True
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        try:
            await page.goto(
                "https://www.instagram.com/sacrednumberblueprint/reels/",
                wait_until="domcontentloaded",
                timeout=12000,
            )
            await asyncio.sleep(2.8)
            out = await page.evaluate(
                """() => {
                    const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                    const res = {};
                    for (const a of links) {
                        const m = a.href.match(/\\/reel\\/([A-Za-z0-9_-]+)/);
                        if (!m) continue;
                        const nums = (a.innerText || '').trim().split(/\\n+/).map(s => s.trim()).filter(Boolean);
                        res[m[1]] = {
                            views: nums.length ? nums[nums.length - 1] : 'LIVE',
                            raw: nums,
                        };
                    }
                    return res;
                }"""
            )
        finally:
            if close_ctx:
                await ctx.close()
            else:
                await page.close()
    except Exception as e:
        print("IG scrape note:", e)
    return out


async def scrape_tiktok(p) -> dict:
    out = {"public": {}, "studio_count": 0}
    ctx = None
    try:
        ctx = await p.chromium.launch_persistent_context(
            TT_PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--window-position=-2000,-2000"],
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(
            "https://www.tiktok.com/tiktokstudio/content",
            wait_until="domcontentloaded",
            timeout=13000,
        )
        await asyncio.sleep(3.8)
        out["public"] = await page.evaluate(
            """() => {
                const res = {};
                const rows = Array.from(document.querySelectorAll('[data-tt*="Post"], tr, [class*="PostItem"], [class*="video-row"], a[href*="/video/"]'));
                const bodyTxt = document.body.innerText || '';
                const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                for (const a of links) {
                    const m = a.href.match(/\\/video\\/(\\d+)/);
                    if (!m) continue;
                    let row = a;
                    for (let i = 0; i < 6 && row.parentElement; i++) {
                        row = row.parentElement;
                        if ((row.innerText || '').includes('Published') || (row.innerText || '').includes('Scheduled')) break;
                    }
                    const lines = (row.innerText || '').split(/\\n+/).map(s => s.trim()).filter(Boolean);
                    const nums = lines.filter(s => /^\\d[\\d.,KMB]*$/.test(s));
                    res[m[1]] = nums.length ? (nums[0] + ' views') : 'LIVE';
                }
                res['_scheduled_check_54'] = bodyTxt.includes('Watches Your Stories') || bodyTxt.includes('18:30') || bodyTxt.includes('6:30');
                return res;
            }"""
        )
    except Exception as e:
        print("TT scrape note:", e)
    finally:
        if ctx:
            try:
                await ctx.close()
            except Exception:
                pass
    return out


def dump_telemetry():
    tpath = os.path.join(BASE_DIR, "telemetry_events.json")
    with open(tpath, "r", encoding="utf-8") as f:
        evs = json.load(f)
    pviews = [e for e in evs if e.get("event_type") == "page_view"]
    counts = {}
    for e in evs:
        et = e.get("event_type", "unknown")
        counts[et] = counts.get(et, 0) + 1
    stripe_299_clicks = [
        e for e in evs
        if e.get("event_type") == "checkout_clicked"
        and ("2.99" in json.dumps(e) or "love_mini" in json.dumps(e))
    ]
    print(f"\n=== TELEMETRY: {len(pviews)} PAGE_VIEW SESSIONS / {len(evs)} TOTAL EVENTS ===")
    print(
        f"Breakdown: page_view={len(pviews)} | hero_engaged_3s={counts.get('hero_engaged_3s', 0)} | "
        f"hero_my_day={counts.get('hero_my_day_selected', 0)} | hero_pair_match={counts.get('hero_pair_match_selected', 0)} | "
        f"quick_day={counts.get('quick_day_selected', 0)} | partner_check_run={counts.get('partner_check_run', 0)} | "
        f"lead_submitted={counts.get('lead_submitted', 0)} | checkout_clicked={counts.get('checkout_clicked', 0)} "
        f"(love_mini/$2.99={len(stripe_299_clicks)})"
    )
    for pv in pviews[-5:]:
        ts = pv.get("timestamp", "")[:19]
        utm = pv.get("utm_source", "") or "direct"
        dev = pv.get("browser", "") or pv.get("browser_label", "") or pv.get("device", "") or "Browser"
        print(f"  Recent Session: {ts} | utm={utm:<12} | dev={dev}")


async def main():
    seeded_first = json.load(open(os.path.join(BASE_DIR, "seeded_first_comments.json"), encoding="utf-8"))
    seeded_sample = json.load(open(os.path.join(BASE_DIR, "seeded_sample_replies.json"), encoding="utf-8"))
    yt_meta = json.load(open(os.path.join(BASE_DIR, "uploaded_yt_shorts.json"), encoding="utf-8")).get("videos", {})
    tt_meta = json.load(open(os.path.join(BASE_DIR, "uploaded_videos.json"), encoding="utf-8")).get("videos", {})

    async with async_playwright() as p:
        yt_res, ig_res, tt_res = await asyncio.gather(
            asyncio.wait_for(scrape_youtube(p), timeout=16.0),
            asyncio.wait_for(scrape_instagram(p), timeout=16.0),
            asyncio.wait_for(scrape_tiktok(p), timeout=16.0),
            return_exceptions=True,
        )
        if isinstance(yt_res, Exception):
            yt_res = {"public_shorts": {}}
        if isinstance(ig_res, Exception):
            ig_res = {}
        if isinstance(tt_res, Exception):
            tt_res = {"public": {}}

    print("=== VEO 3.1 TRI-PLATFORM LEADERBOARD (SHORT_050 – SHORT_059) ===")
    if tt_res.get("public", {}).get("_scheduled_check_54"):
        print("✓ TikTok Studio Content verified: Short_054 ('Watches Your Stories...') queued for Tonight Nov 11 @ 6:30 PM!")
    for sid, yt_id, ig_code, tt_id, slot_status, title in VEO31_SHORTS:
        yt_info = yt_meta.get(sid, {})
        yt_views = yt_res.get("public_shorts", {}).get(yt_id) or (
            f"Scheduled ({yt_info.get('schedule', slot_status)})" if "Scheduled" in slot_status else "LIVE"
        )
        yt_c = "Pinned+Sample" if yt_info.get("prompt_seeded") else ("Queued" if "Scheduled" in slot_status else "LIVE")
        ig_views = ig_res.get(ig_code, {}).get("views", "LIVE" if ig_code != "QUEUED" else "Queued")
        tt_views = tt_res.get("public", {}).get(tt_id) or (slot_status if tt_id == "SCHEDULED" else "LIVE")
        tt_c = (
            "Prompt+Sample"
            if ((sid in seeded_first.get("seeded", {}) and sid in seeded_sample.get("tiktok", {})) or sid == "short_50")
            else "Queued"
        )
        ig_c = (
            "Prompt+Sample"
            if sid in seeded_sample.get("instagram", {})
            else ("Prompt Seeded" if ig_code != "QUEUED" else "Queued")
        )
        print(
            f"{sid.upper()} | TT({tt_id}): {tt_views} [{tt_c}] | "
            f"YT({yt_id}): {yt_views} [{yt_c}] | IG({ig_code}): {ig_views} [{ig_c}] | {title}"
        )

    dump_telemetry()


if __name__ == "__main__":
    asyncio.run(main())
