#!/usr/bin/env python3
"""
=============================================================================
SOVEREIGN 5-SYSTEM · REAL-TIME LEAD CAPTURE & 3-PART LUXURY EMAIL SEQUENCE
lead_capture_worker.py
-----------------------------------------------------------------------------
1. Captures leads submitted from https://rj2point0.github.io/sovereign-5-system/
   via public cloud relay (ntfy.sh/sovereign_5_leads_mvv_991214754) and local
   HTTP webhook (http://127.0.0.1:8788/webhook).
2. Computes exact 5-System Numerology numbers (matching engine.js 100%):
   - Proper compound reduction cap=52 (e.g. 99 -> 18/9)
   - Strict system count vs. system list consistency (len(systems) <= count)
   - Clean Vedic Moolank formatting (e.g. '7 · Ketu (South Node)')
3. Logs every lead permanently to:
   - G:\\My Drive\\5_System_Numerology_MVP\\leads_captured.csv
   - c:\\Users\\User\\5numsystem\\leads_captured.csv
   - G:\\My Drive\\MVV_Memory_Vault\\03-Projects\\Leads_Captured_Dashboard.md
   - Supabase PostgreSQL (`public.numerology_leads`)
4. Runs an automated 3-part luxury HTML email sequence via Google Workspace SMTP
   (Sacred Number Blueprint <adamvega@megavegaventures.com>):
   - Email #1 (Instant): 5-System Overlap Teaser + Single-System Friction Alert
     + Locked Systems II/III/V Curiosity Gap + 20-Page Value Stack
   - Email #2 (24h later): Missing Chinese Lo Shu Grid Numbers & Relationship /
     Wealth Engine (#2 Anchor) Follow-Up
   - Email #3 (48h later): Active 52-Day Rosicrucian Cycle & Somatic Nervous
     System Alignment Follow-Up
=============================================================================
"""

import argparse
import csv
import html
import json
import math
import os
import re
import smtplib
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# -----------------------------------------------------------------------------
# CONFIGURATION & PATHS
# -----------------------------------------------------------------------------
NTFY_TOPIC = "sovereign_5_leads_mvv_991214754"
NTFY_POLL_URL = f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1&since=48h"

SUPABASE_DB_URL = "postgresql://postgres.psfwllfxejfbtaqhwhtt:b5oJO3pf8y6QdSYf@aws-1-us-west-2.pooler.supabase.com:5432/postgres"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "adamvega@megavegaventures.com"
SMTP_PASS = "msct rkqt xcwb inma"
SENDER_DISPLAY = "Sacred Number Blueprint <adamvega@megavegaventures.com>"

STRIPE_BASE_URL = "https://buy.stripe.com/6oU7sLek90MdbVechV38401"
STRIPE_BUMP_URL = "https://buy.stripe.com/eVq28r2Br9iJe3mbdR38402"
BASE_FUNNEL_URL = "https://blueprint.megavegaventures.com/"
APP_BASE_URL = BASE_FUNNEL_URL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CSV_PATH = os.path.join(BASE_DIR, "leads_captured.csv")
GDRIVE_CSV_PATH = r"G:\My Drive\5_System_Numerology_MVP\leads_captured.csv"
OBSIDIAN_DASHBOARD_PATH = r"G:\My Drive\MVV_Memory_Vault\03-Projects\Leads_Captured_Dashboard.md"
PROCESSED_LEADS_PATH = os.path.join(BASE_DIR, "processed_leads_state.json")
TELEMETRY_STATE_PATH = os.path.join(BASE_DIR, "telemetry_events.json")
GDRIVE_TELEMETRY_PATH = r"G:\My Drive\5_System_Numerology_MVP\telemetry_events.json"

CSV_COLUMNS = [
    "timestamp",
    "name",
    "dob",
    "email",
    "lang",
    "source_attribution",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "cohort",
    "top_3_overlap_numbers",
    "life_path",
    "vedic_moolank",
    "chaldean_name",
    "email_sent",
    "email_1_sent_at",
    "email_2_sent_at",
    "email_3_sent_at",
]

# -----------------------------------------------------------------------------
# EXACT 5-SYSTEM NUMEROLOGY ENGINE (MATCHES engine.js 100%)
# -----------------------------------------------------------------------------
PYTHAGOREAN_MAP = {ch: (i % 9) + 1 for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CHALDEAN_MAP = {}
for val, letters in [
    (1, "AIJQY"), (2, "BKR"), (3, "CGLS"), (4, "DMT"),
    (5, "EHNX"), (6, "UVW"), (7, "OZ"), (8, "FP")
]:
    for ch in letters:
        CHALDEAN_MAP[ch] = val

VOWELS = set("AEIOU")

ARCHETYPES_EN = {
    1: {
        "name": "The Sovereign Pioneer",
        "keywords": "Command · Originality · Will",
        "summary": "You are wired to initiate, lead from the front, and carve original paths where consensus hesitates.",
        "single_trap": "pushing in isolation and carrying every burden on your own shoulders",
    },
    2: {
        "name": "The Diplomatic Oracle",
        "keywords": "Intuition · Resonance · Alliance",
        "summary": "You perceive the unspoken currents between people, turning subtle emotional intelligence into strategic harmony.",
        "single_trap": "over-adapting to others' emotions and second-guessing your own authority",
    },
    3: {
        "name": "The Magnetic Catalyst",
        "keywords": "Expression · Synthesis · Charisma",
        "summary": "Your voice and creative fire translate complex truths into magnetic ideas that move rooms and markets.",
        "single_trap": "scattering creative energy across too many fronts without structural leverage",
    },
    4: {
        "name": "The Master Architect",
        "keywords": "Structure · Endurance · Foundation",
        "summary": "You turn abstract vision into permanent, load-bearing systems, wealth structures, and unshakable order.",
        "single_trap": "overworking inside rigid systems while starving your higher intuitive strategy",
    },
    5: {
        "name": "The Mercurial Alchemist",
        "keywords": "Velocity · Freedom · Pivot",
        "summary": "You thrive at the intersection of rapid change, sensory mastery, and high-leverage adaptability.",
        "single_trap": "restless pivoting and nervous system overstimulation without an anchor",
    },
    6: {
        "name": "The Sovereign Guardian",
        "keywords": "Magnetism · Sanctuary · Devotion",
        "summary": "You command through beauty, loyalty, and protective stewardship over your family, capital, and legacy.",
        "single_trap": "over-extending yourself as a caretaker and harmonizer at the expense of your sovereign path",
    },
    7: {
        "name": "The Mystic Strategist",
        "keywords": "Pattern Analysis · Sovereignty · Depth",
        "summary": "You see beneath surface noise to decode the hidden mathematical and psychological laws governing outcomes.",
        "single_trap": "retreating into analysis paralysis when your wealth engine isn't activated",
    },
    8: {
        "name": "The Executive Magnate",
        "keywords": "Capital · Authority · Scale",
        "summary": "You are built for high-stakes material execution, asymmetric wealth creation, and institutional command.",
        "single_trap": "riding feast-or-famine material cycles by forcing outcomes through sheer willpower",
    },
    9: {
        "name": "The Sage-Warrior",
        "keywords": "Mastery · Completion · Legacy",
        "summary": "You synthesize the wisdom of all preceding numbers into panoramic vision, decisive action, and lasting impact.",
        "single_trap": "carrying karmic weight for others while delaying your own sovereign mission",
    },
}

VEDIC_PLANETS = {
    1: "Surya (Sun)",
    2: "Chandra (Moon)",
    3: "Guru (Jupiter)",
    4: "Rahu (North Node)",
    5: "Budha (Mercury)",
    6: "Shukra (Venus)",
    7: "Ketu (South Node)",
    8: "Shani (Saturn)",
    9: "Mangala (Mars)",
}

ELEMENTS = {
    "Water": [1],
    "Earth": [2, 5, 8],
    "Wood": [3, 4],
    "Metal": [6, 7],
    "Fire": [9],
}
ELEMENT_ORDER = ["Earth", "Metal", "Wood", "Water", "Fire"]
SYSTEM_ORDER = ["Pythagorean", "Chaldean", "Kabbalistic", "Vedic", "Lo Shu"]

ROSICRUCIAN_CYCLES = [
    {"n": 1, "name": "The Solar Period", "planet": "Sun", "glyph": "☉", "theme": "Promotion, High Visibility & Leadership Seek"},
    {"n": 2, "name": "The Lunar Period", "planet": "Moon", "glyph": "☽", "theme": "Travel, Short-Term Pivots & Fluid Calibration"},
    {"n": 3, "name": "The Martial Period", "planet": "Mars", "glyph": "♂", "theme": "Aggressive Action, High-Variance Pushes & Competition"},
    {"n": 4, "name": "The Mercurial Period", "planet": "Mercury", "glyph": "☿", "theme": "Deep Analysis, Systems Building & Intellectual Edge"},
    {"n": 5, "name": "The Jupiterian Period", "planet": "Jupiter", "glyph": "♃", "theme": "Maximum Wealth Expansion, High-Stakes Execution & Scaling"},
    {"n": 6, "name": "The Venusian Period", "planet": "Venus", "glyph": "♀", "theme": "Social Magnetism, Attraction, Luxury & Partnerships"},
    {"n": 7, "name": "The Saturnian Period", "planet": "Saturn", "glyph": "♄", "theme": "Capital Preservation, Tightening Ranges, Pruning & Vault Defense"},
]


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(int(n))))


def reduce_num(n: int) -> int:
    x = abs(int(n))
    while x > 9:
        x = digit_sum(x)
    return x


def compound_of(n: int, cap: int = 52) -> int:
    c = abs(int(n))
    while c > cap:
        c = digit_sum(c)
    return c


def make_num(raw: int, cap: int = 52) -> Dict[str, Any]:
    comp = compound_of(raw, cap)
    val = reduce_num(raw)
    return {
        "raw": raw,
        "compound": comp,
        "value": val,
        "display": f"{comp}/{val}" if comp > 9 else str(val),
    }


def normalize_name(s: str) -> str:
    nfd = unicodedata.normalize("NFD", str(s or ""))
    clean = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    clean = re.sub(r"[^A-Z\s'-]", " ", clean.upper())
    return re.sub(r"\s+", " ", clean).strip()


def only_letters(s: str) -> str:
    return re.sub(r"[^A-Z]", "", str(s or "").upper())


def normalize_dob(dob_str: str) -> str:
    """Converts MM/DD/YYYY or YYYY-MM-DD into standard YYYY-MM-DD."""
    s = str(dob_str or "").strip()
    m_iso = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m_iso:
        return f"{int(m_iso.group(1)):04d}-{int(m_iso.group(2)):02d}-{int(m_iso.group(3)):02d}"
    m_us = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", s)
    if m_us:
        return f"{int(m_us.group(3)):04d}-{int(m_us.group(1)):02d}-{int(m_us.group(2)):02d}"
    return s


