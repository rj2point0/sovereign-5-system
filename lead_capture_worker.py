#!/usr/bin/env python3
"""
=============================================================================
SOVEREIGN 5-SYSTEM · REAL-TIME LEAD CAPTURE & LUXURY EMAIL FOLLOW-UP WORKER
lead_capture_worker.py
-----------------------------------------------------------------------------
1. Captures leads submitted from https://rj2point0.github.io/sovereign-5-system/
   via public cloud relay (ntfy.sh/sovereign_5_leads_mvv_991214754) and local
   HTTP webhook (http://127.0.0.1:8788/webhook).
2. Computes exact 5-System Numerology numbers (matching engine.js 100%).
3. Logs every lead permanently to:
   - G:\\My Drive\\5_System_Numerology_MVP\\leads_captured.csv
   - c:\\Users\\User\\5numsystem\\leads_captured.csv
   - G:\\My Drive\\MVV_Memory_Vault\\03-Projects\\Leads_Captured_Dashboard.md
   - Supabase PostgreSQL (`public.numerology_leads`)
4. Sends an instant, luxury Obsidian & Gold HTML follow-up email via
   Google Workspace SMTP (adamvega@megavegaventures.com) with the user's
   Big 3 Master Overlap Numbers and $37 Dossier Unlock + Teaser Session links.
=============================================================================
"""

import argparse
import csv
import html
import json
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
SENDER_DISPLAY = "Sacred Number Blueprint · Sovereign 5-System <adamvega@megavegaventures.com>"

STRIPE_BASE_URL = "https://buy.stripe.com/6oU7sLek90MdbVechV38401"
STRIPE_BUMP_URL = "https://buy.stripe.com/eVq28r2Br9iJe3mbdR38402"
APP_BASE_URL = "https://rj2point0.github.io/sovereign-5-system/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CSV_PATH = os.path.join(BASE_DIR, "leads_captured.csv")
GDRIVE_CSV_PATH = r"G:\My Drive\5_System_Numerology_MVP\leads_captured.csv"
OBSIDIAN_DASHBOARD_PATH = r"G:\My Drive\MVV_Memory_Vault\03-Projects\Leads_Captured_Dashboard.md"
PROCESSED_LEADS_PATH = os.path.join(BASE_DIR, "processed_leads_state.json")

CSV_COLUMNS = [
    "timestamp",
    "name",
    "dob",
    "email",
    "lang",
    "top_3_overlap_numbers",
    "life_path",
    "vedic_moolank",
    "chaldean_name",
    "email_sent",
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
    1: {"name": "The Sovereign Pioneer", "keywords": "Command · Originality · Will", "summary": "You are wired to initiate, lead from the front, and carve original paths where consensus hesitates."},
    2: {"name": "The Diplomatic Oracle", "keywords": "Intuition · Resonance · Alliance", "summary": "You perceive the unspoken currents between people, turning subtle emotional intelligence into strategic harmony."},
    3: {"name": "The Magnetic Catalyst", "keywords": "Expression · Synthesis · Charisma", "summary": "Your voice and creative fire translate complex truths into magnetic ideas that move rooms and markets."},
    4: {"name": "The Master Architect", "keywords": "Structure · Endurance · Foundation", "summary": "You turn abstract vision into permanent, load-bearing systems, wealth structures, and unshakable order."},
    5: {"name": "The Mercurial Alchemist", "keywords": "Velocity · Freedom · Pivot", "summary": "You thrive at the intersection of rapid change, sensory mastery, and high-leverage adaptability."},
    6: {"name": "The Sovereign Guardian", "keywords": "Magnetism · Sanctuary · Devotion", "summary": "You command through beauty, loyalty, and protective stewardship over your family, capital, and legacy."},
    7: {"name": "The Mystic Strategist", "keywords": "Pattern Analysis · Sovereignty · Depth", "summary": "You see beneath surface noise to decode the hidden mathematical and psychological laws governing outcomes."},
    8: {"name": "The Executive Magnate", "keywords": "Capital · Authority · Scale", "summary": "You are built for high-stakes material execution, asymmetric wealth creation, and institutional command."},
    9: {"name": "The Sage-Warrior", "keywords": "Mastery · Completion · Legacy", "summary": "You synthesize the wisdom of all preceding numbers into panoramic vision, decisive action, and lasting impact."},
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


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(int(n))))


