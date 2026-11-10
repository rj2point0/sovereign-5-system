#!/usr/bin/env python3
"""
UNIFIED INTERACTIVE LOCAL WEB LOGIN RELAY BRIDGE (`http://localhost:8767`)
==========================================================================
Provides a browser-accessible remote screenshot + password/click/key relay at
`http://localhost:8767` with two instant account tabs:
  - Tab 1 (`?tab=veo`): `adam.vegaui@gmail.com` (Port 9224 `veo_ultra_cdp_userdata` -> Google Flow Veo 3.1)
  - Tab 2 (`?tab=yt`):  `imcodingdad@gmail.com` (Port 9222 `yt_chrome_cdp_userdata` -> YouTube Studio)
Plus a direct 1-click link + live status check for enabling Vertex AI (`aiplatform.googleapis.com`)
on project `828136803921` for the `AQ.` API key.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Dict, Optional
from urllib.parse import parse_qs, unquote

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from mcp_veo31_server import Veo31VideoGenerator

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VEO_CDP_DIR = r"C:\Users\User\.gemini\antigravity\veo_ultra_cdp_userdata"
YT_CDP_DIR = r"C:\Users\User\.gemini\antigravity\yt_chrome_cdp_userdata"
IG_CDP_DIR = r"C:\Users\User\.gemini\antigravity\ig_browser_profile"
YT_CHANNEL_ID = "UCBIWSA7ZBuBEP_9rj3uSfqA"
RELAY_PORT = 8767


def is_cdp_port_open(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.2) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_chrome_cdp_started(port: int, user_data_dir: str, start_url: str, profile_dir: Optional[str] = None):
    os.makedirs(user_data_dir, exist_ok=True)
    if is_cdp_port_open(port):
        return
    cmd = [
        CHROME_EXE,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1366,900",
    ]
    if profile_dir:
        cmd.append(f"--profile-directory={profile_dir}")
    cmd.append(start_url)
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(20):
        if is_cdp_port_open(port):
            break
        time.sleep(0.4)


class DualAccountRelayServer:
    def __init__(self):
        self.active_tab: str = "ig"  # "veo" (port 9224), "yt" (port 9222), or "ig" (port 9225)
        self.pages: Dict[str, Optional[Page]] = {"veo": None, "yt": None, "ig": None}
        self.screenshots: Dict[str, bytes] = {"veo": b"", "yt": b"", "ig": b""}
        self.urls: Dict[str, str] = {"veo": "", "yt": "", "ig": ""}
        self.auth_status: Dict[str, bool] = {"veo": False, "yt": False, "ig": False}
        self.ig_auto_upload_triggered: bool = False
        self.vertex_ok: bool = False
        self.vertex_msg: str = "Checking..."
        self.veo_gen = Veo31VideoGenerator()

    async def prefill_email_on_page(self, page: Page, email: str):
        try:
            await page.set_viewport_size({"width": 1366, "height": 900})
        except Exception:
            pass
        try:
            acct = page.locator(f'[data-identifier="{email}"], div:has-text("{email}")').last
            if await acct.count() > 0 and await acct.is_visible():
                await acct.click(force=True)
                await asyncio.sleep(2.0)
            email_in = page.locator('input[type="email"], input#identifierId').first
            if await email_in.count() > 0 and await email_in.is_visible():
                cur_val = await email_in.input_value()
                if not cur_val or email.lower() not in cur_val.lower():
                    await email_in.fill(email)
                    await asyncio.sleep(0.4)
                await page.keyboard.press("Enter")
                await asyncio.sleep(2.0)
        except Exception:
            pass

    async def init_browsers(self, playwright):
        # 1. Start Port 9224 (adam.vegaui@gmail.com -> Google Flow Veo 3.1)
        veo_url = "https://accounts.google.com/"
        ensure_chrome_cdp_started(9224, VEO_CDP_DIR, veo_url)
        b_veo = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9224")
        ctx_veo = b_veo.contexts[0] if b_veo.contexts else await b_veo.new_context(viewport={"width": 1366, "height": 900})
        p_veo = ctx_veo.pages[0] if ctx_veo.pages else await ctx_veo.new_page()
        if p_veo.url in ("about:blank", "") or "chrome://" in p_veo.url or "continue=https://labs.google" in p_veo.url:
            await p_veo.goto(veo_url, wait_until="domcontentloaded", timeout=30000)
        self.pages["veo"] = p_veo
        await self.prefill_email_on_page(p_veo, "adam.vegaui@gmail.com")

        # 2. Start Port 9222 (imcodingdad@gmail.com -> YouTube Studio)
        yt_url = f"https://studio.youtube.com/channel/{YT_CHANNEL_ID}"
        ensure_chrome_cdp_started(9222, YT_CDP_DIR, yt_url, profile_dir="Profile 6")
        b_yt = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx_yt = b_yt.contexts[0] if b_yt.contexts else await b_yt.new_context(viewport={"width": 1366, "height": 900})
        p_yt = ctx_yt.pages[0] if ctx_yt.pages else await ctx_yt.new_page()
        if p_yt.url in ("about:blank", "") or "chrome://" in p_yt.url:
            await p_yt.goto(yt_url, wait_until="domcontentloaded", timeout=30000)
        self.pages["yt"] = p_yt
        await self.prefill_email_on_page(p_yt, "imcodingdad@gmail.com")

        # 3. Start Port 9225 (@sacrednumberblueprint -> Instagram Reels)
        ig_url = "https://www.instagram.com/"
        ensure_chrome_cdp_started(9225, IG_CDP_DIR, ig_url)
        b_ig = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9225")
        ctx_ig = b_ig.contexts[0] if b_ig.contexts else await b_ig.new_context(viewport={"width": 1366, "height": 900})
        p_ig = ctx_ig.pages[0] if ctx_ig.pages else await ctx_ig.new_page()
        try:
            await p_ig.set_viewport_size({"width": 1366, "height": 900})
        except Exception:
            pass
        if p_ig.url in ("about:blank", "") or "chrome://" in p_ig.url:
            await p_ig.goto(ig_url, wait_until="domcontentloaded", timeout=30000)
        self.pages["ig"] = p_ig
        try:
            await asyncio.sleep(1.5)
            cont_btn = p_ig.locator('button:has-text("Continue as sacrednumberblueprint"), div[role="button"]:has-text("Continue as sacrednumberblueprint")').first
            if await cont_btn.count() > 0 and await cont_btn.is_visible():
                await cont_btn.click(force=True)
                await asyncio.sleep(2.0)
            user_in = p_ig.locator('input[name="username"], input[name="email"]').first
            if await user_in.count() > 0 and await user_in.is_visible():
                cur_u = await user_in.input_value()
                if not cur_u:
                    await user_in.fill("sacrednumberblueprint")
        except Exception:
            pass

    async def screenshot_loop(self):
        tick = 0
        while True:
            tick += 1
            for key, page in self.pages.items():
                if page is None:
                    continue
                try:
                    png = await page.screenshot(type="png")
                    self.screenshots[key] = png
                    u = page.url
                    self.urls[key] = u
                    if key == "veo":
                        cookies = await page.context.cookies(["https://labs.google", "https://flow.google.com", "https://accounts.google.com"])
                        cnames = {c["name"] for c in cookies}
                        is_authed = ("SID" in cnames or "__Secure-1PSID" in cnames) and ("signin" not in u.lower() and "servicelogin" not in u.lower())
                        self.auth_status["veo"] = is_authed
                        if is_authed and "myaccount.google.com" in u:
                            await page.goto("https://labs.google/fx/tools/flow", wait_until="domcontentloaded", timeout=25000)
                    elif key == "yt":
                        self.auth_status["yt"] = ("studio.youtube.com" in u) and ("accounts.google.com" not in u)
                    elif key == "ig":
                        cookies = await page.context.cookies(["https://www.instagram.com"])
                        cnames = {c["name"] for c in cookies}
                        has_sidebar = await page.locator('svg[aria-label="New post"], svg[aria-label="Home"], a[href="/sacrednumberblueprint/"]').count() > 0
                        is_ig_authed = ("sessionid" in cnames or has_sidebar) and ("/accounts/login" not in u.lower())
                        self.auth_status["ig"] = is_ig_authed
                        if is_ig_authed and not self.ig_auto_upload_triggered:
                            self.ig_auto_upload_triggered = True
                            subprocess.Popen(
                                [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ig_reels_auto_uploader.py"), "--video", "Short_051_Veo31_Breadcrumbing.mp4", "--wait-login", "15"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                except Exception:
                    pass
            if tick % 5 == 1:
                try:
                    ok, msg = await asyncio.to_thread(self.veo_gen.verify_vertex_veo_ready)
                    self.vertex_ok = ok
                    self.vertex_msg = msg
                except Exception:
                    pass
            await asyncio.sleep(0.9)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            req_line = await reader.readline()
            if not req_line:
                writer.close()
                return
            parts = req_line.decode("utf-8", errors="ignore").split()
            path = parts[1] if len(parts) > 1 else "/"
            while True:
                h = await reader.readline()
                if not h or h in (b"\r\n", b"\n"):
                    break

            qs = parse_qs(path.split("?", 1)[1]) if "?" in path else {}
            tab = qs.get("tab", [self.active_tab])[0]
            if tab not in ("veo", "yt", "ig"):
                tab = "ig"
            self.active_tab = tab
            page = self.pages.get(tab)

            if path.startswith("/shot.png"):
                body = self.screenshots.get(tab, b"")
                writer.write(
                    b"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nCache-Control: no-store\r\n\r\n" + body
                )
            elif path.startswith("/status.json"):
                payload = json.dumps({
                    "active_tab": self.active_tab,
                    "urls": self.urls,
                    "auth_status": self.auth_status,
                    "vertex_ok": self.vertex_ok,
                    "vertex_msg": self.vertex_msg,
                }).encode("utf-8")
                writer.write(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nCache-Control: no-store\r\n\r\n" + payload
                )
            elif path.startswith("/click?") and page is not None:
                cx = float(qs.get("x", ["0"])[0])
                cy = float(qs.get("y", ["0"])[0])
                if cx > 0 and cy > 0:
                    await page.mouse.click(cx, cy)
                    await asyncio.sleep(0.4)
                    try:
                        self.screenshots[tab] = await page.screenshot(type="png")
                    except Exception:
                        pass
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"ok\":true}")
            elif path.startswith("/key?") and page is not None:
                k = qs.get("k", ["Enter"])[0]
                await page.keyboard.press(k)
                await asyncio.sleep(0.5)
                try:
                    self.screenshots[tab] = await page.screenshot(type="png")
                except Exception:
                    pass
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"ok\":true}")
            elif path.startswith("/prefill?") and page is not None:
                email = "adam.vegaui@gmail.com" if tab == "veo" else "imcodingdad@gmail.com"
                await self.prefill_email_on_page(page, email)
                try:
                    self.screenshots[tab] = await page.screenshot(type="png")
                except Exception:
                    pass
                writer.write(f"HTTP/1.1 302 Found\r\nLocation: /?tab={tab}\r\n\r\n".encode("utf-8"))
            elif path.startswith("/send?") and page is not None:
                txt = unquote(qs.get("text", [""])[0])
                if txt:
                    pw_in = page.locator(
                        'input[type="password"], input[name="Passwd"], input[type="tel"], input[type="text"], input[type="email"]'
                    ).first
                    try:
                        if await pw_in.count() > 0 and await pw_in.is_visible():
                            await pw_in.fill(txt)
                        else:
                            await page.keyboard.type(txt)
                    except Exception:
                        await page.keyboard.type(txt)
                    await asyncio.sleep(0.3)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(1.2)
                    try:
                        self.screenshots[tab] = await page.screenshot(type="png")
                    except Exception:
                        pass
                writer.write(f"HTTP/1.1 302 Found\r\nLocation: /?tab={tab}\r\n\r\n".encode("utf-8"))
            else:
                veo_badge = "🟢 SIGNED IN" if self.auth_status["veo"] else "🟡 LOGIN NEEDED"
                yt_badge = "🟢 SIGNED IN" if self.auth_status["yt"] else "🟡 LOGIN NEEDED"
                ig_badge = "🟢 SIGNED IN" if self.auth_status["ig"] else "🟡 LOGIN NEEDED"
                vtx_badge = "🟢 VERTEX API ENABLED" if self.vertex_ok else "🟡 CLICK TO ENABLE VERTEX AI API (PROJECT 828136803921)"
                if tab == "veo":
                    cur_email = "adam.vegaui@gmail.com (Google Flow Veo 3.1 · Port 9224)"
                elif tab == "yt":
                    cur_email = "imcodingdad@gmail.com (YouTube Studio · Port 9222)"
                else:
                    cur_email = "@sacrednumberblueprint (Instagram Reels · Port 9225)"
                cur_url = self.urls.get(tab, "")

                html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Unified Auth Relay Bridge (localhost:8767)</title>
  <style>
    body {{ background:#0d0b14; color:#f5e6c8; font-family:system-ui,-apple-system,sans-serif; text-align:center; padding:14px; margin:0; }}
    .tabs {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-bottom:12px; }}
    .tab-btn {{ padding:12px 20px; border-radius:10px; font-weight:700; font-size:15px; text-decoration:none; border:2px solid #d4af37; color:#f5e6c8; background:#171426; }}
    .tab-btn.active {{ background:#d4af37; color:#000; }}
    .vertex-banner {{ display:inline-block; margin-bottom:12px; padding:10px 18px; border-radius:8px; background:#1e293b; border:1px solid #38bdf8; color:#38bdf8; font-weight:700; text-decoration:none; font-size:14px; }}
    .bar {{ display:flex; gap:8px; justify-content:center; align-items:center; flex-wrap:wrap; margin-bottom:12px; }}
    input {{ padding:11px 14px; width:320px; font-size:16px; border-radius:8px; border:1px solid #d4af37; background:#171426; color:#fff; }}
    button, .action-btn {{ padding:11px 18px; font-size:15px; background:#d4af37; color:#000; font-weight:700; border:none; border-radius:8px; cursor:pointer; text-decoration:none; }}
    .secondary-btn {{ background:#2a2438; color:#f5e6c8; border:1px solid #d4af37; }}
    img {{ width:1060px; max-width:96vw; border:2px solid #d4af37; border-radius:10px; cursor:crosshair; display:block; margin:0 auto; }}
    .url-bar {{ font-size:12px; color:#94a3b8; margin-bottom:8px; font-family:monospace; }}
  </style>
</head>
<body>
  <div class="tabs">
    <a class="tab-btn {'active' if tab=='veo' else ''}" href="/?tab=veo">
      Tab 1: adam.vegaui@gmail.com (Flow Veo 3.1 · Port 9224) [{veo_badge}]
    </a>
    <a class="tab-btn {'active' if tab=='yt' else ''}" href="/?tab=yt">
      Tab 2: imcodingdad@gmail.com (YouTube Studio · Port 9222) [{yt_badge}]
    </a>
    <a class="tab-btn {'active' if tab=='ig' else ''}" href="/?tab=ig">
      Tab 3: @sacrednumberblueprint (Instagram Reels · Port 9225) [{ig_badge}]
    </a>
  </div>

  <div>
    <a class="vertex-banner" href="https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project=828136803921" target="_blank">
      ⚡ {vtx_badge} — Open Google Cloud Console (Project 828136803921) ↗
    </a>
  </div>

  <h3 style="margin:6px 0;">Active Relay: <code>{cur_email}</code></h3>
  <div class="url-bar" id="url-bar">Current URL: {cur_url}</div>

  <form class="bar" action="/send" method="get">
    <input type="hidden" name="tab" value="{tab}">
    <input type="password" name="text" placeholder="Type password, email, or 2FA code..." autofocus>
    <button type="submit">Submit &amp; Press Enter</button>
    <a class="action-btn secondary-btn" href="/prefill?tab={tab}">Pre-Fill Email &amp; Next</a>
    <button type="button" class="secondary-btn" onclick="sendKey('Enter')">Press Enter</button>
    <button type="button" class="secondary-btn" onclick="sendKey('Tab')">Press Tab</button>
  </form>

  <img id="sc" src="/shot.png?tab={tab}&t=1" onclick="sendClick(event)">

  <script>
    const activeTab = "{tab}";
    setInterval(() => {{
      document.getElementById('sc').src = '/shot.png?tab=' + activeTab + '&t=' + Date.now();
    }}, 1100);
    function sendClick(e) {{
      const img = e.target;
      const rect = img.getBoundingClientRect();
      const scaleX = 1366 / rect.width;
      const scaleY = 900 / rect.height;
      const x = Math.round((e.clientX - rect.left) * scaleX);
      const y = Math.round((e.clientY - rect.top) * scaleY);
      fetch('/click?tab=' + activeTab + '&x=' + x + '&y=' + y).then(() => {{
        setTimeout(() => {{ img.src = '/shot.png?tab=' + activeTab + '&t=' + Date.now(); }}, 350);
      }});
    }}
    function sendKey(k) {{
      fetch('/key?tab=' + activeTab + '&k=' + encodeURIComponent(k)).then(() => {{
        setTimeout(() => {{ document.getElementById('sc').src = '/shot.png?tab=' + activeTab + '&t=' + Date.now(); }}, 350);
      }});
    }}
  </script>
</body>
</html>"""
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n" + html.encode("utf-8"))
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    async def run(self):
        async with async_playwright() as p:
            await self.init_browsers(p)
            asyncio.create_task(self.screenshot_loop())
            server = await asyncio.start_server(self.handle_client, "127.0.0.1", RELAY_PORT)
            print(f"✅ UNIFIED AUTH RELAY ACTIVE AT: http://localhost:{RELAY_PORT}", flush=True)
            async with server:
                await server.serve_forever()


if __name__ == "__main__":
    relay = DualAccountRelayServer()
    asyncio.run(relay.run())
