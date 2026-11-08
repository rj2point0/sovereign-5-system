#!/usr/bin/env python3
"""
Probes Google Gemini Ultra (https://gemini.google.com/app) and Google Labs Flow / Veo 2
(https://labs.google/fx/tools/flow) using `veo_ultra_cdp_userdata` (`Profile 1` `adam.vegaui@gmail.com`)
with a strict 20-second timeout. Also audits the SQLite cookie encryption versions (`v10` DPAPI vs
`v20` Chrome 130+ App-Bound Encryption) in `p1_cookies_backup.sqlite`.
"""

import asyncio
import json
import os
import shutil
import sqlite3
import subprocess
import sys

from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

AG_DIR = r"C:\Users\User\.gemini\antigravity"
VEO_CDP_DIR = os.path.join(AG_DIR, "veo_ultra_cdp_userdata")
P1_BACKUP_DB = os.path.join(AG_DIR, "p1_cookies_backup.sqlite")
ARTIFACT_DIR = r"C:\Users\User\.gemini\antigravity\brain\72394d54-35fc-4bc0-a5bf-d614aa1b6a64"


def audit_backup_cookies():
    if not os.path.exists(P1_BACKUP_DB):
        print("[Audit] p1_cookies_backup.sqlite not found.")
        return
    conn = sqlite3.connect(P1_BACKUP_DB)
    total = conn.execute("SELECT count(*) FROM cookies").fetchone()[0]
    v10_cnt = conn.execute("SELECT count(*) FROM cookies WHERE substr(encrypted_value, 1, 3) = X'763130'").fetchone()[0]
    v20_cnt = conn.execute("SELECT count(*) FROM cookies WHERE substr(encrypted_value, 1, 3) = X'763230'").fetchone()[0]
    google_rows = conn.execute(
        "SELECT host_key, name, substr(encrypted_value, 1, 3), length(encrypted_value) "
        "FROM cookies WHERE (host_key LIKE '%google%' OR host_key LIKE '%labs%') "
        "AND name IN ('SID', 'SAPISID', 'LSID', '__Secure-1PSID', '__Secure-3PSID')"
    ).fetchall()
    conn.close()
    print(f"[Backup DB Audit] Total cookies={total} | v10 (DPAPI)={v10_cnt} | v20 (App-Bound)={v20_cnt}")
    print(f"[Backup DB Audit] Google Auth Cookies: {[(r[0], r[1], bytes(r[2]).decode('ascii', 'ignore'), r[3]) for r in google_rows]}")


async def probe_veo_ultra():
    audit_backup_cookies()

    # Ensure fresh copy from p1_cookies_backup.sqlite before launch
    dst_cookies = os.path.join(VEO_CDP_DIR, "Profile 1", "Network", "Cookies")
    os.makedirs(os.path.dirname(dst_cookies), exist_ok=True)
    if os.path.exists(P1_BACKUP_DB):
        shutil.copy2(P1_BACKUP_DB, dst_cookies)

    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_proc = subprocess.Popen(
        [
            chrome_exe,
            "--remote-debugging-port=9228",
            f"--user-data-dir={VEO_CDP_DIR}",
            "--profile-directory=Profile 1",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1400,900",
            "https://gemini.google.com/app",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        async with async_playwright() as p:
            browser = None
            for _ in range(8):
                await asyncio.sleep(0.8)
                try:
                    browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9228", timeout=4000)
                    break
                except Exception:
                    pass

            if not browser:
                print("[Probe] Could not connect to CDP port 9228 within 6.4s.")
                return

            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = ctx.pages[0] if ctx.pages else await ctx.new_page()
            page.set_default_timeout(12000)

            for label, url, shot_name in [
                ("Gemini App", "https://gemini.google.com/app", "veo_ultra_gemini_app.png"),
                ("Google Labs Flow (Veo)", "https://labs.google/fx/tools/flow", "veo_ultra_flow.png"),
            ]:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                    await asyncio.sleep(2.5)
                    cur_url = page.url
                    title = await page.title()
                    info = await page.evaluate(
                        """() => {
                            const txt = (document.body.innerText || '');
                            const btns = Array.from(document.querySelectorAll('button, a[role="button"]'))
                                .map(b => (b.innerText || b.getAttribute('aria-label') || '').trim())
                                .filter(Boolean);
                            const signInBtn = btns.some(b => /^sign in$/i.test(b));
                            const hasUltra = /ultra|advanced|veo|video/i.test(txt);
                            return {
                                signedIn: !signInBtn && !location.href.includes('accounts.google.com'),
                                hasUltraKeywords: hasUltra,
                                sampleControls: btns.slice(0, 10)
                            };
                        }"""
                    )
                    shot_p = os.path.join(ARTIFACT_DIR, shot_name)
                    await page.screenshot(path=shot_p)
                    print(f"[{label}] URL={cur_url} | Title={title!r} | SignedIn={info['signedIn']} | Controls={info['sampleControls'][:6]}")
                except Exception as e:
                    print(f"[{label}] Probe error: {e}")

            await browser.close()
    finally:
        chrome_proc.terminate()

    # Check how many cookies remain in VEO_CDP_DIR after Chrome opened it
    try:
        c_after = sqlite3.connect(dst_cookies)
        rem = c_after.execute("SELECT count(*) FROM cookies").fetchone()[0]
        c_after.close()
        print(f"[Post-Launch Cookie Audit] Cookies remaining in veo_ultra_cdp_userdata after Chrome startup: {rem}")
    except Exception as e:
        print(f"[Post-Launch Cookie Audit] {e}")


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(probe_veo_ultra(), timeout=22.0))