def reduce_num(n: int) -> int:
    x = abs(int(n))
    while x > 9:
        x = digit_sum(x)
    return x


def compound_of(n: int, cap: int = 99) -> int:
    c = abs(int(n))
    while c > cap:
        c = digit_sum(c)
    return c


def make_num(raw: int, cap: int = 99) -> Dict[str, Any]:
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

    # 1. Pythagorean
    lp = make_num(reduce_num(y) + reduce_num(m) + reduce_num(d))
    expr = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters))
    soul = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters if ch in VOWELS))
    pers = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in all_letters if ch not in VOWELS))
    first_cons = make_num(sum(PYTHAGOREAN_MAP.get(ch, 0) for ch in first_word if ch not in VOWELS))

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
        if n in kab_nums:
            sys_set.add("Kabbalistic")
        first_idx = next((idx for idx, s in enumerate(filtered) if s[3] == n), 99)
        tally[n] = {
            "number": n,
            "archetype": ARCHETYPES_EN[n]["name"],
            "keywords": ARCHETYPES_EN[n]["keywords"],
            "summary": ARCHETYPES_EN[n]["summary"],
            "count": len(hits),
            "systems": [s for s in SYSTEM_ORDER if s in sys_set],
            "sources": [h[1] for h in hits],
            "firstIndex": first_idx,
            "loShuCount": counts[n],
        }

    ranking = sorted(
        tally.values(),
        key=lambda a: (-a["count"], -len(a["systems"]), -a["loShuCount"], a["firstIndex"], a["number"])
    )
    anchors = ranking[:3]

    return {
        "name": " ".join(w.capitalize() for w in full_name.strip().split()),
        "dob": iso_dob,
        "top_3_overlap_numbers": ", ".join(str(a["number"]) for a in anchors),
        "anchors": anchors,
        "life_path": lp["display"],
        "expression": expr["display"],
        "soul_urge": soul["display"],
        "vedic_moolank": f"{moolank_val} ({VEDIC_PLANETS.get(moolank_val, 'Surya')})",
        "vedic_bhagyank": f"{bhagyank_val} ({VEDIC_PLANETS.get(bhagyank_val, 'Surya')})",
        "chaldean_name": chal_total["display"],
        "dominant_element": f"{dom_element} (#{dom_number})",
        "total_sources": len(filtered),
    }