def compute_active_rosicrucian_cycle(m: int, d: int, now_dt: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculates the current 52-day Rosicrucian planetary period."""
    t = now_dt or datetime.now(timezone.utc)
    today_date = datetime(t.year, t.month, t.day, tzinfo=timezone.utc)

    def bday_in_year(yr: int) -> datetime:
        if m == 2 and d == 29 and not (yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)):
            return datetime(yr, 2, 28, tzinfo=timezone.utc)
        return datetime(yr, m, d, tzinfo=timezone.utc)

    start = bday_in_year(today_date.year)
    if start > today_date:
        start = bday_in_year(today_date.year - 1)
    nxt = bday_in_year(start.year + 1)
    year_len = max(1, (nxt - start).days)
    day_of_year = (today_date - start).days

    active_idx = 6
    days_rem = 1
    for i in range(7):
        s_off = math.floor(i * year_len / 7.0)
        e_off = (year_len - 1) if i == 6 else (math.floor((i + 1) * year_len / 7.0) - 1)
        if s_off <= day_of_year <= e_off:
            active_idx = i
            days_rem = (e_off - day_of_year) + 1
            break

    cyc = dict(ROSICRUCIAN_CYCLES[active_idx])
    cyc["days_remaining"] = days_rem
    return cyc


def calculate_5_systems(full_name: str, dob_str: str) -> Dict[str, Any]:
    """Exact Python implementation of engine.js `calculate()`."""
    iso_dob = normalize_dob(dob_str)
    y, m, d = [int(x) for x in iso_dob.split("-")]
    compact = f"{y:04d}{m:02d}{d:02d}"

    norm = normalize_name(full_name)
    words = [only_letters(w) for w in norm.split(" ") if only_letters(w)]
    first_word = words[0] if words else ""
    last_words = "".join(words[1:]) if len(words) > 1 else ""
    all_letters = "".join(words)

    # 1. Pythagorean (compound cap=52 so 99 reduces to 18/9)
    lp = make_num(reduce_num(y) + reduce_num(m) + reduce_num(d), 52)
    expr = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters), 52)
    soul = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters if ch in VOWELS), 52)
    pers = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters if ch not in VOWELS), 52)
    first_cons = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in first_word if ch not in VOWELS), 52)

    # 2. Chaldean
    chal_first = make_num(sum(CHALDEAN_MAP.get(ch, 0) for ch in first_word), 52)
    chal_last = make_num(sum(CHALDEAN_MAP.get(ch, 0) for ch in last_words), 52)
    chal_total = make_num(sum(CHALDEAN_MAP.get(ch, 0) for ch in all_letters), 52)

    # 3. Kabbalistic
    kab_list = [lp["value"], expr["value"], chal_total["value"], soul["value"]]
    if chal_last["value"]:
        kab_list.append(chal_last["value"])
    kab_nums = set(v for v in kab_list if 1 <= v <= 9)

    # 4. Vedic
    moolank_val = reduce_num(d)
    bhagyank_raw = digit_sum(int(compact))
    bhagyank_val = reduce_num(bhagyank_raw)
    namank_val = chal_total["value"]

    # 5. Lo Shu
    extra = [v for v in (lp["value"], expr["value"], chal_total["value"]) if v > 0]
    lo_source = compact + "".join(str(v) for v in extra)
    counts = {n: 0 for n in range(1, 10)}
    for ch in lo_source:
        n = int(ch)
        if 1 <= n <= 9:
            counts[n] += 1

    missing_loshu = [n for n in range(1, 10) if counts[n] == 0]
    el_scores = {el: sum(counts[n] for n in nums) for el, nums in ELEMENTS.items()}
    max_el = max(el_scores.values())
    dom_element = next(el for el in ELEMENT_ORDER if el_scores[el] == max_el)
    dom_number = sorted(ELEMENTS[dom_element], key=lambda n: (-counts[n], n))[0]

    # 6. Master Overlap Sources
    sources = [
        ("lifePath", "Life Path", "Pythagorean", lp["value"]),
        ("expression", "Expression / Destiny", "Pythagorean", expr["value"]),
        ("soulUrge", "Soul Urge (Heart's Desire)", "Pythagorean", soul["value"]),
        ("firstNameConsonants", "First-Name Consonants", "Pythagorean", first_cons["value"]),
        ("chaldeanName", "Chaldean Full Name", "Chaldean", chal_total["value"]),
        ("moolank", "Moolank (Driver)", "Vedic", moolank_val),
        ("bhagyank", "Bhagyank (Conductor)", "Vedic", bhagyank_val),
        ("namank", "Namank (Name Vibration)", "Vedic", namank_val),
        ("loShuDominant", f"Lo Shu Dominant ({dom_element})", "Lo Shu", dom_number),
    ]
    if chal_last["value"]:
        sources.append(("chaldeanSurname", "Chaldean Surname Vibration", "Chaldean", chal_last["value"]))
    if m:
        sources.append(("birthMonth", "Birth Month Vibration", "Pythagorean", reduce_num(m)))
    if counts[8] > 0:
        sources.append(("loShuWealthEight", "Lo Shu Earth Wealth (8 - Fa)", "Lo Shu", 8))

    cons_counts: Dict[int, int] = {}
    for ch in all_letters:
        if ch not in VOWELS:
            v = reduce_num(PYTHAGOREAN_MAP.get(ch, 0))
            cons_counts[v] = cons_counts.get(v, 0) + 1
    for n_val in sorted(cons_counts.keys()):
        if cons_counts[n_val] >= 2:
            sources.append((f"consonantBase{n_val}", f"Consonant Structural Base ({n_val})", "Pythagorean", n_val))

    if cons_counts.get(4, 0) >= 2 or "ADAM" in first_word:
        sources.append(("kabbalahChesed", "Kabbalistic Abundance Base (Chesed / Dalet-Mem)", "Kabbalistic", 4))
        kab_nums.add(4)

    sources.append(("baguaWealthCorner", "Feng Shui Wealth Corner (Southeast Xun)", "Lo Shu", 4))

    filtered = [s for s in sources if 1 <= s[3] <= 9]
    tally = {}
    for n in range(1, 10):
        hits = [s for s in filtered if s[3] == n]
        sys_set = set(h[2] for h in hits)
        # Only attribute a secondary Kabbalistic Sephirah system when hits has multiple entries
        # so len(systems) NEVER exceeds count (len(hits)).
        if n in kab_nums and len(hits) > len(sys_set):
            sys_set.add("Kabbalistic")
        first_idx = next((idx for idx, s in enumerate(filtered) if s[3] == n), 99)
        tally[n] = {
            "number": n,
            "archetype": ARCHETYPES_EN[n]["name"],
            "keywords": ARCHETYPES_EN[n]["keywords"],
            "summary": ARCHETYPES_EN[n]["summary"],
            "count": len(hits),
            "systems": [s for s in SYSTEM_ORDER if s in sys_set],
            "kabbalahActive": 1 if n in kab_nums else 0,
            "sources": [h[1] for h in hits],
            "firstIndex": first_idx,
            "loShuCount": counts[n],
        }

    ranking = sorted(
        tally.values(),
        key=lambda a: (-a["count"], -len(a["systems"]), -a["kabbalahActive"], -a["loShuCount"], a["firstIndex"], a["number"])
    )
    anchors = ranking[:3]
    active_cycle = compute_active_rosicrucian_cycle(m, d)

    return {
        "name": " ".join(w.capitalize() for w in full_name.strip().split()),
        "dob": iso_dob,
        "top_3_overlap_numbers": ", ".join(str(a["number"]) for a in anchors),
        "anchors": anchors,
        "life_path": lp["display"],
        "life_path_val": lp["value"],
        "life_path_archetype": ARCHETYPES_EN[lp["value"]]["name"],
        "life_path_trap": ARCHETYPES_EN[lp["value"]]["single_trap"],
        "expression": expr["display"],
        "soul_urge": soul["display"],
        "vedic_moolank": f"{moolank_val} · {VEDIC_PLANETS.get(moolank_val, 'Surya (Sun)')}",
        "vedic_bhagyank": f"{bhagyank_val} · {VEDIC_PLANETS.get(bhagyank_val, 'Surya (Sun)')}",
        "chaldean_name": chal_total["display"],
        "dominant_element": f"{dom_element} (#{dom_number})",
        "missing_loshu": missing_loshu,
        "active_cycle_name": active_cycle["name"],
        "active_cycle_planet": active_cycle["planet"],
        "active_cycle_glyph": active_cycle["glyph"],
        "active_cycle_theme": active_cycle["theme"],
        "active_cycle_days_remaining": active_cycle["days_remaining"],
        "total_sources": len(filtered),
    }


def build_teaser_deep_link(name: str, dob: str, email_addr: str) -> str:
    """
    Constructs the exact cross-browser session-restoring Teaser URL:
    https://rj2point0.github.io/sovereign-5-system/?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=getshoes7%40gmail.com
    """
    query = urllib.parse.urlencode(
        [
            ("view", "teaser"),
            ("name", name),
            ("dob", dob),
            ("email", email_addr),
        ]
    )
    return f"{APP_BASE_URL}?{query}"


# -----------------------------------------------------------------------------
# EMAIL #1 (INSTANT): 5-SYSTEM OVERLAP TEASER + FRICTION ALERT + VALUE STACK
# -----------------------------------------------------------------------------
def build_luxury_followup_email(lead: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (subject, plain_text, html_body) for Email #1 (Instant Teaser)."""
    name = lead["name"]
    first_name = name.split()[0] if name else "Friend"
    dob = lead["dob"]
    email_addr = lead["email"]
    calc = lead["calc"]
    anchors = calc["anchors"]
    a1, a2, a3 = anchors[0], anchors[1], anchors[2]

    try:
        dt_obj = datetime.strptime(dob, "%Y-%m-%d")
        dob_formatted = dt_obj.strftime("%B %d, %Y")
    except Exception:
        dob_formatted = dob

    teaser_url = build_teaser_deep_link(name, dob, email_addr)
    stripe_url = f"{STRIPE_BASE_URL}?prefilled_email={urllib.parse.quote(email_addr)}"

    subject = f"✦ Your 5-System Numerology Code: Master Overlap #{a1['number']} ({a1['archetype']})"

    lp_disp = calc["life_path"]
    lp_val = calc.get("life_path_val", reduce_num(int(lp_disp.split("/")[-1])))
    lp_arch = calc.get("life_path_archetype", ARCHETYPES_EN.get(lp_val, ARCHETYPES_EN[6])["name"])
    lp_trap = calc.get("life_path_trap", ARCHETYPES_EN.get(lp_val, ARCHETYPES_EN[6])["single_trap"])

    if lp_val != a1["number"]:
        friction_headline = f"Western Life Path {lp_disp} vs. Master Overlap #{a1['number']}"
        friction_text = (
            f"Standard Western numerology apps only calculate your birth date, labeling you a "
            f"<strong>Life Path {html.escape(lp_disp)} ({html.escape(lp_arch)})</strong>—which pushes you toward "
            f"{html.escape(lp_trap)}. Yet when we cross-reference your full birth name and birth date across all 5 ancient "
            f"traditions, your true <strong>#1 Master Overlap Anchor is #{a1['number']} ({html.escape(a1['archetype'])})</strong> "
            f"({a1['count']}× across {len(a1['systems'])} systems). Living by your single-system Life Path creates invisible "
            f"friction against your true #{a1['number']} sovereign nature."
        )
    else:
        friction_headline = f"Single-System Life Path {lp_disp} vs. Your #2 Wealth Engine (#{a2['number']})"
        friction_text = (
            f"While Western numerology correctly identifies your primary #{a1['number']} ({html.escape(a1['archetype'])}) "
            f"frequency, relying on that single number alone leaves you stuck in {html.escape(lp_trap)}. Your real material "
            f"breakthrough requires activating your <strong>#2 Wealth &amp; Strategy Engine: Anchor #{a2['number']} "
            f"({html.escape(a2['archetype'])})</strong> ({a2['count']}× across {len(a2['systems'])} systems)."
        )

    a2_sys_label = f"{len(a2['systems'])} system" + ("s" if len(a2["systems"]) != 1 else "")
    a3_sys_label = f"{len(a3['systems'])} system" + ("s" if len(a3["systems"]) != 1 else "")

    plain_text = (
        f"SACRED NUMBER BLUEPRINT · THE SOVEREIGN 5-SYSTEM CODE\n"
        f"Decoded for {name} (Born {dob_formatted})\n"
        f"============================================================\n\n"
        f"{first_name}, we cross-referenced your full birth name and birth date across all 5 ancient mathematical traditions "
        f"(Pythagorean, Babylonian Chaldean, Kabbalistic Tree of Life, Vedic Planetary Council & Chinese Lo Shu).\n\n"
        f"YOUR #1 PRIMARY SIGNATURE ANCHOR: #{a1['number']} — {a1['archetype']}\n"
        f"Appeared {a1['count']} times across {len(a1['systems'])} of 5 ancient systems ({', '.join(a1['systems'])})\n"
        f"\"{a1['summary']}\"\n\n"
        f"⚠️ SINGLE-SYSTEM FRICTION ALERT ({friction_headline}):\n"
        f"Western Life Path {lp_disp} ({lp_arch}) only tells 20% of your code. Your true multi-system center of gravity "
        f"is #{a1['number']} ({a1['archetype']}), supported by:\n"
        f"• #2 WEALTH & STRATEGY ENGINE: Anchor #{a2['number']} · {a2['archetype']} ({a2['count']}× across {a2_sys_label}: {', '.join(a2['systems'])})\n"
        f"• #3 SANCTUARY & FOUNDATION: Anchor #{a3['number']} · {a3['archetype']} ({a3['count']}× across {a3_sys_label}: {', '.join(a3['systems'])})\n\n"
        f"YOUR 5-SYSTEM MATHEMATICAL SNAPSHOT:\n"
        f"• System I (Pythagorean Life Path): {calc['life_path']}\n"
        f"• System IV (Vedic Planetary Moolank): {calc['vedic_moolank']}\n"
        f"• System II (Babylonian Chaldean Compound Name): 🔒 Locked in Full 20-Page Dossier\n"
        f"• System III (Kabbalistic Tree of Life & Sephirot): 🔒 Locked in Full 20-Page Dossier\n"
        f"• System V (Chinese Lo Shu Grid & Missing Numbers): 🔒 Locked in Full 20-Page Dossier\n"
        f"• Active 52-Day Rosicrucian Planetary Cycle: 🔒 Locked in Full 20-Page Dossier\n\n"
        f"UNLOCK YOUR FULL 20-PAGE SOVEREIGN DOSSIER ($37):\n"
        f"{stripe_url}\n\n"
        f"RETURN TO YOUR INTERACTIVE 5-SYSTEM TEASER & WATCH VIDEO BRIEFING:\n"
        f"{teaser_url}\n\n"
        f"— Sacred Number Blueprint (@sacrednumberblueprint)\n"
    )

    a1_systems_badges = "".join(
        f'<span style="display:inline-block;margin:3px 4px;padding:4px 10px;border-radius:99px;'
        f'background:#1c1910;border:1px solid rgba(212,175,55,0.45);color:#F3E5AB;font-size:11px;'
        f'letter-spacing:1px;text-transform:uppercase;">{html.escape(s)}</span>'
        for s in a1["systems"]
    )

    preheader_text = (
        f"Your #1 Master Overlap Anchor is #{a1['number']} ({a1['archetype']}) across {len(a1['systems'])} systems — "
        f"see why your Western Life Path {lp_disp} only tells 20% of your code..."
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#0A0A0C;font-family:'Georgia',serif;color:#F5F5F7;">
  <!-- Hidden Preheader Snippet -->
  <div style="display:none;max-height:0px;overflow:hidden;mso-hide:all;font-size:1px;color:#0A0A0C;line-height:1px;opacity:0;">
    {html.escape(preheader_text)}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;
  </div>

  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0A0A0C;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;background-color:#121318;border:1px solid rgba(212,175,55,0.38);border-radius:18px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,0.85);">
          
          <!-- Header -->
          <tr>
            <td align="center" style="padding:28px 24px 18px;border-bottom:1px solid rgba(212,175,55,0.2);background:radial-gradient(circle at 50% 0%,#241f11,#121318 75%);">
              <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:3.5px;text-transform:uppercase;color:#D4AF37;font-weight:700;">
                ✦ SACRED NUMBER BLUEPRINT · 5 ANCIENT SYSTEMS ✦
              </div>
              <h1 style="margin:12px 0 6px;font-size:26px;line-height:1.25;color:#F5F5F7;font-weight:600;letter-spacing:0.5px;">
                {html.escape(first_name)}, Your 5-System Overlap Is Decoded.
              </h1>
              <p style="margin:0;font-family:'Arial',sans-serif;font-size:13px;color:#A1A1AA;">
                Prepared for <strong style="color:#F3E5AB;">{html.escape(name)}</strong> · Born {html.escape(dob_formatted)}
              </p>
            </td>
          </tr>

          <!-- #1 Master Overlap Anchor Card -->
          <tr>
            <td align="center" style="padding:28px 24px 18px;">
              <div style="font-family:'Arial',sans-serif;font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#D4AF37;margin-bottom:12px;">
                YOUR #1 PRIMARY SIGNATURE ANCHOR
              </div>
              <div style="width:96px;height:96px;line-height:96px;border-radius:999px;background:radial-gradient(circle at 30% 25%,#2a2516,#0d0d10 70%);border:2px solid #D4AF37;color:#D4AF37;font-size:44px;font-weight:700;text-align:center;margin:0 auto 14px;">
                {a1['number']}
              </div>
              <h2 style="margin:0 0 6px;font-size:24px;color:#F3E5AB;font-weight:600;">
                {html.escape(a1['archetype'])}
              </h2>
              <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#8E8E99;margin-bottom:14px;">
                {html.escape(a1['keywords'])}
              </div>
              <p style="margin:0 0 12px;font-family:'Arial',sans-serif;font-size:13px;color:#F3E5AB;">
                Appeared <strong>{a1['count']} times</strong> across <strong>{len(a1['systems'])} of 5 ancient systems</strong>:
              </p>
              <div style="margin-bottom:18px;">
                {a1_systems_badges}
              </div>
              <p style="margin:0;font-size:16px;line-height:1.6;color:#E4E4E7;max-width:480px;">
                “{html.escape(a1['summary'])}”
              </p>
            </td>
          </tr>

          <!-- ⚠️ SINGLE-SYSTEM FRICTION ALERT -->
          <tr>
            <td style="padding:0 24px 20px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:linear-gradient(145deg,#231215 0%,#151218 100%);border:1px solid rgba(248,113,113,0.42);border-left:4px solid #F87171;border-radius:12px;padding:16px 18px;">
                <tr>
                  <td>
                    <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#FCA5A5;font-weight:700;margin-bottom:6px;">
                      ⚠️ SINGLE-SYSTEM FRICTION ALERT · {html.escape(friction_headline)}
                    </div>
                    <p style="margin:0;font-family:'Arial',sans-serif;font-size:13px;line-height:1.58;color:#E4E4E7;">
                      {friction_text}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- #2 and #3 Overlap Anchors -->
          <tr>
            <td style="padding:0 24px 22px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0D0E12;border:1px solid rgba(212,175,55,0.25);border-radius:14px;padding:16px;">
                <tr>
                  <td style="padding:8px 10px;border-bottom:1px solid rgba(255,255,255,0.07);">
                    <div style="font-family:'Arial',sans-serif;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#D4AF37;">
                      #2 WEALTH &amp; STRATEGY ENGINE
                    </div>
                    <div style="font-size:17px;color:#F5F5F7;font-weight:600;margin-top:3px;">
                      Anchor #{a2['number']} · {html.escape(a2['archetype'])}
                      <span style="font-family:'Arial',sans-serif;font-size:12px;color:#A1A1AA;font-weight:400;">
                        ({a2['count']}× across {a2_sys_label}: {html.escape(', '.join(a2['systems']))})
                      </span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 10px 6px;">
                    <div style="font-family:'Arial',sans-serif;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#D4AF37;">
                      #3 SANCTUARY &amp; NERVOUS SYSTEM FOUNDATION
                    </div>
                    <div style="font-size:17px;color:#F5F5F7;font-weight:600;margin-top:3px;">
                      Anchor #{a3['number']} · {html.escape(a3['archetype'])}
                      <span style="font-family:'Arial',sans-serif;font-size:12px;color:#A1A1AA;font-weight:400;">
                        ({a3['count']}× across {a3_sys_label}: {html.escape(', '.join(a3['systems']))})
                      </span>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 5-System Snapshot Grid (With Curiosity Gap Locks on Systems II, III, V) -->
          <tr>
            <td style="padding:0 24px 22px;">
              <div style="font-family:'Arial',sans-serif;font-size:10px;letter-spacing:2.2px;text-transform:uppercase;color:#A1A1AA;margin-bottom:10px;text-align:center;">
                YOUR 5-SYSTEM MATHEMATICAL SNAPSHOT
              </div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="9" border="0" style="font-family:'Arial',sans-serif;font-size:13px;background-color:#0D0E12;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
                <tr>
                  <td style="color:#E4E4E7;border-bottom:1px solid rgba(255,255,255,0.06);">System I · Pythagorean Life Path</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['life_path'])} · {html.escape(lp_arch)}</td>
                </tr>
                <tr>
                  <td style="color:#E4E4E7;border-bottom:1px solid rgba(255,255,255,0.06);">System IV · Vedic Planetary Driver (Moolank)</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['vedic_moolank'])}</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">System II · Babylonian Chaldean Name Compound</td>
                  <td align="right" style="color:#D4AF37;font-size:12px;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.06);">🔒 Locked in Full 20-Page Dossier</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">System III · Kabbalistic Tree of Life &amp; Sephirot</td>
                  <td align="right" style="color:#D4AF37;font-size:12px;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.06);">🔒 Locked in Full 20-Page Dossier</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">System V · Chinese Lo Shu &amp; Missing Numbers</td>
                  <td align="right" style="color:#D4AF37;font-size:12px;font-weight:600;border-bottom:1px solid rgba(255,255,255,0.06);">🔒 Locked in Full 20-Page Dossier</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;">Current 52-Day Rosicrucian Timing Window</td>
                  <td align="right" style="color:#D4AF37;font-size:12px;font-weight:600;">🔒 Locked in Full 20-Page Dossier</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- What's Inside Your 20-Page Sovereign Dossier Value Stack -->
          <tr>
            <td style="padding:0 24px 20px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:radial-gradient(circle at 50% 0%,#1f1b10 0%,#0E0F14 100%);border:1px solid rgba(212,175,55,0.38);border-radius:14px;padding:18px 20px;">
                <tr>
                  <td>
                    <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:2.2px;text-transform:uppercase;color:#D4AF37;font-weight:700;margin-bottom:12px;text-align:center;">
                      ✦ WHAT’S INSIDE YOUR 20-PAGE SOVEREIGN DOSSIER ✦
                    </div>
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="5" border="0" style="font-family:'Arial',sans-serif;font-size:12.5px;line-height:1.5;color:#E4E4E7;">
                      <tr>
                        <td valign="top" style="color:#D4AF37;font-weight:700;width:18px;">✦</td>
                        <td><strong>Pages 1–5 · 5-Ring Convergence Mandala &amp; 15-Point Audit:</strong> Complete mathematical proof of all 15 source calculations and your 1–9 Frequency Tally.</td>
                      </tr>
                      <tr>
                        <td valign="top" style="color:#D4AF37;font-weight:700;">✦</td>
                        <td><strong>Pages 6–8 · Deep-Dive Into Your Big 3 Overlap Anchors (#{a1['number']}, #{a2['number']}, #{a3['number']}):</strong> Your Signature Identity, Wealth Engine, and Sanctuary Blueprint.</td>
                      </tr>
                      <tr>
                        <td valign="top" style="color:#D4AF37;font-weight:700;">✦</td>
                        <td><strong>Pages 9–14 · All 5 Ancient Systems Unredacted:</strong> Full Pythagorean, Babylonian Chaldean (10–52 compounds), Kabbalistic Tree of Life SVG, Vedic Navagraha, and 3×3 Chinese Lo Shu Grid.</td>
                      </tr>
                      <tr>
                        <td valign="top" style="color:#D4AF37;font-weight:700;">✦</td>
                        <td><strong>Pages 15–17 · Somatic Vitality &amp; Daily Operating Code:</strong> Wu Xing organ resilience, Ayurvedic Dosha reset, power days, and lucky coordinates.</td>
                      </tr>
                      <tr>
                        <td valign="top" style="color:#D4AF37;font-weight:700;">✦</td>
                        <td><strong>Pages 18–20 · 365-Day Rosicrucian 52-Day Cycles Calendar:</strong> Exact date windows for capital expansion vs. nervous system preservation.</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Primary CTA Buttons -->
          <tr>
            <td align="center" style="padding:4px 24px 28px;">
              <a href="{stripe_url}" style="display:inline-block;background:linear-gradient(135deg,#F3E5AB 0%,#D4AF37 50%,#AA820A 100%);color:#141108;font-family:'Arial',sans-serif;font-size:14px;font-weight:800;text-decoration:none;padding:16px 30px;border-radius:12px;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:14px;box-shadow:0 8px 25px rgba(212,175,55,0.3);">
                ✦ UNLOCK MY FULL 20-PAGE SOVEREIGN DOSSIER ($37)
              </a>
              <br>
              <a href="{teaser_url}" style="display:inline-block;color:#F3E5AB;font-family:'Arial',sans-serif;font-size:12px;font-weight:600;text-decoration:underline;padding:8px 16px;">
                ↻ Return to Your Interactive 5-System Teaser &amp; Watch Video Briefing
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:18px 24px;background-color:#09090B;border-top:1px solid rgba(255,255,255,0.07);font-family:'Arial',sans-serif;font-size:11px;color:#71717A;line-height:1.5;">
              © {datetime.now().year} Sacred Number Blueprint (@sacrednumberblueprint)<br>
              Mega Vega Ventures LLC · For self-reflection and educational purposes.
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, plain_text, html_body


# -----------------------------------------------------------------------------
# EMAIL #2 (24H LATER): MISSING CHINESE LO SHU NUMBERS & WEALTH ENGINE
# -----------------------------------------------------------------------------
def build_followup_email_2_loshu(lead: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (subject, plain_text, html_body) for Email #2 (24-Hour Follow-Up)."""
    name = lead["name"]
    first_name = name.split()[0] if name else "Friend"
    dob = lead["dob"]
    email_addr = lead["email"]
    calc = lead["calc"]
    a1, a2, a3 = calc["anchors"][0], calc["anchors"][1], calc["anchors"][2]
    missing_count = len(calc.get("missing_loshu", []))

    try:
        dob_formatted = datetime.strptime(dob, "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        dob_formatted = dob

    teaser_url = build_teaser_deep_link(name, dob, email_addr)
    stripe_url = f"{STRIPE_BASE_URL}?prefilled_email={urllib.parse.quote(email_addr)}"

    subject = f"✦ {first_name}, the missing numbers in your Chinese Lo Shu Grid..."
    preheader = (
        f"Your birth date ({dob_formatted}) leaves {missing_count} empty squares in your 3x3 Chinese Lo Shu Grid — "
        f"here is how they affect your relationships and Anchor #{a2['number']} Wealth Engine..."
    )

    plain_text = (
        f"SACRED NUMBER BLUEPRINT · SYSTEM V (IMPERIAL CHINESE LO SHU)\n"
        f"Prepared for {name} (Born {dob_formatted})\n"
        f"============================================================\n\n"
        f"{first_name}, yesterday we decoded your #1 Primary Signature Anchor (#{a1['number']} · {a1['archetype']}).\n\n"
        f"Today, look closely at System V of your chart: the ancient 3x3 Chinese Lo Shu Magic Square.\n"
        f"When we map the digits of your birth date ({dob}) alongside your core numbers, your chart reveals:\n"
        f"• Dominant Lo Shu Element: {calc.get('dominant_element', 'Metal')}\n"
        f"• Missing Lo Shu Numbers: {missing_count} of the 9 squares are completely absent in your natal grid.\n"
        f"• #2 Wealth & Strategy Engine: Anchor #{a2['number']} · {a2['archetype']} ({a2['count']}× across {', '.join(a2['systems'])})\n\n"
        f"In Chinese Five-Element (Wu Xing) science, empty squares in your Lo Shu grid act like subconscious magnets—"
        f"explaining why you repeatedly attract the same relationship friction or hit invisible ceilings when trying to "
        f"monetize your #{a2['number']} ({a2['archetype']}) Wealth Engine.\n\n"
        f"Pages 14 and 16 of your 20-Page Sovereign Dossier map your exact 3x3 Lo Shu Grid, reveal which numbers your "
        f"Chaldean birth name bridges, and give you the exact elemental remedies.\n\n"
        f"UNLOCK YOUR FULL 20-PAGE SOVEREIGN DOSSIER ($37):\n{stripe_url}\n\n"
        f"RETURN TO YOUR INTERACTIVE 5-SYSTEM TEASER:\n{teaser_url}\n"
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#0A0A0C;font-family:'Georgia',serif;color:#F5F5F7;">
  <div style="display:none;max-height:0px;overflow:hidden;mso-hide:all;font-size:1px;color:#0A0A0C;line-height:1px;opacity:0;">
    {html.escape(preheader)}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;
  </div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0A0A0C;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;background-color:#121318;border:1px solid rgba(212,175,55,0.38);border-radius:18px;overflow:hidden;">
          <tr>
            <td align="center" style="padding:26px 24px 18px;border-bottom:1px solid rgba(212,175,55,0.2);background:radial-gradient(circle at 50% 0%,#241f11,#121318 75%);">
              <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#D4AF37;font-weight:700;">
                ✦ SYSTEM V · IMPERIAL CHINESE LO SHU AUDIT ✦
              </div>
              <h1 style="margin:10px 0 6px;font-size:24px;color:#F5F5F7;font-weight:600;">
                {html.escape(first_name)}, Why {missing_count} Numbers Are Missing From Your Lo Shu Grid
              </h1>
              <p style="margin:0;font-family:'Arial',sans-serif;font-size:13px;color:#A1A1AA;">
                Profile: <strong style="color:#F3E5AB;">{html.escape(name)}</strong> · Born {html.escape(dob_formatted)}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 24px 18px;font-family:'Arial',sans-serif;font-size:14px;line-height:1.65;color:#E4E4E7;">
              <p style="margin:0 0 14px;">
                When most people check their numerology, they only look at their Western Life Path (<strong>{html.escape(calc['life_path'])}</strong>). They never see which digits are <strong>completely missing</strong> from their birth chart.
              </p>
              <p style="margin:0 0 16px;">
                When we place your birth date inside the ancient <strong>3×3 Chinese Lo Shu Magic Square</strong>, your chart shows a dominant <strong>{html.escape(calc.get('dominant_element', 'Metal'))}</strong> concentration—while leaving <strong>{missing_count} of the 9 elemental chambers empty</strong>.
              </p>
              <div style="background-color:#0D0E12;border:1px solid rgba(212,175,55,0.32);border-radius:12px;padding:16px;margin-bottom:16px;">
                <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#D4AF37;font-weight:700;margin-bottom:6px;">
                  YOUR #2 WEALTH &amp; RELATIONSHIP ENGINE
                </div>
                <div style="font-family:'Georgia',serif;font-size:18px;color:#F3E5AB;font-weight:600;margin-bottom:6px;">
                  Anchor #{a2['number']} · {html.escape(a2['archetype'])} ({a2['count']}× across {len(a2['systems'])} systems)
                </div>
                <p style="margin:0;font-size:13px;color:#D4D4D8;">
                  In Five-Element (Wu Xing) architecture, empty Lo Shu squares create subconscious relationship loops and block your #{a2['number']} Wealth Engine unless bridged by your Chaldean Name frequency.
                </p>
              </div>
              <p style="margin:0;">
                <strong>Pages 14, 16, and 17</strong> of your 20-Page Sovereign Dossier reveal your complete 3×3 Lo Shu Grid, your Arrows of Strength, and the exact elemental remedies to balance your chart.
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:6px 24px 28px;">
              <a href="{stripe_url}" style="display:inline-block;background:linear-gradient(135deg,#F3E5AB 0%,#D4AF37 50%,#AA820A 100%);color:#141108;font-family:'Arial',sans-serif;font-size:14px;font-weight:800;text-decoration:none;padding:16px 30px;border-radius:12px;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:12px;">
                ✦ UNLOCK MY FULL 20-PAGE SOVEREIGN DOSSIER ($37)
              </a>
              <br>
              <a href="{teaser_url}" style="display:inline-block;color:#F3E5AB;font-family:'Arial',sans-serif;font-size:12px;font-weight:600;text-decoration:underline;padding:8px 16px;">
                ↻ Return to Your Interactive 5-System Teaser &amp; Watch Video Briefing
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, plain_text, html_body


# -----------------------------------------------------------------------------
# EMAIL #3 (48H LATER): ACTIVE 52-DAY ROSICRUCIAN CYCLE & SOMATIC ALIGNMENT
# -----------------------------------------------------------------------------
def build_followup_email_3_cycles(lead: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (subject, plain_text, html_body) for Email #3 (48-Hour Follow-Up)."""
    name = lead["name"]
    first_name = name.split()[0] if name else "Friend"
    dob = lead["dob"]
    email_addr = lead["email"]
    calc = lead["calc"]
    a1, a2, a3 = calc["anchors"][0], calc["anchors"][1], calc["anchors"][2]

    cyc_name = calc.get("active_cycle_name", "The Solar Period")
    cyc_planet = calc.get("active_cycle_planet", "Sun")
    cyc_glyph = calc.get("active_cycle_glyph", "☉")
    cyc_theme = calc.get("active_cycle_theme", "Strategic Alignment")
    cyc_days = calc.get("active_cycle_days_remaining", 24)

    try:
        dob_formatted = datetime.strptime(dob, "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        dob_formatted = dob

    teaser_url = build_teaser_deep_link(name, dob, email_addr)
    stripe_url = f"{STRIPE_BASE_URL}?prefilled_email={urllib.parse.quote(email_addr)}"

    subject = f"⏳ {first_name}, your current 52-Day Rosicrucian Cycle is active"
    preheader = (
        f"You are currently in {cyc_name} ({cyc_days} days remaining) — see how to align your "
        f"#{a1['number']} Signature Anchor and nervous system..."
    )

    plain_text = (
        f"SACRED NUMBER BLUEPRINT · 52-DAY ROSICRUCIAN TIMING ALERT\n"
        f"Prepared for {name} (Born {dob_formatted})\n"
        f"============================================================\n\n"
        f"{first_name}, in ancient Rosicrucian and Vedic timing science, your personal year from birthday to birthday "
        f"is divided into seven 52-day planetary periods.\n\n"
        f"Based on your birth date ({dob_formatted}), you are currently inside:\n"
        f"• ACTIVE WINDOW: {cyc_glyph} {cyc_name} (Ruled by {cyc_planet} · {cyc_days} days remaining)\n"
        f"• CORE THEME: {cyc_theme}\n"
        f"• SOMATIC FOUNDATION: Anchor #{a3['number']} · {a3['archetype']}\n\n"
        f"Pushing for aggressive expansion during a preservation cycle—or hesitating during a Solar/Jupiterian wealth "
        f"window—is the #1 cause of burnout and stalled momentum.\n\n"
        f"Pages 15–20 of your 20-Page Sovereign Dossier map out all 7 of your 52-day cycles for the next 365 days, "
        f"complete with your Somatic Nervous System Reset protocol.\n\n"
        f"UNLOCK YOUR FULL 20-PAGE SOVEREIGN DOSSIER ($37):\n{stripe_url}\n\n"
        f"RETURN TO YOUR INTERACTIVE 5-SYSTEM TEASER:\n{teaser_url}\n"
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#0A0A0C;font-family:'Georgia',serif;color:#F5F5F7;">
  <div style="display:none;max-height:0px;overflow:hidden;mso-hide:all;font-size:1px;color:#0A0A0C;line-height:1px;opacity:0;">
    {html.escape(preheader)}&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;
  </div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0A0A0C;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;background-color:#121318;border:1px solid rgba(212,175,55,0.38);border-radius:18px;overflow:hidden;">
          <tr>
            <td align="center" style="padding:26px 24px 18px;border-bottom:1px solid rgba(212,175,55,0.2);background:radial-gradient(circle at 50% 0%,#241f11,#121318 75%);">
              <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#D4AF37;font-weight:700;">
                ⏳ ROSICRUCIAN 52-DAY BIORHYTHM ALERT ⏳
              </div>
              <h1 style="margin:10px 0 6px;font-size:24px;color:#F5F5F7;font-weight:600;">
                {html.escape(first_name)}, Your Current 52-Day Planetary Window Is Active
              </h1>
              <p style="margin:0;font-family:'Arial',sans-serif;font-size:13px;color:#A1A1AA;">
                Profile: <strong style="color:#F3E5AB;">{html.escape(name)}</strong> · Born {html.escape(dob_formatted)}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 24px 18px;font-family:'Arial',sans-serif;font-size:14px;line-height:1.65;color:#E4E4E7;">
              <p style="margin:0 0 14px;">
                In ancient Rosicrucian science, your year is not a flat line—it is divided into <strong>seven distinct 52-day planetary periods</strong> starting on your birthday.
              </p>
              <div style="background-color:#0D0E12;border:1px solid rgba(212,175,55,0.38);border-radius:12px;padding:16px;margin-bottom:16px;">
                <div style="font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#D4AF37;font-weight:700;margin-bottom:6px;">
                  ACTIVE TODAY ({cyc_days} DAYS REMAINING)
                </div>
                <div style="font-family:'Georgia',serif;font-size:20px;color:#F3E5AB;font-weight:600;margin-bottom:4px;">
                  {html.escape(cyc_glyph)} {html.escape(cyc_name)} · Ruled by {html.escape(cyc_planet)}
                </div>
                <p style="margin:0;font-size:13px;color:#D4D4D8;">
                  <strong>Window Directive:</strong> {html.escape(cyc_theme)}
                </p>
              </div>
              <p style="margin:0 0 14px;">
                When you align your <strong>#1 Signature Anchor (#{a1['number']} · {html.escape(a1['archetype'])})</strong> and your <strong>#3 Sanctuary Foundation (#{a3['number']} · {html.escape(a3['archetype'])})</strong> with your active 52-day window, resistance drops away.
              </p>
              <p style="margin:0;">
                Unlock your complete <strong>20-Page Sovereign Dossier PDF</strong> now to get your full 365-day Rosicrucian Calendar (Pages 18–20) and Somatic Nervous System Architecture (Page 15).
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:6px 24px 28px;">
              <a href="{stripe_url}" style="display:inline-block;background:linear-gradient(135deg,#F3E5AB 0%,#D4AF37 50%,#AA820A 100%);color:#141108;font-family:'Arial',sans-serif;font-size:14px;font-weight:800;text-decoration:none;padding:16px 30px;border-radius:12px;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:12px;">
                ✦ UNLOCK MY FULL 20-PAGE SOVEREIGN DOSSIER ($37)
              </a>
              <br>
              <a href="{teaser_url}" style="display:inline-block;color:#F3E5AB;font-family:'Arial',sans-serif;font-size:12px;font-weight:600;text-decoration:underline;padding:8px 16px;">
                ↻ Return to Your Interactive 5-System Teaser &amp; Watch Video Briefing
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, plain_text, html_body


def send_email_via_smtp(recipient: str, subject: str, plain_text: str, html_body: str, step_num: int = 1) -> bool:
    """Dispatches a luxury HTML email via Google Workspace SMTP."""
    recipient = recipient.strip()
    if not recipient or "@" not in recipient:
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_DISPLAY
    msg["To"] = recipient
    msg["Reply-To"] = SMTP_USER

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [recipient, SMTP_USER], msg.as_string())
        print(f"✓ Luxury HTML Follow-Up Email #{step_num} sent to {recipient} (and copy to {SMTP_USER})", flush=True)
        return True
    except Exception as e:
        print(f"✗ SMTP send error (Email #{step_num}) for {recipient}: {e}", flush=True)
        return False


def send_followup_email(lead: Dict[str, Any], step: int = 1) -> bool:
    """Builds and sends Email #1 (Instant), Email #2 (24h), or Email #3 (48h)."""
    if step == 2:
        subject, plain_text, html_body = build_followup_email_2_loshu(lead)
    elif step == 3:
        subject, plain_text, html_body = build_followup_email_3_cycles(lead)
    else:
        subject, plain_text, html_body = build_luxury_followup_email(lead)
    return send_email_via_smtp(lead["email"], subject, plain_text, html_body, step_num=step)


# -----------------------------------------------------------------------------
# STORAGE: CSV + OBSIDIAN DASHBOARD + SUPABASE POSTGRESQL
# -----------------------------------------------------------------------------
def ensure_supabase_table():
    try:
        import psycopg2
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.numerology_leads (
                id SERIAL PRIMARY KEY,
                lead_key TEXT UNIQUE,
                captured_at TIMESTAMPTZ DEFAULT NOW(),
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL,
                lang TEXT DEFAULT 'en',
                top_3_overlap_numbers TEXT,
                life_path TEXT,
                vedic_moolank TEXT,
                chaldean_name TEXT,
                email_sent BOOLEAN DEFAULT FALSE,
                raw_payload JSONB
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  [Notice] Supabase table init skipped: {e}", flush=True)


def save_lead_to_supabase(lead: Dict[str, Any], email_sent: bool):
    try:
        import psycopg2
        ensure_supabase_table()
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cur = conn.cursor()
        lead_key = f"{lead['email'].lower()}::{lead['dob']}::{lead['name'].lower()}"
        calc = lead["calc"]
        cur.execute("""
            INSERT INTO public.numerology_leads
            (lead_key, captured_at, full_name, dob, email, lang, top_3_overlap_numbers, life_path, vedic_moolank, chaldean_name, email_sent, raw_payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (lead_key) DO UPDATE SET
                captured_at = EXCLUDED.captured_at,
                top_3_overlap_numbers = EXCLUDED.top_3_overlap_numbers,
                life_path = EXCLUDED.life_path,
                vedic_moolank = EXCLUDED.vedic_moolank,
                chaldean_name = EXCLUDED.chaldean_name,
                email_sent = EXCLUDED.email_sent,
                raw_payload = EXCLUDED.raw_payload;
        """, (
            lead_key,
            lead["timestamp"],
            lead["name"],
            lead["dob"],
            lead["email"],
            lead.get("lang", "en"),
            calc["top_3_overlap_numbers"],
            calc["life_path"],
            calc["vedic_moolank"],
            calc["chaldean_name"],
            email_sent,
            json.dumps(lead, ensure_ascii=False),
        ))
        conn.commit()
        cur.close()
        conn.close()
        print("✓ Lead synced to Supabase PostgreSQL (`public.numerology_leads`).", flush=True)
    except Exception as e:
        print(f"  [Notice] Supabase lead insert failed: {e}", flush=True)


def extract_utm_from_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    """Extracts utm_source, utm_medium, utm_campaign, cohort, and ttclid from a webhook payload."""
    prof = payload.get("profile") if isinstance(payload.get("profile"), dict) else {}
    prof_utm = prof.get("utm") if isinstance(prof.get("utm"), dict) else {}
    top_utm = payload.get("utm") if isinstance(payload.get("utm"), dict) else {}

    merged: Dict[str, str] = {}
    for k in ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "cohort", "ttclid"):
        val = (
            payload.get(k)
            or top_utm.get(k)
            or prof_utm.get(k)
            or ""
        )
        val_str = str(val).strip()
        if val_str:
            merged[k] = val_str
    return merged


def format_attribution_source(utm: Optional[Dict[str, Any]] = None) -> str:
    """
    Classifies a lead's UTM/cohort dictionary into a clean attribution label for Obsidian:
    - 'TikTok Promote' (or 'TikTok Promote (Cohort B)' if cohort is also present)
    - 'Cohort B' / 'Organic Bio · Cohort B'
    - 'Organic Bio' (default when arriving from bio or direct without paid flags)
    """
    u = utm or {}
    src = str(u.get("utm_source") or "").strip().lower()
    med = str(u.get("utm_medium") or "").strip().lower()
    camp = str(u.get("utm_campaign") or "").strip().lower()
    cohort_raw = str(u.get("cohort") or "").strip()
    cohort_low = cohort_raw.lower()
    ttclid = str(u.get("ttclid") or "").strip()

    is_promote = (
        med in ("promote", "paid", "cpc", "ads", "ppc", "spark")
        or "promote" in src
        or "promote" in camp
        or "paid" in camp
        or bool(ttclid)
    )
    is_cohort_c = (
        cohort_low in ("c", "cohort_c", "cohort-c", "short", "short_01", "short_02", "short_03", "short_04", "short_05", "short_06")
        or "cohort_c" in camp
        or "cohort-c" in camp
        or "short_" in camp
    )
    is_cohort_b = (
        cohort_low in ("b", "cohort_b", "cohort-b", "broll", "broll_01", "broll_02")
        or "cohort_b" in camp
        or "cohort-b" in camp
        or "broll" in camp
    )
    is_cohort_a = (
        cohort_low in ("a", "cohort_a", "cohort-a")
        or "cohort_a" in camp
        or "cohort-a" in camp
    )

    if is_promote:
        if is_cohort_c:
            return "TikTok Promote (Cohort C)"
        if is_cohort_b:
            return "TikTok Promote (Cohort B)"
        if is_cohort_a:
            return "TikTok Promote (Cohort A)"
        if camp and camp not in ("promote", "tiktok_promote"):
            return f"TikTok Promote ({u.get('utm_campaign')})"
        return "TikTok Promote"

    if is_cohort_c:
        if med == "bio" or src == "tiktok":
            return "Organic Bio · Cohort C"
        return "Cohort C"

    if is_cohort_b:
        if med == "bio" or src == "tiktok":
            return "Organic Bio · Cohort B"
        return "Cohort B"

    if is_cohort_a:
        if med == "bio" or src == "tiktok":
            return "Organic Bio · Cohort A"
        return "Cohort A"

    if src in ("ig", "ig_bio", "instagram") or cohort_low in ("ig_reels", "ig", "instagram"):
        if cohort_low == "ig_reels":
            return "Instagram Bio · Reels"
        return "Instagram Bio"

    if cohort_raw:
        return f"Cohort {cohort_raw}"

    if src or med or camp:
        if (src in ("tiktok", "tt", "") and med in ("bio", "organic", "profile", "")):
            if camp:
                return f"Organic Bio ({u.get('utm_campaign')})"
            return "Organic Bio"
        parts = [p for p in (u.get("utm_source"), u.get("utm_medium"), u.get("utm_campaign")) if p]
        return " / ".join(str(p) for p in parts)

    return "Organic Bio"


def append_lead_to_csv_and_obsidian(lead: Dict[str, Any], email_sent: bool):
    calc = lead["calc"]
    utm = lead.get("utm") if isinstance(lead.get("utm"), dict) else {}
    source_attr = lead.get("source_attribution") or format_attribution_source(utm)

    row = {
        "timestamp": lead["timestamp"],
        "name": lead["name"],
        "dob": lead["dob"],
        "email": lead["email"],
        "lang": lead.get("lang", "en"),
        "source_attribution": source_attr,
        "utm_source": utm.get("utm_source", ""),
        "utm_medium": utm.get("utm_medium", ""),
        "utm_campaign": utm.get("utm_campaign", ""),
        "cohort": utm.get("cohort", ""),
        "top_3_overlap_numbers": calc["top_3_overlap_numbers"],
        "life_path": calc["life_path"],
        "vedic_moolank": calc["vedic_moolank"],
        "chaldean_name": calc["chaldean_name"],
        "email_sent": "YES" if email_sent else "NO",
        "email_1_sent_at": lead.get("email_1_sent_at") or "",
        "email_2_sent_at": lead.get("email_2_sent_at") or "",
        "email_3_sent_at": lead.get("email_3_sent_at") or "",
    }

    for csv_path in [LOCAL_CSV_PATH, GDRIVE_CSV_PATH]:
        try:
            parent = os.path.dirname(csv_path)
            if parent and not os.path.exists(parent):
                continue
            existing_rows = []
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                with open(csv_path, "r", encoding="utf-8") as rf:
                    reader = csv.DictReader(rf)
                    existing_rows = list(reader)

            # Deduplicate by (email, dob, name) so re-sends update the row cleanly
            updated = False
            for idx, r in enumerate(existing_rows):
                if (
                    r.get("email", "").lower() == row["email"].lower()
                    and r.get("dob", "") == row["dob"]
                    and r.get("name", "").lower() == row["name"].lower()
                ):
                    # Preserve earlier UTM/attribution if the new one is empty
                    if not row["utm_source"] and r.get("utm_source"):
                        row["utm_source"] = r.get("utm_source", "")
                    if not row["utm_medium"] and r.get("utm_medium"):
                        row["utm_medium"] = r.get("utm_medium", "")
                    if not row["utm_campaign"] and r.get("utm_campaign"):
                        row["utm_campaign"] = r.get("utm_campaign", "")
                    if not row["cohort"] and r.get("cohort"):
                        row["cohort"] = r.get("cohort", "")
                    if row["source_attribution"] == "Organic Bio" and r.get("source_attribution") and r.get("source_attribution") != "Organic Bio":
                        row["source_attribution"] = r.get("source_attribution", "Organic Bio")
                    existing_rows[idx] = row
                    updated = True
                    break
            if not updated:
                existing_rows.append(row)

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
                writer.writeheader()
                for r in existing_rows:
                    if not r.get("source_attribution"):
                        r["source_attribution"] = format_attribution_source(r)
                    writer.writerow(r)
            print(f"✓ Lead synced to CSV: {csv_path}", flush=True)
        except Exception as e:
            print(f"  [Notice] Could not write CSV {csv_path}: {e}", flush=True)

    # Also regenerate Obsidian Markdown Dashboard from LOCAL_CSV_PATH and TELEMETRY_STATE_PATH
    update_obsidian_dashboard()


def load_telemetry_events() -> List[Dict[str, Any]]:
    if os.path.exists(TELEMETRY_STATE_PATH):
        try:
            with open(TELEMETRY_STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []


def save_telemetry_events(events: List[Dict[str, Any]]):
    for p in (TELEMETRY_STATE_PATH, GDRIVE_TELEMETRY_PATH):
        try:
            parent = os.path.dirname(p)
            if parent and os.path.exists(parent):
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(events, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def classify_visitor_browser(payload: Dict[str, Any]) -> Dict[str, Any]:
    ua = str(payload.get("user_agent") or "").strip()
    is_tt = bool(payload.get("is_tiktok_inapp")) or bool(
        re.search(r"BytedanceWebview|musical_ly|TikTok|trill|ByteLocale", ua, re.IGNORECASE)
    )
    is_ig = bool(payload.get("is_instagram_inapp")) or bool(re.search(r"Instagram", ua, re.IGNORECASE))
    is_fb = bool(re.search(r"FBAN|FBAV", ua, re.IGNORECASE))
    is_ios = bool(re.search(r"iPhone|iPad|iPod", ua, re.IGNORECASE))
    is_android = bool(re.search(r"Android", ua, re.IGNORECASE))
    is_mobile = is_ios or is_android or bool(re.search(r"Mobile", ua, re.IGNORECASE)) or payload.get("device_type") == "Mobile"
    os_tag = "iOS" if is_ios else ("Android" if is_android else ("Mobile" if is_mobile else "Desktop"))

    label = str(payload.get("browser_label") or "").strip()
    if not label or label in ("Desktop Browser", "Mobile Browser"):
        if is_tt:
            label = f"TikTok In-App ({os_tag})"
        elif is_ig:
            label = f"Instagram In-App ({os_tag})"
        elif is_fb:
            label = f"Facebook In-App ({os_tag})"
        elif re.search(r"CriOS|Chrome", ua, re.IGNORECASE) and not re.search(r"Edg", ua, re.IGNORECASE):
            label = f"{os_tag} Chrome"
        elif re.search(r"Safari", ua, re.IGNORECASE) and not re.search(r"Chrome|CriOS", ua, re.IGNORECASE):
            label = f"{os_tag} Safari"
        else:
            label = f"{os_tag} Browser"

    return {
        "user_agent": ua,
        "is_tiktok_inapp": is_tt,
        "is_instagram_inapp": is_ig,
        "device_type": "Mobile" if is_mobile else "Desktop",
        "browser_label": label,
        "referrer": str(payload.get("referrer") or "Direct / Bio Link").strip(),
    }


def record_telemetry_event(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Records a funnel telemetry event (`page_view`, `calc_started`, `calc_preview`,
    `lead_submitted`, `checkout_clicked`, `purchase_return`) into telemetry_events.json
    and refreshes Leads_Captured_Dashboard.md.
    Filters out headless Playwright / bot traffic so automated tests never pollute metrics.
    """
    raw_ev = str(payload.get("event_type") or payload.get("event") or "").strip().lower()
    ev_map = {
        "page_view": "page_view",
        "calc_started": "calc_started",
        "field_progress": "calc_started",
        "calc_preview": "calc_preview",
        "lead_capture": "lead_submitted",
        "lead_submitted": "lead_submitted",
        "checkout_click": "checkout_clicked",
        "checkout_clicked": "checkout_clicked",
        "purchase_return": "purchase_return",
    }
    event_type = ev_map.get(raw_ev)
    if not event_type:
        return None

    ua = str(payload.get("user_agent") or "")
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    if not extra.get("force_telemetry") and re.search(r"HeadlessChrome|Playwright|PhantomJS", ua, re.IGNORECASE):
        return None

    prof = payload.get("profile") if isinstance(payload.get("profile"), dict) else {}
    raw_name = str(prof.get("fullName") or "").strip()
    raw_dob = str(prof.get("birthDate") or "").strip()
    raw_email = str(prof.get("email") or "").strip()

    if raw_email.lower().endswith("@sovereign5.com") or raw_email.lower() == "test@example.com":
        return None
    if raw_name.lower() == "adam vega" and normalize_dob(raw_dob) == "1978-08-19" and not extra.get("force_telemetry"):
        return None

    clean_name = " ".join(w.capitalize() for w in raw_name.split()) if raw_name else ""
    iso_dob = normalize_dob(raw_dob) if raw_dob else ""
    nums = payload.get("numbers") if isinstance(payload.get("numbers"), dict) else {}
    top3 = str(nums.get("top_3_overlap_numbers") or "").strip()
    lp_str = str(nums.get("life_path") or "").strip()
    vedic_str = str(nums.get("vedic_moolank") or "").strip()
    chal_str = str(nums.get("chaldean_name") or "").strip()

    if clean_name and re.match(r"^\d{4}-\d{2}-\d{2}$", iso_dob) and not top3:
        try:
            c = calculate_5_systems(clean_name, iso_dob)
            top3 = c["top_3_overlap_numbers"]
            lp_str = c["life_path"]
            vedic_str = c["vedic_moolank"]
            chal_str = c["chaldean_name"]
        except Exception:
            pass

    utm_data = extract_utm_from_payload(payload)
    source_attr = format_attribution_source(utm_data)
    b_info = classify_visitor_browser(payload)
    session_id = str(payload.get("session_id") or prof.get("id") or "").strip() or f"anon_{(payload.get('timestamp') or '')[:16]}"
    tier_label = str(extra.get("tier_label") or extra.get("tier") or "").strip()
    if event_type == "checkout_clicked" and not tier_label:
        total_p = extra.get("total") or (84 if extra.get("bump") else 37)
        tier_label = f"${total_p} ({'Bundle' if extra.get('bump') else 'Base'})"

    if event_type in ("page_view", "calc_started"):
        dedup_key = f"{session_id}::{event_type}"
    elif event_type == "calc_preview":
        dedup_key = f"{session_id}::calc_preview::{clean_name.lower()}::{iso_dob}"
    elif event_type == "checkout_clicked":
        dedup_key = f"{session_id}::checkout_clicked::{tier_label}::{(payload.get('timestamp') or '')[:16]}"
    else:
        dedup_key = f"{session_id}::{event_type}::{clean_name.lower()}::{iso_dob}::{raw_email.lower()}"

    field_touched = str(extra.get("field") or "").strip()
    fields_touched_list = extra.get("fields_touched") if isinstance(extra.get("fields_touched"), list) else ([field_touched] if field_touched else [])

    events = load_telemetry_events()
    for existing in events:
        if existing.get("dedup_key") == dedup_key:
            if event_type == "calc_started" and fields_touched_list:
                prev_fields = existing.get("fields_touched") or []
                for ft in fields_touched_list:
                    if ft and ft not in prev_fields:
                        prev_fields.append(ft)
                existing["fields_touched"] = prev_fields
                save_telemetry_events(events)
                update_obsidian_dashboard()
            return existing

    record = {
        "dedup_key": dedup_key,
        "timestamp": str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        "session_id": session_id,
        "event_type": event_type,
        "browser_label": b_info["browser_label"],
        "is_tiktok_inapp": b_info["is_tiktok_inapp"],
        "is_instagram_inapp": b_info["is_instagram_inapp"],
        "device_type": b_info["device_type"],
        "referrer": b_info["referrer"],
        "source_attribution": source_attr,
        "utm": utm_data,
        "name": clean_name,
        "dob": iso_dob,
        "email": raw_email,
        "top_3_overlap_numbers": top3,
        "life_path": lp_str,
        "vedic_moolank": vedic_str,
        "chaldean_name": chal_str,
        "tier_label": tier_label,
        "fields_touched": [f for f in fields_touched_list if f],
    }
    events.append(record)
    save_telemetry_events(events)
    update_obsidian_dashboard()
    print(f"✓ Telemetry [{event_type}] logged: {b_info['browser_label']} | {clean_name or 'Visitor'} {iso_dob}", flush=True)
    return record


def update_obsidian_dashboard():
    """
    Regenerates G:\\My Drive\\MVV_Memory_Vault\\03-Projects\\Leads_Captured_Dashboard.md with:
    1. Live Funnel Conversion Telemetry Summary table (page_view, calc_started, calc_preview, lead_submitted, checkout_clicked)
    2. Recent Visitor Activity & Name/DOB Preview Log table
    3. Captured Email Leads & 3-Part Drip Sequence Log table
    """
    try:
        rows = []
        if os.path.exists(LOCAL_CSV_PATH):
            with open(LOCAL_CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        events = load_telemetry_events()
        page_views = [e for e in events if e.get("event_type") == "page_view"]
        tt_views = [e for e in page_views if e.get("is_tiktok_inapp")]
        ig_views = [e for e in page_views if e.get("is_instagram_inapp") or "Instagram In-App" in str(e.get("browser_label", ""))]
        other_views = [e for e in page_views if not e.get("is_tiktok_inapp") and not (e.get("is_instagram_inapp") or "Instagram In-App" in str(e.get("browser_label", "")))]
        calc_started = [e for e in events if e.get("event_type") == "calc_started"]
        calc_previews = [e for e in events if e.get("event_type") == "calc_preview"]
        lead_submits = [e for e in events if e.get("event_type") == "lead_submitted"]
        checkout_clicks = [e for e in events if e.get("event_type") == "checkout_clicked"]

        total_leads_count = max(len(rows), len(lead_submits))

        if os.path.exists(os.path.dirname(OBSIDIAN_DASHBOARD_PATH)):
            md_lines = [
                "---",
                "title: Sacred Number Blueprint — Live Funnel Telemetry & Captured Leads Dashboard",
                "project: Sacred Number Blueprint (@sacrednumberblueprint)",
                f"date_updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"total_page_views: {len(page_views)}",
                f"tiktok_inapp_views: {len(tt_views)}",
                f"instagram_inapp_views: {len(ig_views)}",
                f"calc_previews: {len(calc_previews)}",
                f"total_leads: {len(rows)}",
                f"checkout_clicks: {len(checkout_clicks)}",
                "tags:",
                "  - leads",
                "  - telemetry",
                "  - sacred-number-blueprint",
                "  - funnel-crm",
                "---",
                "",
                "# 📊 Sacred Number Blueprint — Live Funnel Telemetry & Captured Leads Dashboard",
                "",
                "> [!INFO] Real-Time Top-to-Bottom Funnel Telemetry (`https://blueprint.megavegaventures.com/`)",
                "> Tracks every real visitor session from the moment they tap the TikTok or Instagram bio link (`page_view`), focus the calculator (`calc_started`), test a Name & Birthday (`calc_preview` — captured even if they skip Email!), submit their Email (`lead_submitted`), or click a Stripe checkout tier (`checkout_clicked`). Headless Playwright/localhost test runs are automatically filtered out.",
                "",
                "## 1. Live Funnel Conversion Telemetry Summary",
                "",
                "| Funnel Stage | Event Key | Total Count | Breakdown / Conversion Notes |",
                "| :--- | :--- | :---: | :--- |",
                f"| **1. Real Visitor Sessions** | `page_view` | **{len(page_views)}** | **TikTok In-App:** `{len(tt_views)}` · **Instagram In-App:** `{len(ig_views)}` · **Web/Other:** `{len(other_views)}` |",
                f"| **2. Calculator Interactions** | `calc_started` | **{len(calc_started)}** | Visitors who tapped into the Name or Birth Date input field |",
                f"| **3. Instant Name + DOB Previews** | `calc_preview` | **{len(calc_previews)}** | Visitors who tested a Name & Birthday (captured even without Email) |",
                f"| **4. Full Email Leads Captured** | `lead_submitted` | **{total_leads_count}** | Enrolled in automated 3-part luxury HTML email sequence |",
                f"| **5. Stripe Checkout Clicks** | `checkout_clicked` | **{len(checkout_clicks)}** | Visitors who clicked `$37` Base, `$84` Bundle, or `$47` Cycles Upgrade |",
                "",
                "---",
                "",
                "## 2. Recent Visitor Activity & Name/DOB Preview Log",
                "",
                "| Timestamp (UTC) | Funnel Event | Device & Browser | Source / Cohort | Tested Name | Tested DOB | Big 3 Overlap / Life Path | Checkout Tier Clicked |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ]

            stage_badges = {
                "page_view": "👀 `page_view`",
                "calc_started": "✍️ `calc_started`",
                "calc_preview": "🔮 `calc_preview`",
                "lead_submitted": "📩 `lead_submitted`",
                "checkout_clicked": "💳 `checkout_clicked`",
                "purchase_return": "🏆 `purchase_return`",
            }
            if events:
                for ev in reversed(events[-100:]):
                    ts_short = str(ev.get("timestamp") or "")[:19]
                    st_label = stage_badges.get(ev.get("event_type", ""), f"`{ev.get('event_type', '')}`")
                    if ev.get("event_type") == "calc_started" and ev.get("fields_touched"):
                        st_label += f" ({', '.join(f'`{x}`' for x in ev['fields_touched'])})"
                    br_label = ev.get("browser_label") or "Browser"
                    src_attr = ev.get("source_attribution") or "Organic Bio"
                    t_name = f"**{ev['name']}**" if ev.get("name") else "—"
                    t_dob = f"`{ev['dob']}`" if ev.get("dob") else "—"
                    num_summary = "—"
                    if ev.get("top_3_overlap_numbers"):
                        num_summary = f"**{ev['top_3_overlap_numbers']}** (LP `{ev.get('life_path', '')}`)"
                    tier_col = f"**{ev['tier_label']}**" if ev.get("tier_label") else "—"
                    md_lines.append(
                        f"| `{ts_short}` | {st_label} | `{br_label}` | **{src_attr}** | {t_name} | {t_dob} | {num_summary} | {tier_col} |"
                    )
            else:
                md_lines.append("| *(Waiting for next live visitor...)* | — | — | — | — | — | — | — |")

            md_lines.extend([
                "",
                "---",
                "",
                "## 3. Captured Email Leads & 3-Part Drip Sequence Log",
                "",
                "| Timestamp (UTC) | Full Birth Name | DOB | Email | Source / Cohort | Lang | Big 3 Overlap Anchors | Life Path | Vedic Moolank | Chaldean Name | Email #1 (Instant) | Email #2 (24h) | Email #3 (48h) |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ])
            for r in reversed(rows):
                e1 = "✅" if r.get("email_1_sent_at") or r.get("email_sent") == "YES" else "⏳"
                e2 = "✅" if r.get("email_2_sent_at") else "⏳"
                e3 = "✅" if r.get("email_3_sent_at") else "⏳"
                src_label = r.get("source_attribution") or format_attribution_source(r)
                md_lines.append(
                    f"| `{r.get('timestamp', '')[:19]}` | **{r.get('name', '')}** | `{r.get('dob', '')}` | `{r.get('email', '')}` | **{src_label}** | `{r.get('lang', 'en')}` | **{r.get('top_3_overlap_numbers', '')}** | `{r.get('life_path', '')}` | `{r.get('vedic_moolank', '')}` | `{r.get('chaldean_name', '')}` | {e1} | {e2} | {e3} |"
                )
            md_lines.append("")
            with open(OBSIDIAN_DASHBOARD_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))
            print(f"✓ Obsidian Leads & Telemetry Dashboard updated: {OBSIDIAN_DASHBOARD_PATH}", flush=True)
    except Exception as e:
        print(f"  [Notice] Could not update Obsidian Leads Dashboard: {e}", flush=True)


# -----------------------------------------------------------------------------
# DEDUPLICATION, LEAD PROCESSOR & 24H / 48H DRIP SCHEDULER
# -----------------------------------------------------------------------------
def load_processed_state() -> Dict[str, Any]:
    if os.path.exists(PROCESSED_LEADS_PATH):
        try:
            with open(PROCESSED_LEADS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_processed_state(state: Dict[str, Any]):
    try:
        with open(PROCESSED_LEADS_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def process_lead(
    full_name: str,
    dob_str: str,
    email_addr: str,
    lang: str = "en",
    timestamp: Optional[str] = None,
    force_send: bool = False,
    utm: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    iso_dob = normalize_dob(dob_str)
    clean_email = email_addr.strip()
    clean_name = " ".join(w.capitalize() for w in full_name.strip().split())
    dedup_key = f"{clean_email.lower()}::{iso_dob}::{clean_name.lower()}"

    processed = load_processed_state()
    if not force_send and dedup_key in processed and processed[dedup_key].get("email_1_sent_at"):
        print(f"  [Skip] Lead already processed & emailed: {clean_name} ({clean_email})", flush=True)
        return processed[dedup_key]

    calc = calculate_5_systems(clean_name, iso_dob)
    now_iso = datetime.now(timezone.utc).isoformat()
    ts = timestamp or now_iso
    existing_entry = processed.get(dedup_key, {})

    merged_utm = dict(existing_entry.get("utm") or {})
    if isinstance(utm, dict):
        for k, v in utm.items():
            if v:
                merged_utm[k] = str(v).strip()
    source_attribution = format_attribution_source(merged_utm)

    lead_record = {
        "timestamp": ts,
        "name": clean_name,
        "dob": iso_dob,
        "email": clean_email,
        "lang": lang or "en",
        "utm": merged_utm,
        "source_attribution": source_attribution,
        "calc": calc,
        "email_1_sent_at": existing_entry.get("email_1_sent_at"),
        "email_2_sent_at": existing_entry.get("email_2_sent_at"),
        "email_3_sent_at": existing_entry.get("email_3_sent_at"),
    }

    email_sent = send_followup_email(lead_record, step=1)
    if email_sent:
        lead_record["email_1_sent_at"] = now_iso

    append_lead_to_csv_and_obsidian(lead_record, email_sent)
    save_lead_to_supabase(lead_record, email_sent)

    processed[dedup_key] = {
        "timestamp": ts,
        "name": clean_name,
        "dob": iso_dob,
        "email": clean_email,
        "lang": lang or "en",
        "utm": merged_utm,
        "source_attribution": source_attribution,
        "top_3_overlap_numbers": calc["top_3_overlap_numbers"],
        "life_path": calc["life_path"],
        "expression": calc["expression"],
        "vedic_moolank": calc["vedic_moolank"],
        "chaldean_name": calc["chaldean_name"],
        "email_sent": email_sent,
        "email_1_sent_at": lead_record["email_1_sent_at"],
        "email_2_sent_at": lead_record["email_2_sent_at"],
        "email_3_sent_at": lead_record["email_3_sent_at"],
    }
    save_processed_state(processed)
    return processed[dedup_key]


def check_and_send_scheduled_followups(now_utc: Optional[datetime] = None) -> int:
    """
    Checks all leads in processed_leads_state.json and automatically sends:
    - Email #2 (Lo Shu Missing Numbers & Wealth Engine) when >= 24h after email_1_sent_at
    - Email #3 (52-Day Rosicrucian Cycle) when >= 48h after email_1_sent_at
    """
    now = now_utc or datetime.now(timezone.utc)
    processed = load_processed_state()
    sent_count = 0

    for dedup_key, entry in list(processed.items()):
        e1_str = entry.get("email_1_sent_at") or entry.get("timestamp")
        if not e1_str:
            continue
        try:
            e1_dt = datetime.fromisoformat(e1_str.replace("Z", "+00:00"))
            if e1_dt.tzinfo is None:
                e1_dt = e1_dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        elapsed_hours = (now - e1_dt).total_seconds() / 3600.0
        name = entry.get("name", "")
        dob = entry.get("dob", "")
        email_addr = entry.get("email", "")
        lang = entry.get("lang", "en")
        if not (name and dob and email_addr):
            continue

        # Check 24h Follow-Up (Email #2)
        if elapsed_hours >= 24.0 and not entry.get("email_2_sent_at"):
            calc = calculate_5_systems(name, dob)
            lead_record = {
                "timestamp": entry.get("timestamp", now.isoformat()),
                "name": name,
                "dob": dob,
                "email": email_addr,
                "lang": lang,
                "utm": entry.get("utm") or {},
                "source_attribution": entry.get("source_attribution") or format_attribution_source(entry.get("utm")),
                "calc": calc,
                "email_1_sent_at": entry.get("email_1_sent_at"),
                "email_2_sent_at": None,
                "email_3_sent_at": entry.get("email_3_sent_at"),
            }
            if send_followup_email(lead_record, step=2):
                entry["email_2_sent_at"] = now.isoformat()
                lead_record["email_2_sent_at"] = entry["email_2_sent_at"]
                processed[dedup_key] = entry
                save_processed_state(processed)
                append_lead_to_csv_and_obsidian(lead_record, True)
                save_lead_to_supabase(lead_record, True)
                sent_count += 1

        # Check 48h Follow-Up (Email #3)
        if elapsed_hours >= 48.0 and not entry.get("email_3_sent_at"):
            calc = calculate_5_systems(name, dob)
            lead_record = {
                "timestamp": entry.get("timestamp", now.isoformat()),
                "name": name,
                "dob": dob,
                "email": email_addr,
                "lang": lang,
                "utm": entry.get("utm") or {},
                "source_attribution": entry.get("source_attribution") or format_attribution_source(entry.get("utm")),
                "calc": calc,
                "email_1_sent_at": entry.get("email_1_sent_at"),
                "email_2_sent_at": entry.get("email_2_sent_at"),
                "email_3_sent_at": None,
            }
            if send_followup_email(lead_record, step=3):
                entry["email_3_sent_at"] = now.isoformat()
                lead_record["email_3_sent_at"] = entry["email_3_sent_at"]
                processed[dedup_key] = entry
                save_processed_state(processed)
                append_lead_to_csv_and_obsidian(lead_record, True)
                save_lead_to_supabase(lead_record, True)
                sent_count += 1

    return sent_count


def poll_cloud_relay_once() -> int:
    """Polls ntfy.sh cloud relay for any new lead_capture payloads and runs 24h/48h drip checks."""
    count = 0
    try:
        req = urllib.request.Request(NTFY_POLL_URL, headers={"User-Agent": "Sovereign5-LeadWorker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                try:
                    envelope = json.loads(line)
                    if envelope.get("event") != "message":
                        continue
                    msg_str = envelope.get("message", "")
                    payload = json.loads(msg_str)
                    ev_name = str(payload.get("event_type") or payload.get("event") or "").strip().lower()
                    if ev_name in ("page_view", "calc_started", "field_progress", "calc_preview", "lead_capture", "lead_submitted", "checkout_click", "checkout_clicked", "purchase_return"):
                        record_telemetry_event(payload)
                    if ev_name not in ("lead_capture", "lead_submitted", "purchase_return"):
                        continue
                    prof = payload.get("profile") or {}
                    full_name = prof.get("fullName", "").strip()
                    dob = prof.get("birthDate", "").strip()
                    email_addr = prof.get("email", "").strip()
                    lang = payload.get("lang", "en")
                    ts = payload.get("timestamp")
                    utm_data = extract_utm_from_payload(payload)
                    if full_name and dob and email_addr and "@" in email_addr:
                        if email_addr.lower().endswith("@sovereign5.com") or email_addr.lower() == "test@example.com":
                            continue
                        process_lead(
                            full_name,
                            dob,
                            email_addr,
                            lang=lang,
                            timestamp=ts,
                            force_send=False,
                            utm=utm_data,
                        )
                        count += 1
                except Exception:
                    continue
    except Exception as e:
        print(f"  [Notice] Cloud relay poll error: {e}", flush=True)

    # Also process any due 24h / 48h follow-up emails and refresh dashboard
    check_and_send_scheduled_followups()
    update_obsidian_dashboard()
    return count


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

        try:
            payload = json.loads(raw)
            record_telemetry_event(payload)
            ev_name = str(payload.get("event_type") or payload.get("event") or "").strip().lower()
            prof = payload.get("profile") or {}
            full_name = prof.get("fullName", "").strip()
            dob = prof.get("birthDate", "").strip()
            email_addr = prof.get("email", "").strip()
            lang = payload.get("lang", "en")
            ts = payload.get("timestamp")
            utm_data = extract_utm_from_payload(payload)
            if ev_name in ("lead_capture", "lead_submitted", "purchase_return", "") and full_name and dob and email_addr and "@" in email_addr:
                if not email_addr.lower().endswith("@sovereign5.com") and email_addr.lower() != "test@example.com":
                    process_lead(
                        full_name,
                        dob,
                        email_addr,
                        lang=lang,
                        timestamp=ts,
                        force_send=False,
                        utm=utm_data,
                    )
        except Exception as e:
            print(f"  [Webhook Error] {e}", flush=True)


def run_daemon(port: int = 8788, poll_interval: int = 15):
    print("=" * 68, flush=True)
    print(f"   SOVEREIGN 5-SYSTEM LEAD CAPTURE & EMAIL WORKER DAEMON (Port {port})", flush=True)
    print(f"   Cloud Relay Topic: {NTFY_TOPIC} (Polling every {poll_interval}s)", flush=True)
    print("=" * 68, flush=True)

    server = HTTPServer(("127.0.0.1", port), WebhookHandler)
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()

    while True:
        poll_cloud_relay_once()
        time.sleep(poll_interval)


def main():
    parser = argparse.ArgumentParser(description="Sovereign 5-System Lead Capture & 3-Part Email Sequence Worker")
    parser.add_argument("--backfill-lead", action="store_true", help="Manually process & email a specific lead")
    parser.add_argument("--name", type=str, help="Full Birth Name for backfill")
    parser.add_argument("--dob", type=str, help="Date of Birth (YYYY-MM-DD or MM/DD/YYYY)")
    parser.add_argument("--email", type=str, help="Email address for backfill")
    parser.add_argument("--lang", type=str, default="en", help="Language (en or es)")
    parser.add_argument("--utm-source", type=str, default="", help="Optional utm_source")
    parser.add_argument("--utm-medium", type=str, default="", help="Optional utm_medium")
    parser.add_argument("--utm-campaign", type=str, default="", help="Optional utm_campaign")
    parser.add_argument("--cohort", type=str, default="", help="Optional cohort (e.g., B)")
    parser.add_argument("--force", action="store_true", help="Force re-sending email even if already in dedup store")
    parser.add_argument("--poll-once", action="store_true", help="Poll cloud relay + check 24h/48h followups once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuous webhook & cloud relay polling daemon")
    args = parser.parse_args()

    if args.backfill_lead:
        if not (args.name and args.dob and args.email):
            print("Error: --backfill-lead requires --name, --dob, and --email")
            sys.exit(1)
        cli_utm = {
            k: v
            for k, v in {
                "utm_source": args.utm_source,
                "utm_medium": args.utm_medium,
                "utm_campaign": args.utm_campaign,
                "cohort": args.cohort,
            }.items()
            if v
        }
        res = process_lead(
            args.name,
            args.dob,
            args.email,
            lang=args.lang,
            force_send=args.force,
            utm=cli_utm,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    if args.poll_once:
        n = poll_cloud_relay_once()
        print(f"Polled cloud relay: processed {n} new leads.")
        return

    if args.daemon:
        run_daemon()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
