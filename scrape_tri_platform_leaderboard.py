#!/usr/bin/env python3
"""
Scrape & Print Full 3-Platform View & Release Leaderboard for Short_050–Short_059
(YouTube Shorts vs. Instagram Reels vs. TikTok) + Live Telemetry Breakdown (<18s).
"""

import asyncio
from datetime import datetime
import json
import os
import sys
import time
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
    ("short_50", "gWQcUs-uGkk", "Dfj7e4LuWVr", "7706521591961685261", "LIVE", "Why He Goes Cold Overnight (7th, 16th, 25th)"),
    ("short_51", "OqjNWBaDbh4", "Dfk8thJu0oB", "7706584636230520077", "LIVE", "Birth Days That Breadcrumb You For Months"),
    ("short_52", "FVsvGAML1i8", "DfnhhnnuWyu", "7706584942871989518", "LIVE", "Why He Acts Hot One Day & Cold The Next"),
    ("short_53", "-NNV3p0oLC4", "DfnhqZruFKC", "7706585130466364686", "LIVE", "Texted Daily For 6 Weeks Then Vanished?"),
    ("short_54", "8tsuaClbV9c", "DfpUlv-OEJ3", "7706595930299960590", "LIVE", "Watches Your Stories In 30s But Won't Text?"),
    ("short_55", "eM80I9Sp_ws", "QUEUED", "7706595957424622862", "Scheduled (Thu Nov 12 @ 11:00 AM)", "What His Dry 1-Word Replies Actually Mean"),
    ("short_56", "k9shAAfRGTw", "QUEUED", "7706596196311108878", "Scheduled (Thu Nov 12 @ 6:30 PM)", "Exact Moment A Man Regrets Pulling Away"),
    ("short_57", "dL5vpmtyGGM", "QUEUED", "7707039781108174093", "Scheduled (Fri Nov 13 @ 11:00 AM)", "Gets Super Close Then Pulls Away On Monday?"),
    ("short_58", "U03tc8Utw6s", "QUEUED", "7707039999321034015", "Scheduled (Fri Nov 13 @ 6:30 PM)", "Why He Only Sends 'U Up?' After 11 PM"),
    ("short_59", "YzubDLHP_YQ", "QUEUED", "7707040089796365598", "Scheduled (Sat Nov 14 @ 11:00 AM)", "Texts All Day But Never Makes Real Plans?"),
]