# -----------------------------------------------------------------------------
# LUXURY HTML FOLLOW-UP EMAIL BUILDER & SENDER
# -----------------------------------------------------------------------------
def build_luxury_followup_email(lead: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (subject, plain_text, html_body) for the captured lead."""
    name = lead["name"]
    first_name = name.split()[0] if name else "Friend"
    dob = lead["dob"]
    email_addr = lead["email"]
    calc = lead["calc"]
    anchors = calc["anchors"]
    a1, a2, a3 = anchors[0], anchors[1], anchors[2]

    # Format birth date nicely
    try:
        dt_obj = datetime.strptime(dob, "%Y-%m-%d")
        dob_formatted = dt_obj.strftime("%B %d, %Y")
    except Exception:
        dob_formatted = dob

    teaser_url = (
        f"{APP_BASE_URL}?name={urllib.parse.quote(name)}"
        f"&dob={urllib.parse.quote(dob)}"
        f"&email={urllib.parse.quote(email_addr)}&view=teaser"
    )
    stripe_url = f"{STRIPE_BASE_URL}?prefilled_email={urllib.parse.quote(email_addr)}"

    subject = f"✦ Your 5-System Numerology Code: Master Overlap #{a1['number']} ({a1['archetype']})"

    plain_text = (
        f"THE SOVEREIGN 5-SYSTEM BLUEPRINT\n"
        f"Decoded for {name} (Born {dob_formatted})\n"
        f"============================================================\n\n"
        f"{first_name}, we cross-referenced your full birth name and birth date across all 5 ancient mathematical traditions "
        f"(Pythagorean, Babylonian Chaldean, Kabbalistic Tree of Life, Vedic Planetary Council & Chinese Lo Shu).\n\n"
        f"YOUR BIG THREE MASTER OVERLAP NUMBERS:\n"
        f"1. PRIMARY SIGNATURE ANCHOR: #{a1['number']} — {a1['archetype']}\n"
        f"   Appeared {a1['count']} times across {len(a1['systems'])} systems ({', '.join(a1['systems'])})\n"
        f"   {a1['summary']}\n\n"
        f"2. WEALTH & STRATEGY ENGINE: #{a2['number']} — {a2['archetype']}\n"
        f"   Appeared {a2['count']} times across {', '.join(a2['systems'])}\n\n"
        f"3. SANCTUARY & STRUCTURAL FOUNDATION: #{a3['number']} — {a3['archetype']}\n"
        f"   Appeared {a3['count']} times across {', '.join(a3['systems'])}\n\n"
        f"CROSS-SYSTEM SNAPSHOT:\n"
        f"• Pythagorean Life Path: {calc['life_path']}\n"
        f"• Expression / Destiny: {calc['expression']}\n"
        f"• Soul Urge: {calc['soul_urge']}\n"
        f"• Vedic Planetary Moolank: {calc['vedic_moolank']}\n"
        f"• Chaldean Name Vibration: {calc['chaldean_name']}\n\n"
        f"UNLOCK YOUR FULL 20-PAGE SOVEREIGN DOSSIER ($37):\n"
        f"{stripe_url}\n\n"
        f"RETURN TO YOUR INTERACTIVE 5-SYSTEM TEASER:\n"
        f"{teaser_url}\n\n"
        f"— Sacred Number Blueprint · Sovereign 5-System\n"
    )

    a1_systems_badges = "".join(
        f'<span style="display:inline-block;margin:3px 4px;padding:4px 10px;border-radius:99px;'
        f'background:#1c1910;border:1px solid rgba(212,175,55,0.45);color:#F3E5AB;font-size:11px;'
        f'letter-spacing:1px;text-transform:uppercase;">{html.escape(s)}</span>'
        for s in a1["systems"]
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#0A0A0C;font-family:'Georgia',serif;color:#F5F5F7;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0A0A0C;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:600px;background-color:#121318;border:1px solid rgba(212,175,55,0.38);border-radius:18px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,0.85);">
          
          <!-- Header -->
          <tr>
            <td align="center" style="padding:28px 24px 18px;border-bottom:1px solid rgba(212,175,55,0.2);background:radial-gradient(circle at 50% 0%,#241f11,#121318 75%);">
              <div style="font-family:'Arial',sans-serif;font-size:11px;letter-spacing:3.5px;text-transform:uppercase;color:#D4AF37;font-weight:700;">
                ✦ SOVEREIGN · 5 ANCIENT SYSTEMS ✦
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
            <td align="center" style="padding:28px 24px 20px;">
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
                        ({a2['count']}× across {', '.join(a2['systems'])})
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
                        ({a3['count']}× across {', '.join(a3['systems'])})
                      </span>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 5-System Snapshot Grid -->
          <tr>
            <td style="padding:0 24px 24px;">
              <div style="font-family:'Arial',sans-serif;font-size:10px;letter-spacing:2.2px;text-transform:uppercase;color:#A1A1AA;margin-bottom:10px;text-align:center;">
                YOUR 5-SYSTEM MATHEMATICAL SNAPSHOT
              </div>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="8" border="0" style="font-family:'Arial',sans-serif;font-size:13px;background-color:#0D0E12;border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">Pythagorean Life Path</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['life_path'])}</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">Pythagorean Expression / Destiny</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['expression'])}</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">Babylonian Chaldean Full Name</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['chaldean_name'])}</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;border-bottom:1px solid rgba(255,255,255,0.06);">Vedic Planetary Driver (Moolank)</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.06);">{html.escape(calc['vedic_moolank'])}</td>
                </tr>
                <tr>
                  <td style="color:#A1A1AA;">Lo Shu Dominant Element</td>
                  <td align="right" style="color:#F3E5AB;font-weight:700;">{html.escape(calc.get('dominant_element', 'Earth'))}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Primary CTA Buttons -->
          <tr>
            <td align="center" style="padding:4px 24px 28px;">
              <p style="margin:0 0 16px;font-family:'Arial',sans-serif;font-size:13px;line-height:1.55;color:#D4D4D8;">
                Your free teaser only unlocks System I. Unlock your complete <strong>20-Page Luxury Sovereign Dossier PDF</strong> (including your 5-Ring Convergence Mandala, 15-Point Calculation Ledger, Somatic Health Architecture, and Rosicrucian 52-Day Cycles):
              </p>
              <a href="{stripe_url}" style="display:inline-block;background:linear-gradient(135deg,#F3E5AB 0%,#D4AF37 50%,#AA820A 100%);color:#141108;font-family:'Arial',sans-serif;font-size:14px;font-weight:800;text-decoration:none;padding:15px 28px;border-radius:12px;letter-spacing:0.6px;text-transform:uppercase;margin-bottom:12px;">
                ✦ Unlock My Full 20-Page Sovereign Dossier ($37)
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
              © {datetime.now().year} Sovereign 5-System · Sacred Number Blueprint (@sacrednumberblueprint)<br>
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


def send_followup_email(lead: Dict[str, Any]) -> bool:
    """Dispatches the luxury HTML follow-up email via Google Workspace SMTP."""
    recipient = lead["email"].strip()
    if not recipient or "@" not in recipient:
        return False

    subject, plain_text, html_body = build_luxury_followup_email(lead)

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
        print(f"✓ Luxury HTML Follow-Up Email sent to {recipient} (and copy to {SMTP_USER})", flush=True)
        return True
    except Exception as e:
        print(f"✗ SMTP send error for {recipient}: {e}", flush=True)
        return False


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


def append_lead_to_csv_and_obsidian(lead: Dict[str, Any], email_sent: bool):
    calc = lead["calc"]
    row = {
        "timestamp": lead["timestamp"],
        "name": lead["name"],
        "dob": lead["dob"],
        "email": lead["email"],
        "lang": lead.get("lang", "en"),
        "top_3_overlap_numbers": calc["top_3_overlap_numbers"],
        "life_path": calc["life_path"],
        "vedic_moolank": calc["vedic_moolank"],
        "chaldean_name": calc["chaldean_name"],
        "email_sent": "YES" if email_sent else "NO",
    }

    for csv_path in [LOCAL_CSV_PATH, GDRIVE_CSV_PATH]:
        try:
            parent = os.path.dirname(csv_path)
            if parent and not os.path.exists(parent):
                continue
            file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            print(f"✓ Lead appended to CSV: {csv_path}", flush=True)
        except Exception as e:
            print(f"  [Notice] Could not write CSV {csv_path}: {e}", flush=True)

    # Also regenerate Obsidian Markdown Dashboard from LOCAL_CSV_PATH
    try:
        rows = []
        if os.path.exists(LOCAL_CSV_PATH):
            with open(LOCAL_CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        if os.path.exists(os.path.dirname(OBSIDIAN_DASHBOARD_PATH)):
            md_lines = [
                "---",
                "title: Sacred Number Blueprint — Captured Leads Dashboard",
                "project: Sacred Number Blueprint (@sacrednumberblueprint)",
                f"date_updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"total_leads: {len(rows)}",
                "tags:",
                "  - leads",
                "  - sacred-number-blueprint",
                "  - funnel-crm",
                "---",
                "",
                "# 📬 Sacred Number Blueprint — Live Captured Leads Dashboard",
                "",
                "> [!INFO] Central Lead Capture & Automated Email Log",
                "> Every visitor who submits their Name, Birth Date, and Email on `https://rj2point0.github.io/sovereign-5-system/` is logged below, synced to `G:\\My Drive\\5_System_Numerology_MVP\\leads_captured.csv` and Supabase (`public.numerology_leads`), and automatically sent their personalized 5-System HTML Teaser Email.",
                "",
                "| Timestamp (UTC) | Full Birth Name | DOB | Email | Lang | Big 3 Overlap Anchors | Life Path | Vedic Moolank | Chaldean Name | Email Sent |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ]
            for r in reversed(rows):
                md_lines.append(
                    f"| `{r.get('timestamp', '')[:19]}` | **{r.get('name', '')}** | `{r.get('dob', '')}` | `{r.get('email', '')}` | `{r.get('lang', 'en')}` | **{r.get('top_3_overlap_numbers', '')}** | `{r.get('life_path', '')}` | `{r.get('vedic_moolank', '')}` | `{r.get('chaldean_name', '')}` | `{r.get('email_sent', '')}` |"
                )
            md_lines.append("")
            with open(OBSIDIAN_DASHBOARD_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))
            print(f"✓ Obsidian Leads Dashboard updated: {OBSIDIAN_DASHBOARD_PATH}", flush=True)
    except Exception as e:
        print(f"  [Notice] Could not update Obsidian Leads Dashboard: {e}", flush=True)


# -----------------------------------------------------------------------------
# DEDUPLICATION & LEAD PROCESSOR
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
) -> Dict[str, Any]:
    iso_dob = normalize_dob(dob_str)
    clean_email = email_addr.strip()
    clean_name = " ".join(w.capitalize() for w in full_name.strip().split())
    dedup_key = f"{clean_email.lower()}::{iso_dob}::{clean_name.lower()}"

    processed = load_processed_state()
    if not force_send and dedup_key in processed:
        print(f"  [Skip] Lead already processed & emailed: {clean_name} ({clean_email})", flush=True)
        return processed[dedup_key]

    calc = calculate_5_systems(clean_name, iso_dob)
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    lead_record = {
        "timestamp": ts,
        "name": clean_name,
        "dob": iso_dob,
        "email": clean_email,
        "lang": lang or "en",
        "calc": calc,
    }

    email_sent = send_followup_email(lead_record)
    append_lead_to_csv_and_obsidian(lead_record, email_sent)
    save_lead_to_supabase(lead_record, email_sent)

    processed[dedup_key] = {
        "timestamp": ts,
        "name": clean_name,
        "dob": iso_dob,
        "email": clean_email,
        "top_3_overlap_numbers": calc["top_3_overlap_numbers"],
        "life_path": calc["life_path"],
        "vedic_moolank": calc["vedic_moolank"],
        "chaldean_name": calc["chaldean_name"],
        "email_sent": email_sent,
    }
    save_processed_state(processed)
    return processed[dedup_key]


def poll_cloud_relay_once() -> int:
    """Polls ntfy.sh cloud relay for any new lead_capture payloads from mobile/desktop visitors."""
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
                    if payload.get("event") not in ("lead_capture", "purchase_return"):
                        continue
                    prof = payload.get("profile") or {}
                    full_name = prof.get("fullName", "").strip()
                    dob = prof.get("birthDate", "").strip()
                    email_addr = prof.get("email", "").strip()
                    lang = payload.get("lang", "en")
                    ts = payload.get("timestamp")
                    if full_name and dob and email_addr and "@" in email_addr:
                        # Skip automated test dummy emails if needed, except real user emails
                        if email_addr.lower().endswith("@sovereign5.com") or email_addr.lower() == "test@example.com":
                            continue
                        process_lead(full_name, dob, email_addr, lang=lang, timestamp=ts, force_send=False)
                        count += 1
                except Exception:
                    continue
    except Exception as e:
        print(f"  [Notice] Cloud relay poll error: {e}", flush=True)
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
            prof = payload.get("profile") or {}
            full_name = prof.get("fullName", "").strip()
            dob = prof.get("birthDate", "").strip()
            email_addr = prof.get("email", "").strip()
            lang = payload.get("lang", "en")
            ts = payload.get("timestamp")
            if full_name and dob and email_addr and "@" in email_addr:
                if not email_addr.lower().endswith("@sovereign5.com") and email_addr.lower() != "test@example.com":
                    process_lead(full_name, dob, email_addr, lang=lang, timestamp=ts, force_send=False)
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
    parser = argparse.ArgumentParser(description="Sovereign 5-System Lead Capture & Email Follow-Up Worker")
    parser.add_argument("--backfill-lead", action="store_true", help="Manually process & email a specific lead")
    parser.add_argument("--name", type=str, help="Full Birth Name for backfill")
    parser.add_argument("--dob", type=str, help="Date of Birth (YYYY-MM-DD or MM/DD/YYYY)")
    parser.add_argument("--email", type=str, help="Email address for backfill")
    parser.add_argument("--lang", type=str, default="en", help="Language (en or es)")
    parser.add_argument("--force", action="store_true", help="Force re-sending email even if already in dedup store")
    parser.add_argument("--poll-once", action="store_true", help="Poll cloud relay once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuous webhook & cloud relay polling daemon")
    args = parser.parse_args()

    if args.backfill_lead:
        if not (args.name and args.dob and args.email):
            print("Error: --backfill-lead requires --name, --dob, and --email")
            sys.exit(1)
        res = process_lead(args.name, args.dob, args.email, lang=args.lang, force_send=args.force)
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
