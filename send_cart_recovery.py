#!/usr/bin/env python3
"""
=============================================================================
SOVEREIGN 5-SYSTEM · INSTANT $17 VIP CART RECOVERY DISPATCHER
send_cart_recovery.py
-----------------------------------------------------------------------------
Dispatches the personalized $17 Partner Synastry & 90-Day Love Timing VIP
Recovery Email via lead_capture_worker.py for high-intent leads who clicked
checkout or ran 3+ Partner Compatibility checks without completing payment.
=============================================================================
"""

import argparse
from datetime import datetime, timezone
import json
import sys

from lead_capture_worker import (
    build_cart_recovery_email,
    calculate_5_systems,
    collect_lead_partner_checks_and_intent,
    format_attribution_source,
    load_processed_state,
    save_processed_state,
    send_cart_recovery_email,
)


def dispatch_recovery_for_email(target_email: str, force: bool = False, dry_run: bool = False) -> bool:
    processed = load_processed_state()
    target_clean = target_email.strip().lower()

    matched_key = None
    matched_entry = None
    for k, entry in processed.items():
        if str(entry.get("email") or "").strip().lower() == target_clean:
            matched_key = k
            matched_entry = entry
            break

    if not matched_entry:
        print(f"✗ Lead {target_email} not found in processed_leads_state.json")
        return False

    if matched_entry.get("cart_recovery_sent_at") and not force and not dry_run:
        print(
            f"✓ Cart recovery email already sent to {target_email} at {matched_entry.get('cart_recovery_sent_at')} "
            f"(use --force to re-send)"
        )
        return True

    name = matched_entry.get("name", "Geet")
    dob = matched_entry.get("dob", "1986-02-19")
    email_addr = matched_entry.get("email", target_email)
    partner_dob = matched_entry.get("partner_dob", "1988-08-19")

    intent = collect_lead_partner_checks_and_intent(email_addr, dob, partner_dob_fallback=partner_dob)
    calc = calculate_5_systems(name, dob)
    lead_record = {
        "timestamp": matched_entry.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "name": name,
        "dob": dob,
        "email": email_addr,
        "lang": matched_entry.get("lang", "en"),
        "utm": matched_entry.get("utm") or {},
        "source_attribution": matched_entry.get("source_attribution") or format_attribution_source(matched_entry.get("utm")),
        "partner_dob": partner_dob,
        "calc": calc,
    }

    subject, plain_text, html_body = build_cart_recovery_email(lead_record, intent_info=intent)
    print(f"Prepared Cart Recovery Email for {name} <{email_addr}> (DOB: {dob})")
    print(f"Subject: {subject}")
    print(f"Partner Checks Found: {len(intent.get('partner_checks', []))} | Checkout Clicked: {intent.get('checkout_clicked')}")
    for p in intent.get("partner_checks", []):
        print(f"  - {p['short_date']} ({p['dob']}): {p['score']}% | Driver: {p['moolank']} | LP: {p['life_path']}")

    if dry_run:
        print("[Dry Run] Skipping SMTP send.")
        return True

    ok = send_cart_recovery_email(lead_record, intent_info=intent)
    if ok and matched_key:
        matched_entry["cart_recovery_sent_at"] = datetime.now(timezone.utc).isoformat()
        processed[matched_key] = matched_entry
        save_processed_state(processed)
        print(f"✓ Recorded cart_recovery_sent_at for {email_addr} in processed_leads_state.json")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Send $17 VIP Cart Recovery Email")
    parser.add_argument("--email", type=str, default="geet08190@gmail.com", help="Target lead email")
    parser.add_argument("--force", action="store_true", help="Force re-send even if cart_recovery_sent_at is set")
    parser.add_argument("--dry-run", action="store_true", help="Preview email metadata without sending")
    args = parser.parse_args()

    ok = dispatch_recovery_for_email(args.email, force=args.force, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