async def scrape_youtube(p) -> dict:
    out = {"public_shorts": {}}
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
            await asyncio.sleep(2.4)
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
                        m[match[1]] = vw ? vw[0] : '0 views';
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
                            views: nums.length ? (nums[nums.length - 1] + ' views') : '0 views',
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
    """Extracts exact numeric play_count & schedule_time from TikTok Studio's creator/manage/item_list JSON API + DOM fallback."""
    out = {"items": {}}
    ctx = None
    now_ts = int(time.time())
    try:
        ctx = await p.chromium.launch_persistent_context(
            TT_PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--window-position=-2000,-2000"],
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        async def on_response(resp):
            if "creator/manage/item_list" in resp.url:
                try:
                    data = await resp.json()
                    for it in data.get("item_list") or []:
                        iid = str(it.get("item_id") or it.get("id") or "")
                        if not iid:
                            continue
                        plays = int(it.get("play_count") or 0)
                        likes = int(it.get("like_count") or 0)
                        comments = int(it.get("comment_count") or 0)
                        sched_ts = int(it.get("schedule_time") or 0)
                        out["items"][iid] = {
                            "plays": plays,
                            "likes": likes,
                            "comments": comments,
                            "schedule_time": sched_ts,
                            "is_scheduled": sched_ts > now_ts,
                        }
                except Exception:
                    pass

        page.on("response", on_response)
        await page.goto(
            "https://www.tiktok.com/tiktokstudio/content",
            wait_until="domcontentloaded",
            timeout=14000,
        )
        await asyncio.sleep(4.5)

        # DOM fallback for any row not yet captured by item_list API
        dom_map = await page.evaluate(
            """() => {
                const res = {};
                const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                for (const a of links) {
                    const m = a.href.match(/\\/video\\/(\\d+)/);
                    if (!m) continue;
                    let row = a;
                    for (let i = 0; i < 7 && row.parentElement; i++) {
                        row = row.parentElement;
                        if ((row.innerText || '').includes('Everyone')) break;
                    }
                    const lines = (row.innerText || '').split(/\\n+/).map(s => s.trim()).filter(Boolean);
                    const evIdx = lines.findIndex(s => s === 'Everyone');
                    if (evIdx >= 0 && evIdx + 1 < lines.length && /^\\d[\\d.,KMB]*$/.test(lines[evIdx + 1])) {
                        res[m[1]] = lines[evIdx + 1];
                    }
                }
                return res;
            }"""
        )
        for vid, vstr in dom_map.items():
            if vid not in out["items"]:
                out["items"][vid] = {"plays": vstr, "likes": 0, "comments": 0, "schedule_time": 0, "is_scheduled": False}
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
    from lead_capture_worker import (
        INTERNAL_TEST_EMAILS,
        LOCAL_CSV_PATH,
        filter_external_customer_events,
        is_internal_test_email,
    )
    import csv

    tpath = os.path.join(BASE_DIR, "telemetry_events.json")
    with open(tpath, "r", encoding="utf-8") as f:
        raw_evs = json.load(f)

    ext_evs, bot_evs = filter_external_customer_events(raw_evs)
    pviews = [e for e in ext_evs if e.get("event_type") == "page_view"]
    bot_pviews = [e for e in bot_evs if e.get("event_type") == "page_view"]

    counts = {}
    for e in ext_evs:
        et = e.get("event_type", "unknown")
        counts[et] = counts.get(et, 0) + 1

    csv_rows = list(csv.DictReader(open(LOCAL_CSV_PATH, encoding="utf-8"))) if os.path.exists(LOCAL_CSV_PATH) else []
    real_leads = [r for r in csv_rows if not is_internal_test_email(r.get("email"))]
    test_leads = [r for r in csv_rows if is_internal_test_email(r.get("email"))]

    stripe_299_clicks = [
        e for e in ext_evs
        if e.get("event_type") == "checkout_clicked"
        and ("2.99" in json.dumps(e) or "love_mini" in json.dumps(e))
    ]
    purchases = [
        e for e in ext_evs
        if e.get("event_type") in ("purchase_completed", "dossier_unlocked", "payment_verified", "purchase_return")
    ]
    print(
        f"\n=== TRUE EXTERNAL CUSTOMER TELEMETRY: {len(pviews)} REAL SESSIONS "
        f"(+{len(bot_pviews)} Playwright/crawler filtered from {len(pviews)+len(bot_pviews)} raw) ==="
    )
    print(
        f"External Funnel: page_view={len(pviews)} | calc_started={counts.get('calc_started', 0)} | "
        f"quick_day={counts.get('quick_day_selected', 0)} | calc_preview={counts.get('calc_preview', 0)} | "
        f"partner_check_run={counts.get('partner_check_run', 0)} | real_leads={len(real_leads)} "
        f"(+{len(test_leads)} [INTERNAL TEST] excluded) | checkout_clicked={counts.get('checkout_clicked', 0)} "
        f"(love_mini/$2.99={len(stripe_299_clicks)}) | purchases={len(purchases)}"
    )
    for pv in pviews:
        ts = pv.get("timestamp", "")[:19]
        utm = (pv.get("utm") or {}).get("utm_source") or pv.get("source_attribution") or "direct"
        dev = pv.get("browser_label") or pv.get("browser") or "Browser"
        ref = pv.get("referrer") or ""
        print(f"  External Session: {ts} | src={str(utm):<22} | dev={dev:<26} | ref={ref}")


async def main():
    seeded_first = json.load(open(os.path.join(BASE_DIR, "seeded_first_comments.json"), encoding="utf-8"))
    seeded_sample = json.load(open(os.path.join(BASE_DIR, "seeded_sample_replies.json"), encoding="utf-8"))
    yt_meta = json.load(open(os.path.join(BASE_DIR, "uploaded_yt_shorts.json"), encoding="utf-8")).get("videos", {})

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
            tt_res = {"items": {}}

    print("=== VEO 3.1 TRI-PLATFORM LEADERBOARD (SHORT_050 – SHORT_059) ===")
    tt_items = tt_res.get("items", {})
    for sid, yt_id, ig_code, tt_id, slot_status, title in VEO31_SHORTS:
        yt_info = yt_meta.get(sid, {})
        yt_views = yt_res.get("public_shorts", {}).get(yt_id) or (
            f"Scheduled ({yt_info.get('schedule', slot_status)})" if "Scheduled" in slot_status else "0 views"
        )
        yt_c = "Pinned+Sample" if yt_info.get("prompt_seeded") else ("Queued" if "Scheduled" in slot_status else "LIVE")
        ig_views = ig_res.get(ig_code, {}).get("views", "0 views" if ig_code != "QUEUED" else "Queued")

        tt_entry = tt_items.get(tt_id)
        if tt_entry:
            if tt_entry.get("is_scheduled"):
                dt_str = datetime.fromtimestamp(tt_entry["schedule_time"]).strftime("%b %d @ %I:%M %p")
                tt_views = f"Scheduled ({dt_str})"
            else:
                tt_views = f"{tt_entry['plays']} views"
        else:
            tt_views = slot_status

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
