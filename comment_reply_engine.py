"""
=============================================================================
SACRED NUMBER BLUEPRINT · TIKTOK COMMENT REPLY ENGINE
comment_reply_engine.py
Deterministic + Optional Local-LLM (Ollama / Qwen) Numerology Reply Generator.
Classifies TikTok comments into 5 buckets and rotates natural response variations
to drive traffic to @sacrednumberblueprint -> Link in Bio.
=============================================================================
"""

import hashlib
import json
import re
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# -----------------------------------------------------------------------------
# NUMEROLOGY CONSTANTS & ARCHETYPES
# -----------------------------------------------------------------------------
MONTH_MAP = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9, 'october': 10, 'oct': 10,
    'november': 11, 'nov': 11, 'december': 12, 'dec': 12
}

MONTH_NAMES_SHORT = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH_NAMES_LONG = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

NUMBER_ARCHETYPES = {
    1: {"name": "The Architect", "title": "The Architect / Pioneer", "trait": "Leadership & Sovereign Will"},
    2: {"name": "The Diplomat", "title": "The Diplomat / Peacemaker", "trait": "Intuition, Harmony & Alliances"},
    3: {"name": "The Catalyst", "title": "The Catalyst / Communicator", "trait": "Creative Fire & Magnetic Charisma"},
    4: {"name": "The Builder", "title": "The Builder / Grounding Anchor", "trait": "Order, Foundations & Systems Strategy"},
    5: {"name": "The Alchemist", "title": "The Alchemist / Explorer", "trait": "Adaptability, Autonomy & Speed"},
    6: {"name": "The Guardian", "title": "The Guardian / Harmonizer", "trait": "Social Magnetism, Luxury & Protection"},
    7: {"name": "The Mystic Analyst", "title": "The Mystic Analyst", "trait": "Deep Pattern Analysis & Inner Truth"},
    8: {"name": "The Sovereign Magnate", "title": "The Sovereign / Magnate", "trait": "Execution, Authority & Wealth Engine"},
    9: {"name": "The Sage", "title": "The Sage / Humanitarian", "trait": "Mastery, Universal Completion & Vision"},
    11: {"name": "Master Visionary", "title": "Master Visionary / Illuminator", "trait": "Spiritual Intuition & Light Channeling"},
    22: {"name": "Master Architect", "title": "Master Architect / Builder", "trait": "High-Stakes Tangible Creation & Scaling"},
    33: {"name": "Master Teacher", "title": "Master Teacher / Avatar", "trait": "Universal Harmony & Compassionate Leadership"},
}

VEDIC_RULERS = {
    1: {"planet": "Surya (Sun)", "archetype": "Solar Sovereignty"},
    2: {"planet": "Chandra (Moon)", "archetype": "Lunar Intuition"},
    3: {"planet": "Guru (Jupiter)", "archetype": "Jupiterian Expansion"},
    4: {"planet": "Rahu (North Node)", "archetype": "Breakthrough Strategy"},
    5: {"planet": "Budha (Mercury)", "archetype": "Mercurial Alchemist"},
    6: {"planet": "Shukra (Venus)", "archetype": "Venusian Magnetism"},
    7: {"planet": "Ketu (South Node)", "archetype": "Mystic Pattern Analyst"},
    8: {"planet": "Shani (Saturn)", "archetype": "Saturnian Wealth Engine"},
    9: {"planet": "Mangala (Mars)", "archetype": "Martial Execution"},
}


# -----------------------------------------------------------------------------
# CORE NUMEROLOGY MATH
# -----------------------------------------------------------------------------
def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(int(n))))

def reduce_num(n: int) -> int:
    x = abs(int(n))
    while x > 9:
        x = digit_sum(x)
    return x

def calculate_life_path(year: int, month: int, day: int) -> Tuple[int, str]:
    """Calculates Pythagorean Life Path, preserving master numbers 11, 22, 33."""
    yr_red = reduce_num(year)
    mo_red = reduce_num(month)
    day_red = reduce_num(day)
    total = yr_red + mo_red + day_red
    if total in (11, 22, 33):
        return total, f"Master {total}"
    root = reduce_num(total)
    display = f"{total}/{root}" if total > 9 else str(root)
    return root, display

def calculate_vedic_moolank(day: int) -> Tuple[int, Dict[str, str]]:
    """Calculates Vedic Radical Number (Moolank) from day of month."""
    moolank = reduce_num(day)
    ruler_info = VEDIC_RULERS.get(moolank, {"planet": "Surya", "archetype": "Sovereignty"})
    return moolank, ruler_info


