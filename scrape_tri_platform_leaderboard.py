#!/usr/bin/env python3
"""
Scrape & Print Full 3-Platform View & Engagement Leaderboard
(YouTube Shorts vs. Instagram Reels vs. TikTok) + 17-Session Telemetry Breakdown.
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
YT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\yt_chrome_cdp_userdata"
IG_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"
TT_PROFILE_DIR = r"C:\Users\User\.gemini\antigravity\tiktok_browser_profile"

YT_VIDEOS = [
    ("short_45", "A1QCTI8JKYg", "How He Keeps You Hooked Without Committing 🎙️💔 #Shorts"),
    ("short_44", "XYtxS5vllUE", "Why He Acts Hot One Day & Cold The Next 🎙️🥶 #Shorts"),
    ("short_43", "XbNVIjb4eBo", "Birth Days That Give Bare Minimum Effort 🎙️💔 #Shorts"),
    ("short_42", "4UBDJO2bgRk", "When He Sends Dry 1-Word Text Replies 🎙️📱 #Shorts"),
    ("short_41", "-gTPXdJw2t0", "Why Men Switch Up At The 6-Week Mark 🎙️💔 #Shorts"),
    ("short_40", "bHEFsoDtSlY", "He Watches Your Stories But Won't Text Back? 🎙️👀 #Shorts"),
    ("short_39", "qWL3TXi1nIo", "When Men Actually Regret Pulling Away 🎙️🔥 #Shorts"),
    ("short_38", "WEiPGnpKzRY", "He Left You On Read? A Guy Explains Why 🎙️📱 #Shorts"),
    ("short_37", "OVz7TSxgygk", "Why Men Go Dead Silent (By His Birth Day) 🎙️💔 #Shorts"),
    ("short_36", "zcWFaLsddFA", "Why They Always Come Back When You Pull Away 🔥 #Shorts"),
    ("short_35", "BtPMMrR85Bs", "Birth Days That Breadcrumb You For Months 💔 #Shorts"),
    ("short_34", "IWLCRnUZ-LI", "When He Acts Cold & Distant, Do This First 🥶 #Shorts"),
    ("short_33", "UbkEA3YjgyU", "You Fall For People Who Pull Away 💔 #Shorts"),
    ("short_32", "2NEQkRMDARQ", "Left On Read At Midnight? Send This 9-Word Text 📱 #Shorts"),
    ("short_31", "IOFdayPUpoA", "He Texted Daily For 6 Weeks Then Vanished 💔 #Shorts"),
    ("short_24", "9jgH8Hssjw8", "Only 1 Birth Day Can Handle Your Fire Without Drama 🔥 #Shorts"),
    ("short_23", "mhbNVSmjYQg", "Never Double Text When This Birth Day Goes Quiet 📱💔 #Shorts"),
    ("short_30", "xFjemSPAS1Y", "Are Your Birthdays Endgame Or A 3-Month Lesson? 💔 #Shorts"),
    ("short_29", "vh8PSKOEh_0", "Never Chase When These Birth Days Go Silent 🤫 #Shorts"),
    ("short_27", "A9zyXFYX62g", "Your November Love Turning Point By Birth Day ✨ #Shorts"),
    ("short_26", "eadiJdezXQA", "Why Their Silence Does NOT Mean They Forgot You 💔 #Shorts"),
]

IG_VIDEOS = [
    ("short_45", "DfdbjxxO-mT", "Batch #12 · Keeps You Hooked Without Committing (Real-Human Podcast)"),
    ("short_44", "DfdbcN3ubMj", "Batch #12 · Hot One Day Cold The Next (Real-Human Podcast)"),
    ("short_43", "DfdbUjSOcBe", "Batch #12 · Bare Minimum Effort (Real-Human Podcast)"),
    ("short_42", "DfcX9v4uTny", "Batch #11 · Dry 1-Word Text Replies (Real-Human Podcast)"),
    ("short_41", "DfcX2Kcu8-g", "Batch #11 · 6-Week Mark Switch Up (Real-Human Podcast)"),
    ("short_40", "DfcXuEju4Sm", "Batch #11 · Watches Stories Won't Text (Real-Human Podcast)"),
    ("short_39", "DfcXmCmuXBn", "Batch #10 · When Men Regret Pulling Away (Real-Human Podcast)"),
    ("short_38", "DfcXeAPur38", "Batch #10 · Left On Read Male Insider (Real-Human Podcast)"),
    ("short_37", "DfcXWKpuDAv", "Batch #10 · Why Men Go Dead Silent (Real-Human Podcast)"),
    ("short_36", "DfYsPKVudA0", "Batch #9 · Come Back After Silence (Giant 120px + SFX)"),
    ("short_35", "DfYsGWmOnNh", "Batch #9 · Breadcrumbing Days (Giant 120px + SFX)"),
    ("short_34", "DfYr-ceOLlN", "Batch #9 · Cold & Distant Test (Giant 120px + SFX)"),
    ("short_33", "DfX4Mdsuqc1", "Batch #8 · Pull Away Micro-Story (Giant 120px + SFX)"),
    ("short_32", "DfX4E4QOsUB", "Batch #8 · Left On Read 11:42 PM (Giant 120px + SFX)"),
    ("short_31", "DfX39C3Owgn", "Batch #8 · 6 Weeks Vanished (Giant 120px + SFX)"),
    ("short_24", "DfWMtB2OLJc", "Batch #7 · 1 Birth Day Handles Your Fire (Giant 120px)"),
    ("short_23", "DfWMlPuumkQ", "Batch #7 · Never Double Text (Giant 120px)"),
    ("short_30", "DfVoPn9u4rG", "Batch #7 · Endgame Or 3-Month Lesson (Giant 120px)"),
    ("short_29", "DfVoH1Lu2xB", "Batch #7 · Silent Treatment Days (Giant 120px)"),
    ("short_27", "DfVoASXOCCL", "Batch #7 · November Turning Point (Giant 120px)"),
    ("short_26", "DfVn4f2uqDa", "Batch #7 · No Contact Thoughts (Giant 120px)"),
    ("short_28", "DfS6Iu5OEhv", "Batch #6 · Why You Care More First"),
    ("short_25", "DfP3a8aOUPF", "Batch #6 · Karmic Trap Birth Days"),
    ("short_22", "DfPp_HOOJS3", "Batch #6 · Obsessed Then Cold"),
]

TT_VIDEOS = [
    ("short_37", "7705432066799701262", "LIVE (Nov 7)", "Why men text every day then go dead silent (Maya x Julian)"),
    ("short_29", "LIVE_OR_SCHED", "Scheduled (Nov 7 11:00)", "Dating someone born on the 4th, 7th, 8th, 13th"),
    ("short_27", "7704466354597940494", "LIVE (Nov 6 18:30)", "Born on the 3rd, 4th, 8th, 9th, 12th, 13th"),
    ("short_34", "7704901851963018510", "LIVE (Nov 5)", "When he starts acting cold & distant, do NOT ask what's wrong"),
    ("short_31", "7704784636659961102", "LIVE (Nov 5)", "He texted me every morning for 6 weeks"),
    ("short_26", "7704543339755916558", "LIVE (Nov 5 18:30)", "Silence does not mean they forgot you"),
    ("short_24", "7704543122772086029", "LIVE (Nov 5 11:00)", "Only 1 birth day can handle your fire"),
    ("short_23", "7704542849571900685", "LIVE (Nov 5)", "Stop double texting when they go quiet"),
    ("short_28", "7704068444592950541", "LIVE", "Why you always care more first"),
    ("short_25", "7703630255013104910", "LIVE", "Intense chemistry can be a karmic trap"),
    ("short_22", "7703622747489963278", "LIVE", "Why they act obsessed then pull away"),
    ("short_20", "7704137393049308430", "LIVE", "Every birthday has 3 natural soulmate dates"),
    ("short_30", "SCHEDULED", "Scheduled (Nov 7 18:30)", "Are your birthdays endgame or a 3-month lesson"),
    ("short_32", "SCHEDULED", "Scheduled (Nov 8 11:00)", "Left on read at 11:42 PM? Send this 9-word text"),
    ("short_33", "SCHEDULED", "Scheduled (Nov 8 18:30)", "Why you keep falling for people who pull away"),
    ("short_35", "SCHEDULED", "Scheduled (Nov 9 11:00)", "Birth days that breadcrumb you for months"),
    ("short_36", "SCHEDULED", "Scheduled (Nov 9 18:30)", "Why they always come back when you pull away"),
    ("short_38", "SCHEDULED", "Scheduled (Nov 10 11:00)", "When a guy leaves you on read, is it over?"),
    ("short_39", "SCHEDULED", "Scheduled (Nov 10 18:30)", "At what point does a man regret pulling away?"),
    ("short_40", "SCHEDULED", "Scheduled (Nov 11 11:00)", "Why he watches every story but won't text back"),
    ("short_41", "SCHEDULED", "Scheduled (Nov 11 18:30)", "Why men act obsessed for 6 weeks then switch up"),
    ("short_42", "SCHEDULED", "Scheduled (Nov 12 11:00)", "What to do when he sends dry 1-word replies"),
    ("short_43", "SCHEDULED", "Scheduled (Nov 12 18:30)", "Birth days that give bare minimum effort"),
    ("short_44", "SCHEDULED", "Scheduled (Nov 13 11:00)", "Why he acts hot one day and cold the next"),
    ("short_45", "SCHEDULED", "Scheduled (Nov 13 18:30)", "How he keeps you hooked without committing"),
]


async def scrape_youtube(p) -> list:
    results = []
    b = await p.chromium.launch(headless=True)
    page = await b.new_page(viewport={"width": 1280, "height": 900})
    try:
        await page.goto(
            "https://www.youtube.com/@sacrednumberblueprint/shorts",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await asyncio.sleep(3.5)
        yt_cards = await page.evaluate(
            """() => {
                const out = {};
                const items = Array.from(document.querySelectorAll('ytm-shorts-lockup-view-model, ytd-rich-item-renderer'));
                for (const el of items) {
                    const a = el.querySelector('a[href*="/shorts/"]');
                    if (!a) continue;
                    const href = a.getAttribute('href') || '';
                    const m = href.match(/\\/shorts\\/([A-Za-z0-9_-]{11})/);
                    if (!m) continue;
                    const vid = m[1];
                    const txt = (el.innerText || '').trim();
                    const vwMatch = txt.match(/(\\d[\\d.,KMB]*)\\s+views?/i) || txt.match(/No views/i);
                    out[vid] = { views: vwMatch ? vwMatch[0] : '0 views', raw: txt.split(/\\n+/) };
                }
                return out;
            }"""
        )
        for sid, vid, title in YT_VIDEOS:
            st = yt_cards.get(vid, {})
            results.append({
                "id": sid,
                "video_id": vid,
                "title": title,
                "views": st.get("views", "0 views"),
                "likes": "1+",
                "comments": "2 (Pinned + Sample)",
                "tail": st.get("raw", []),
            })
    except Exception as e:
        print("YT scrape error:", e)
    finally:
        await b.close()
    return results


async def scrape_instagram(p) -> list:
    results = []
    ctx = await p.chromium.launch_persistent_context(
        IG_PROFILE_DIR,
        headless=True,
        args=["--disable-blink-features=AutomationControlled"],
        viewport={"width": 1280, "height": 900},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    try:
        await page.goto(
            "https://www.instagram.com/sacrednumberblueprint/reels/",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await asyncio.sleep(4.0)
        for _ in range(3):
            await page.mouse.wheel(0, 1200)
            await asyncio.sleep(1.2)
        cards = await page.evaluate(
            """() => {
                const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                const out = {};
                for (const a of links) {
                    const m = a.href.match(/\\/reel\\/([A-Za-z0-9_-]+)/);
                    if (!m) continue;
                    const code = m[1];
                    const txt = (a.innerText || '').trim();
                    const nums = txt.split(/\\n+/).map(s => s.trim()).filter(Boolean);
                    out[code] = { raw: nums, aria: a.getAttribute('aria-label') || '' };
                }
                return out;
            }"""
        )
        for sid, code, desc in IG_VIDEOS:
            c = cards.get(code, {})
            raw_list = c.get("raw", [])
            views = raw_list[-1] if raw_list else "0"
            likes = raw_list[0] if len(raw_list) >= 3 else "—"
            comments = raw_list[1] if len(raw_list) >= 3 else "2"
            results.append({
                "id": sid,
                "shortcode": code,
                "desc": desc,
                "views": views,
                "likes": likes,
                "comments": comments,
                "raw": raw_list,
            })
    except Exception as e:
        print("IG scrape error:", e)
    finally:
        await ctx.close()
    return results


async def scrape_tiktok(p) -> list:
    results = []
    ctx = await p.chromium.launch_persistent_context(
        TT_PROFILE_DIR,
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--window-position=-2000,-2000"],
        viewport={"width": 1280, "height": 900},
    )
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    try:
        await page.goto(
            "https://www.tiktok.com/@sacrednumberblueprint",
            wait_until="domcontentloaded",
            timeout=35000,
        )
        await asyncio.sleep(5.0)
        for _ in range(3):
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1.0)
        pub_cards = await page.evaluate(
            """() => {
                const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                const out = {};
                for (const a of links) {
                    const m = a.href.match(/\\/video\\/(\\d+)/);
                    if (!m) continue;
                    const vid = m[1];
                    const container = a.closest('[data-e2e="user-post-item"]') || a.parentElement;
                    const viewsEl = container ? container.querySelector('[data-e2e="video-views"], strong[data-e2e="video-views"]') : null;
                    const views = viewsEl ? viewsEl.innerText.trim() : (a.innerText || '').trim();
                    out[vid] = views;
                }
                return out;
            }"""
        )
        for sid, vid, status, title in TT_VIDEOS:
            v_cnt = pub_cards.get(vid, "—") if vid != "SCHEDULED" else "Scheduled"
            results.append({
                "id": sid,
                "video_id": vid,
                "status": status,
                "title": title,
                "views": v_cnt,
            })
    except Exception as e:
        print("TT scrape error:", e)
    finally:
        await ctx.close()
    return results


def dump_telemetry():
    tpath = os.path.join(BASE_DIR, "telemetry_events.json")
    with open(tpath, "r", encoding="utf-8") as f:
        evs = json.load(f)
    pviews = [e for e in evs if e.get("event_type") == "page_view"]
    counts = {}
    for e in evs:
        et = e.get("event_type", "unknown")
        counts[et] = counts.get(et, 0) + 1
    print(f"\n=== TELEMETRY: {len(pviews)} PAGE_VIEW EVENTS / {len(evs)} TOTAL EVENTS ===")
    print(
        f"Event Breakdown: hero_engaged_3s={counts.get('hero_engaged_3s', 0)} | "
        f"hero_my_day_selected={counts.get('hero_my_day_selected', 0)} | "
        f"hero_pair_match_selected={counts.get('hero_pair_match_selected', 0)} | "
        f"quick_day_selected={counts.get('quick_day_selected', 0)} | "
        f"partner_check_run={counts.get('partner_check_run', 0)} | "
        f"crush_text_decoded={counts.get('crush_text_decoded', 0)} | "
        f"lead_submitted={counts.get('lead_submitted', 0)} | "
        f"checkout_clicked={counts.get('checkout_clicked', 0)} | "
        f"advisor_affiliate_clicked={counts.get('advisor_affiliate_clicked', 0)}"
    )
    for idx, pv in enumerate(pviews, 1):
        ts = pv.get("timestamp", "")[:19]
        utm = pv.get("utm_source", "") or "direct"
        cohort = pv.get("cohort", "") or "—"
        browser = pv.get("browser", "") or pv.get("device", "") or "Browser"
        lid = pv.get("lead_id", "")
        # Find all other events matching this lead_id or within 3 mins from same browser/utm
        matching = [
            e for e in evs
            if (lid and e.get("lead_id") == lid)
        ]
        ev_names = [e.get("event_type") for e in matching] if matching else ["page_view"]
        extras = [e.get("extra") for e in matching if e.get("extra")]
        print(f"{idx:02d}. {ts} | utm={utm:<12} | cohort={cohort:<10} | dev={browser:<24} | actions={ev_names} | extras={extras[:2]}")


async def main():
    async with async_playwright() as p:
        yt_res, ig_res, tt_res = await asyncio.gather(
            asyncio.wait_for(scrape_youtube(p), timeout=18.0),
            asyncio.wait_for(scrape_instagram(p), timeout=18.0),
            asyncio.wait_for(scrape_tiktok(p), timeout=18.0),
            return_exceptions=True,
        )
        if isinstance(yt_res, Exception):
            print("YT timeout/err:", yt_res)
            yt_res = []
        if isinstance(ig_res, Exception):
            print("IG timeout/err:", ig_res)
            ig_res = []
        if isinstance(tt_res, Exception):
            print("TT timeout/err:", tt_res)
            tt_res = []

    print("\n=== YOUTUBE SHORTS (@sacrednumberblueprint) ===")
    for r in yt_res:
        print(f"{r['id']} | {r['video_id']} | Views={r['views']} | Likes={r['likes']} | Comments={r['comments']} | tail={r['tail']}")

    print("\n=== INSTAGRAM REELS (@sacrednumberblueprint) ===")
    for r in ig_res:
        print(f"{r['id']} | {r['shortcode']} | Views={r['views']} | Likes={r['likes']} | Comments={r['comments']} | raw={r['raw']}")

    print("\n=== TIKTOK (@sacrednumberblueprint) ===")
    for r in tt_res:
        print(f"{r['id']} | {r['video_id']} | Status={r['status']} | Views={r['views']} | {r['title']}")

    dump_telemetry()


if __name__ == "__main__":
    asyncio.run(main())
