#!/usr/bin/env python3
"""
=============================================================================
SOVEREIGN 5-SYSTEM · CONVERSATIONAL $2.99 EXPRESS SCRIPT RECOVERY DISPATCHER
send_cart_recovery.py
-----------------------------------------------------------------------------
Dispatches a clean, personal 3-line conversational recovery email with the
$2.99 Express Text Script price-drop link (STRIPE_LINK_MINI) to captured leads
who have not yet received the $2.99 price-drop notification.
=============================================================================
"""

import argparse
from datetime import datetime, timezone
import html
from typing import Any, Dict, Tuple
import urllib.parse
import sys

from lead_capture_worker import (
    INTERNAL_TEST_EMAILS,
    STRIPE_MINI_URL,
    calculate_5_systems,
    collect_lead_partner_checks_and_intent,
    is_internal_test_email,
    load_processed_state,
    save_processed_state,
    send_email_via_smtp,
)

STRIPE_LINK_MINI = STRIPE_MINI_URL  # https://buy.stripe.com/00w4gz0tj66x0cw5Tx38405
INTERNAL_TEST_EMAILS = set(INTERNAL_TEST_EMAILS) | {
    "getshoes7@gmail.com",
    "adam.vegaui@gmail.com",
    "imcodingdad@gmail.com",
}


def build_3line_price_drop_email(lead_entry: Dict[str, Any]) -> Tuple[str, str, str]:
    """Builds a clean, conversational 3-line plain + minimal HTML email featuring STRIPE_LINK_MINI ($2.99)."""
    raw_name = str(lead_entry.get("name") or "Friend").strip()
    first_name = raw_name.split()[0] if raw_name and raw_name.lower() not in ("your reading", "tu lectura") else "Friend"
    dob = str(lead_entry.get("dob") or "1986-02-19")
    email_addr = str(lead_entry.get("email") or "").strip()
    partner_dob = str(lead_entry.get("partner_dob") or "")

    try:
        dt_obj = datetime.strptime(dob, "%Y-%m-%d")
        dob_short = dt_obj.strftime("%b %d").replace(" 0", " ")
        day_num = dt_obj.day
    except Exception:
        dob_short = dob
        day_num = 19

    calc = calculate_5_systems(raw_name, dob)
    moolank_raw = str(calc.get("vedic_moolank") or "1 · Surya").split("(")[0].strip().replace(" · ", " ")
    moolank_label = f"#{moolank_raw}"
    intent = collect_lead_partner_checks_and_intent(email_addr, dob, partner_dob_fallback=partner_dob or None)
    p_checks = intent.get("partner_checks") or []
    unique_dates = list(dict.fromkeys([p["short_date"] for p in p_checks if p.get("short_date")]))
    if partner_dob:
        try:
            pd_short = datetime.strptime(partner_dob, "%Y-%m-%d").strftime("%b %d").replace(" 0", " ")
            if pd_short not in unique_dates:
                unique_dates.append(pd_short)
        except Exception:
            pass

    checkout_url = (
        f"{STRIPE_LINK_MINI}?prefilled_email={urllib.parse.quote(email_addr)}"
        f"&utm_source=email_recovery&utm_campaign=price_drop_299"
    )

    if email_addr.lower() == "geet08190@gmail.com" or unique_dates:
        partner_dates = " & ".join(unique_dates[:2]) if unique_dates else "Aug 19"
        subject = f"quick note on your {dob_short} compatibility script, {first_name}"
        line1 = (
            f"Hey {first_name} — I saw you ran your {dob_short} compatibility check (with {partner_dates}) "
            f"and wanted to send a quick note because we just separated the 9-word \"Flip The Chase\" text script from the full dossier."
        )
        line2 = (
            f"Instead of $17, you can now grab your custom Day {day_num} pattern-interrupt text script + his 3 pull-closer dates "
            f"this month for $2.99 (1-tap Apple Pay / Google Pay): {checkout_url}"
        )
        line3 = (
            "If you ever want your full 20-page 5-System Relationship Dossier later, just reply to this email and I'll take care of you personally. — Adam"
        )
    else:
        subject = f"quick note on your {dob_short} blueprint script, {first_name}"
        line1 = (
            f"Hey {first_name} — I saw your {dob_short} ({moolank_label}) reading in Sacred Number Blueprint "
            f"and wanted to let you know we just unbundled the Express \"Flip The Chase\" script from the full dossier."
        )
        line2 = (
            f"Instead of $17, you can now unlock your exact Day {day_num} pattern-interrupt script + 3 high-alignment dates "
            f"this month for $2.99 (1-tap Apple Pay / Google Pay): {checkout_url}"
        )
        line3 = (
            "If you ever want the full 20-page 5-System Blueprint Dossier too, just hit reply here anytime. — Adam"
        )

    plain_text = f"{line1}\n\n{line2}\n\n{line3}\n"
    line2_html = (
        html.escape(line2.replace(checkout_url, "")).rstrip()
        + f' <a href="{html.escape(checkout_url)}" style="color:#0b57d0;font-weight:600;">Unlock your $2.99 Express Script here →</a>'
    )
    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:15px;line-height:1.55;color:#1f2937;">
  <p style="margin:0 0 14px 0;">{html.escape(line1)}</p>
  <p style="margin:0 0 14px 0;">{line2_html}</p>
  <p style="margin:0;">{html.escape(line3)}</p>
</body>
</html>"""
    return subject, plain_text, html_body


def dispatch_price_drop_299(target_email: str = "", send_all: bool = False, force: bool = False, dry_run: bool = False) -> bool:
    processed = load_processed_state()
    targets = []
    for k, entry in processed.items():
        em = str(entry.get("email") or "").strip()
        if not em:
            continue
        if send_all or em.lower() == target_email.strip().lower():
            targets.append((k, entry))

    if not targets:
        print(f"✗ No matching leads found in processed_leads_state.json (target={target_email!r})")
        return False

    all_ok = True
    for key, entry in targets:
        em = str(entry.get("email") or "").strip()
        if em.lower() in {x.lower() for x in INTERNAL_TEST_EMAILS} or is_internal_test_email(em):
            print(f"✓ [INTERNAL TEST] Skipping test account {em}.")
            continue
        if entry.get("price_drop_299_sent_at") and not force and not dry_run:
            print(f"✓ $2.99 Express Script recovery already sent to {em} at {entry['price_drop_299_sent_at']} (skipping).")
            continue

        subject, plain_text, html_body = build_3line_price_drop_email(entry)
        print(f"▶ Prepared 3-line $2.99 recovery email for {entry.get('name')} <{em}> | Subject: {subject}")
        if dry_run:
            print(plain_text)
            continue

        ok = send_email_via_smtp(em, subject, plain_text, html_body, step_num=299)
        if ok:
            entry["price_drop_299_sent_at"] = datetime.now(timezone.utc).isoformat()
            processed[key] = entry
            save_processed_state(processed)
            print(f"✓ Recorded price_drop_299_sent_at for {em} in processed_leads_state.json")
        else:
            all_ok = False
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Send conversational 3-line $2.99 Express Script recovery email")
    parser.add_argument("--email", type=str, default="", help="Specific lead email to notify")
    parser.add_argument("--all", action="store_true", help="Send to all leads who haven't received the $2.99 price-drop link")
    parser.add_argument("--force", action="store_true", help="Force re-send even if price_drop_299_sent_at is set")
    parser.add_argument("--dry-run", action="store_true", help="Preview 3-line emails without sending")
    args = parser.parse_args()

    send_all = args.all or not args.email
    ok = dispatch_price_drop_299(target_email=args.email, send_all=send_all, force=args.force, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