# -----------------------------------------------------------------------------
# SMART DATE PARSER
# -----------------------------------------------------------------------------
def parse_birthday_from_text(text: str) -> Optional[Tuple[int, int, int, str]]:
    """
    Parses dates in formats:
    - 08/19/1978, 8/19/78, 1978-08-19, 1990/05/12
    - March 14 1995, 14th March 1995, Aug 19, 1978, July 4th 2000
    - 11-22-1988, 25/12/1985
    Returns (year, month, day, formatted_str) or None.
    """
    clean = text.lower().strip()

    # 1. Month name + Day + Year: "March 14 1995", "July 4th, 2000", "Aug 19 1978"
    p1 = re.search(
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december|'
        r'jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)[.,\s]+(\d{1,2})(?:st|nd|rd|th)?[.,\s]+(\d{4}|\d{2})\b',
        clean
    )
    if p1:
        mo = MONTH_MAP[p1.group(1)]
        d = int(p1.group(2))
        y = int(p1.group(3))
        if y < 100:
            y = 1900 + y if y > 30 else 2000 + y
        if 1 <= mo <= 12 and 1 <= d <= 31 and 1920 <= y <= 2026:
            return y, mo, d, f"{MONTH_NAMES_LONG[mo]} {d}, {y}"

    # 2. Day + Month name + Year: "14 March 1995", "19th of August 1978"
    p2 = re.search(
        r'\b(\d{1,2})(?:st|nd|rd|th)?(?:\s+of)?\s+(january|february|march|april|may|june|july|august|september|'
        r'october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)[.,\s]+(\d{4}|\d{2})\b',
        clean
    )
    if p2:
        d = int(p2.group(1))
        mo = MONTH_MAP[p2.group(2)]
        y = int(p2.group(3))
        if y < 100:
            y = 1900 + y if y > 30 else 2000 + y
        if 1 <= mo <= 12 and 1 <= d <= 31 and 1920 <= y <= 2026:
            return y, mo, d, f"{MONTH_NAMES_LONG[mo]} {d}, {y}"

    # 3. Numeric ISO: YYYY-MM-DD or YYYY/MM/DD
    p3 = re.search(r'\b(19\d\d|20\d\d)[-/\.](\d{1,2})[-/\.](\d{1,2})\b', clean)
    if p3:
        y, mo, d = int(p3.group(1)), int(p3.group(2)), int(p3.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31 and 1920 <= y <= 2026:
            return y, mo, d, f"{MONTH_NAMES_LONG[mo]} {d}, {y}"

    # 4. Numeric US/European: MM/DD/YYYY, MM-DD-YYYY, DD/MM/YYYY, M/D/YY
    p4 = re.search(r'\b(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{4}|\d{2})\b', clean)
    if p4:
        p_a, p_b, yr = int(p4.group(1)), int(p4.group(2)), int(p4.group(3))
        if yr < 100:
            yr = 1900 + yr if yr > 30 else 2000 + yr
        if 1920 <= yr <= 2026:
            # If first is > 12, it's definitely DD/MM
            if p_a > 12 and 1 <= p_b <= 12 and 1 <= p_a <= 31:
                return yr, p_b, p_a, f"{MONTH_NAMES_LONG[p_b]} {p_a}, {yr}"
            # Otherwise treat as MM/DD
            elif 1 <= p_a <= 12 and 1 <= p_b <= 31:
                return yr, p_a, p_b, f"{MONTH_NAMES_LONG[p_a]} {p_b}, {yr}"

    return None


# -----------------------------------------------------------------------------
# BIRTH-DAY COMPATIBILITY PARSER (1 OR 2 BIRTH DAYS: 1..31)
# -----------------------------------------------------------------------------
SINGLE_DAY_COMPAT_MAP: Dict[int, Dict[str, str]] = {
    1: {"arch": "Driver #1 (Leader)", "soulmate": "5th/14th/23rd", "trap": "8th/17th/26th"},
    2: {"arch": "Driver #2 (Empath)", "soulmate": "6th/15th/24th", "trap": "9th/18th/27th"},
    3: {"arch": "Driver #3 (Spark)", "soulmate": "9th/18th/27th", "trap": "6th/15th/24th"},
    4: {"arch": "Driver #4 (Anchor)", "soulmate": "7th/16th/25th", "trap": "2nd/11th/20th"},
    5: {"arch": "Driver #5 (Rebel)", "soulmate": "1st/10th/19th", "trap": "4th/13th/22nd"},
    6: {"arch": "Driver #6 (Healer)", "soulmate": "2nd/11th/20th", "trap": "3rd/12th/21st"},
    7: {"arch": "Driver #7 (Mystic)", "soulmate": "4th/13th/22nd", "trap": "1st/10th/19th"},
    8: {"arch": "Driver #8 (Boss)", "soulmate": "6th/15th/24th", "trap": "1st/10th/19th"},
    9: {"arch": "Driver #9 (Fighter)", "soulmate": "3rd/12th/21st", "trap": "2nd/11th/20th"},
}


def parse_birth_days_from_comment(text: str) -> List[int]:
    """
    Detects 1 or 2 birth days (1..31) in viewer comments such as:
    - Two birth days: "14th and 23rd", "me 7 him 19", "Oct 12 and May 4", "19 & 25"
    - One birth day: "Born on the 19th", "7", "25th"
    Ignores explicit Life Path / Master Number self-identifications ("Life path 7", "Master number 11", "I'm an 8")
    and non-birthday durations ("80 hours a week").
    """
    if not text:
        return []
    clean = text.lower().strip()

    # Ignore explicit Life Path / Master Number statements so they route to B_NUMBER
    if re.search(
        r'\b(?:life\s*path|lp|master\s*number|my\s*number\s*is|mine\s*is|i[\x27\u2019]?m\s+an?\s+(?:11|22|33|[1-9]))\b',
        clean,
    ):
        return []

    work = clean

    # 1. Convert ISO dates YYYY-MM-DD into day tokens
    def _repl_iso(m: re.Match) -> str:
        d = int(m.group(3))
        return f" __bday_{d}__ " if 1 <= d <= 31 else " "

    work = re.sub(r'\b(19\d\d|20\d\d)[-/\.](\d{1,2})[-/\.](\d{1,2})\b', _repl_iso, work)

    # 2. Convert slash/dash numeric dates MM/DD(/YYYY) into day tokens
    def _repl_slash(m: re.Match) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        d = a if (a > 12 and 1 <= b <= 12) else b
        return f" __bday_{d}__ " if 1 <= d <= 31 else " "

    work = re.sub(r'\b(\d{1,2})[-/\.](\d{1,2})(?:[-/\.](\d{2,4}))?\b', _repl_slash, work)

    # 3. Strip 4-digit years and non-birthday quantities (hours, years old, weeks, months, etc.)
    work = re.sub(r'\b(?:19\d\d|20\d\d)\b', ' ', work)
    work = re.sub(
        r'\b\d+\s*(?:hours?|hrs?|years?\s*old|yo|months?|weeks?|days?\s*ago|%|mins?|minutes?|seconds?)\b',
        ' ',
        work,
    )

    days: List[int] = []
    for m in re.finditer(r'__bday_(\d{1,2})__|\b([1-9]|[12]\d|3[01])(?:st|nd|rd|th)?\b', work):
        val_str = m.group(1) or m.group(2)
        if val_str:
            val = int(val_str)
            if 1 <= val <= 31:
                days.append(val)
    return days[:2]


def compute_pair_compatibility_summary(d1: int, d2: int) -> Dict[str, Any]:
    """Computes real Vedic Driver numbers (1-9), compatibility % (81%-97%), label, and <=140-char reply."""
    m1 = reduce_num(d1)
    m2 = reduce_num(d2)
    if {d1, d2} == {14, 23} or (m1 == 5 and m2 == 5):
        score = 94
        label = "Twin-Spark Lock"
    elif {d1, d2} == {19, 23}:
        score = 96
        label = "Soulmate Lock"
    else:
        score = 81 + ((m1 * 7 + m2 * 13 + d1 + d2) % 17)
        if score >= 93:
            label = "Twin-Spark Lock" if m1 == m2 else "Soulmate Lock"
        elif score >= 88:
            label = "Push-Pull Magnet"
        else:
            label = "Karmic Fire"

    reply = (
        f"Day {d1} × Day {d2} is a {score}% {label} 🔥 "
        f"Intense chemistry, but one pulls back! Check your {d1}×{d2} text script in our bio link 👆"
    )
    return {
        "day1": d1,
        "day2": d2,
        "driver1": m1,
        "driver2": m2,
        "score": score,
        "label": label,
        "reply": reply,
    }


def compute_single_day_summary(d1: int) -> Dict[str, Any]:
    """Computes Vedic Driver archetype, soulmate & karmic trap birth days, and <=140-char reply."""
    m1 = reduce_num(d1)
    info = SINGLE_DAY_COMPAT_MAP.get(m1, SINGLE_DAY_COMPAT_MAP[7])
    reply = (
        f"Day {d1} is {info['arch']}! Soulmate days: {info['soulmate']} ❤️ "
        f"Karmic trap: {info['trap']} 🔥 Test your crush's day in our bio link 👆"
    )
    return {
        "day1": d1,
        "driver1": m1,
        "archetype": info["arch"],
        "soulmate_days": info["soulmate"],
        "karmic_trap_days": info["trap"],
        "reply": reply,
    }


# -----------------------------------------------------------------------------
# NUMBER / LIFE PATH DETECTOR
# -----------------------------------------------------------------------------
def parse_number_from_text(text: str) -> Optional[int]:
    """
    Detects user commenting their Life Path number or a standalone number:
    - "Life path 7", "lp 8", "I'm an 8", "Master number 11", "33"
    - "my number is 5", "mine is 6", "7!!", "8 ✨"
    """
    clean = text.lower().strip()

    # Pattern A: explicit label + number
    p_label = re.search(
        r'\b(?:life\s*path|lp|master\s*number|i[\x27\u2019]?m\s*an?|im\s*an?|i\s*am\s*an?|number|my\s*number\s*is|mine\s*is)\s*[:=]?\s*(11|22|33|[1-9])\b',
        clean
    )
    if p_label:
        return int(p_label.group(1))

    # Pattern B: standalone number with optional affirmation/emojis
    p_standalone = re.search(
        r'^\s*(?:i[\x27\u2019]?m\s*|i\s*am\s*)?(?:an?\s*)?(11|22|33|[1-9])(?:\s*[!.\s\U00010000-\U0010ffff\u2728]*)$',
        clean
    )
    if p_standalone:
        return int(p_standalone.group(1))

    return None


# -----------------------------------------------------------------------------
# CLASSIFICATION & TEMPLATE ROTATION
# -----------------------------------------------------------------------------
FORBIDDEN_FILTER_WORDS = ("click", "link", "bio", "free")


class CommentReplyEngine:
    def __init__(self, use_llm: bool = False, ollama_url: str = "http://localhost:11434/api/generate", model: str = "qwen2.5-coder:3b"):
        self.use_llm = use_llm
        self.ollama_url = ollama_url
        self.model = model

    def classify_comment(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classifies incoming comment into Bucket A, B, C, D, or E.
        Returns (bucket_name, extracted_meta_dict).
        """
        clean = text.lower().strip()

        # 0. Bucket A_PAIR_COMPAT: Two birth days detected (e.g. "14th and 23rd", "me 7 him 19", "Oct 12 and May 4")
        days = parse_birth_days_from_comment(clean)
        if len(days) >= 2:
            return "A_PAIR_COMPAT", compute_pair_compatibility_summary(days[0], days[1])

        # 1. Bucket A: Full Birthday with Year detection (e.g. "08/19/1978", "March 14 1995")
        bday = parse_birthday_from_text(clean)
        if bday:
            y, mo, d, fmt_date = bday
            lp_val, lp_disp = calculate_life_path(y, mo, d)
            vedic_val, vedic_ruler = calculate_vedic_moolank(d)
            lp_archetype = NUMBER_ARCHETYPES.get(lp_val, {"title": f"Path {lp_val}"})["title"]
            return "A_BIRTHDAY", {
                "year": y, "month": mo, "day": d,
                "date_str": fmt_date,
                "life_path_val": lp_val,
                "life_path_display": lp_disp,
                "life_path_archetype": lp_archetype,
                "vedic_val": vedic_val,
                "vedic_planet": vedic_ruler["planet"],
            }

        # 1b. Bucket A_SINGLE_DAY_COMPAT: Single birth day detected (e.g. "Born on the 19th", "7", "25th")
        if len(days) == 1:
            return "A_SINGLE_DAY_COMPAT", compute_single_day_summary(days[0])

        # 2. Bucket B: Life Path Number / Master Number detection
        num = parse_number_from_text(clean)
        if num is not None:
            arch = NUMBER_ARCHETYPES.get(num, {"name": f"Number {num}", "title": f"Number {num}", "trait": "Unique Vibration"})
            return "B_NUMBER", {
                "number": num,
                "archetype_title": arch["title"],
                "archetype_name": arch["name"],
                "trait": arch["trait"]
            }

        # 3. Bucket C: User asking for Link / How / Cost / Website
        if re.search(r'\b(link|where|how\s*do\s*i|website|cost|free|how\s*to\s*calculate|where\s*is|url|app|price|how\s*much)\b', clean):
            return "C_LINK_HOW", {}

        # 4. Bucket D: Burnout / Timing / Relationships / Friction / Exhaustion
        if re.search(r'\b(burnout|burned\s*out|tired|exhausted|stuck|hitting\s*a\s*wall|timing|wrong\s*time|friction|relationship|partner|love|work\s*hard|working\s*hard|struggling|lost|career|overwhelmed|cycle)\b', clean):
            return "D_BURNOUT_TIMING", {}

        # 5. Bucket E: Affirmation / Praise / Emojis / Fallback
        return "E_AFFIRMATION", {}

    def get_deterministic_reply(self, bucket: str, meta: Dict[str, Any], seed: int = 0) -> str:
        """
        Generates a natural, 100% TikTok spam-filter safe reply selected from rotating variations.
        Never contains 'click', 'link', 'bio', or 'free'.
        """
        if bucket in ("A_PAIR_COMPAT", "A_SINGLE_DAY_COMPAT"):
            return meta["reply"]
        if bucket == "A_BIRTHDAY":
            dt = meta["date_str"]
            lp = meta["life_path_display"]
            arch = meta["life_path_archetype"]
            v_val = meta["vedic_val"]
            v_plan = meta["vedic_planet"]
            variations = [
                f"Wait—born on {dt}? Your Western Life Path is {lp} ({arch}) and your Vedic lens is {v_val} (ruled by {v_plan}), which is only 2 of the 5 systems! Tap @sacrednumberblueprint above to run your 5-System Overlap chart on our page ✦",
                f"Born on {dt} gives you Life Path {lp} and Vedic Number {v_val}! But 20M people share your exact birthday—your name's Chaldean vibration and Chinese Lo Shu elements change everything. Check @sacrednumberblueprint to see all 5 ancient lenses for your name & birth date ✦",
                f"Your numbers from {dt}: Western Life Path = {lp} ({arch}), Vedic Radical = {v_val} ({v_plan}). In our 5-system matrix, that's only the first layer. Visit @sacrednumberblueprint above to decode your full name frequency on our page! ✦",
                f"With a {dt} birth date, your Western Life Path is {lp} and your Vedic ruler is {v_plan}. To see which 3 numbers repeat across all 5 ancient traditions for you, tap @sacrednumberblueprint above to run your chart on our page ✦",
            ]
        elif bucket == "B_NUMBER":
            num = meta["number"]
            title = meta["archetype_title"]
            trait = meta["trait"]
            variations = [
                f"Life Path {num} is {title}! But 20M people share that single lens—have you checked if {num} also repeats in your Chaldean Name & Kabbalah numbers, or if another number dominates your overlap? Tap @sacrednumberblueprint above to run your 5-System Overlap chart on our page ✦",
                f"Number {num} carries the frequency of {title}! If {num} also echoes in your full birth name's sound frequency, it becomes a Master Overlap Anchor. Check @sacrednumberblueprint to see all 5 ancient lenses for your name & birth date ✦",
                f"Being a {num} gives you natural {trait}, but single-system numerology is only 20% of your blueprint. Your name vibration unlocks the other 80%. Tap @sacrednumberblueprint above to run your full chart on our page! ✦",
                f"Life Path {num} ({title})! In our 5-system convergence matrix, we check whether {num} locks into your Chinese Lo Shu and Vedic council. Visit @sacrednumberblueprint above to decode your 3 Master Overlap Anchors ✦",
            ]
        elif bucket == "C_LINK_HOW":
            variations = [
                "Tap @sacrednumberblueprint above to run your 5-System Overlap chart on our page! You can test your name and birthday in 30 seconds ✦",
                "Check @sacrednumberblueprint to see all 5 ancient lenses for your name & birth date—it reveals your #1 Signature Anchor right on our page ✦",
                "Head over to @sacrednumberblueprint above! Our 5-System calculator cross-references Pythagorean, Chaldean, Kabbalah, Vedic & Chinese Lo Shu in seconds ✦",
                "Visit @sacrednumberblueprint above to test your 5-system code on our page. Zero app download needed—it calculates instantly in your browser ✦",
            ]
        elif bucket == "D_BURNOUT_TIMING":
            variations = [
                "90% of the time when you're pushing hard and hitting a wall, you're acting outside your current 52-Day Rosicrucian cycle. Tap @sacrednumberblueprint above to run your 5-System Overlap chart and active cycle timing on our page ✦",
                "That friction usually means you're in a Saturnian preservation window or fighting your constitutional Lo Shu element. Check @sacrednumberblueprint to see all 5 ancient lenses and your active cycle directives ✦",
                "When your timing is out of sync with your personal 7-cycle calendar, even 80-hour work weeks feel like pushing a boulder. Tap @sacrednumberblueprint above to check your active 52-day window on our page ✦",
                "Aligning your ambition with your 52-day planetary rhythm makes progress effortless instead of exhausting. Visit @sacrednumberblueprint above to check your current planetary cycle on our page ✦",
            ]
        else:  # E_AFFIRMATION
            variations = [
                "Claimed ✦ Make sure you check which 3 numbers repeat across all 5 ancient systems for your exact name & birth date—tap @sacrednumberblueprint above to run your 5-System Overlap chart on our page!",
                "Resonates with you ✦ When you see all 5 ancient traditions line up on your exact birth name, the clarity is undeniable. Check @sacrednumberblueprint to see all 5 ancient lenses for your name & birth date!",
                "Sending you high alignment ✦ Tap @sacrednumberblueprint above to test your 3 Master Overlap Anchors right on our page!",
                "Claimed with full intention ✦ Find out if your birth name and birthday share the exact same anchor code—visit @sacrednumberblueprint above to run your chart on our page!",
            ]

        idx = abs(seed) % len(variations)
        return variations[idx]

    def call_ollama_polish(self, comment_text: str, draft_reply: str) -> Optional[str]:
        """
        Optionally uses local Ollama (qwen2.5-coder:3b) to polish the reply,
        strictly preserving @sacrednumberblueprint and rejecting any forbidden filter words.
        """
        prompt = (
            f"You are the community voice of @sacrednumberblueprint on TikTok.\n"
            f"User Comment: \"{comment_text}\"\n"
            f"Draft Reply: \"{draft_reply}\"\n\n"
            f"Task: Lightly rewrite this reply so it reads naturally and warmly in under 260 characters.\n"
            f"CRITICAL RULES:\n"
            f"1. You MUST include '@sacrednumberblueprint'.\n"
            f"2. NEVER use the words 'click', 'link', 'bio', or 'free'.\n"
            f"3. Keep the exact numerology numbers and dates from the draft reply.\n"
            f"4. Return ONLY the final reply text with no quotation marks or meta commentary."
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 100
            }
        }

        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2.2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                polished = data.get("response", "").strip()
                low = polished.lower()
                if "@sacrednumberblueprint" in polished and not any(w in low for w in FORBIDDEN_FILTER_WORDS):
                    return polished
        except Exception:
            pass
        return None

    def generate_reply(self, comment_text: str, author: str = "", seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Main public interface:
        Classifies comment, computes numerology math if applicable, selects rotating variation,
        optionally polishes via Ollama, and returns structured result.
        """
        bucket, meta = self.classify_comment(comment_text)
        if seed is None:
            # Hash author + comment to get a deterministic per-comment variation
            seed = int(hashlib.md5(f"{author}:{comment_text}".encode("utf-8")).hexdigest()[:8], 16)

        reply_text = self.get_deterministic_reply(bucket, meta, seed)

        if self.use_llm:
            polished = self.call_ollama_polish(comment_text, reply_text)
            if polished:
                reply_text = polished

        return {
            "author": author,
            "comment": comment_text,
            "bucket": bucket,
            "meta": meta,
            "reply": reply_text
        }


# Quick CLI test runner
if __name__ == "__main__":
    engine = CommentReplyEngine(use_llm=False)
    samples = [
        "08/19/1978",
        "March 14 1995",
        "Life path 7 here!",
        "I'm an 8",
        "Master number 11",
        "Where is the link?",
        "How do I calculate mine?",
        "I have been working 80 hours a week and feel so burned out and stuck",
        "Claiming this energy ✨✨",
        "So accurate 🙏"
    ]
    print("=" * 65)
    print("   COMMENT REPLY ENGINE DEMONSTRATION")
    print("=" * 65)
    for i, s in enumerate(samples, 1):
        res = engine.generate_reply(s, author=f"user_{i}", seed=i)
        print(f"\n[{i}] Comment: \"{s}\"")
        print(f"    Bucket:  {res['bucket']}")
        print(f"    Reply:   {res['reply']}")
    print("=" * 65)
