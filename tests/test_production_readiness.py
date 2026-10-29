import asyncio
from playwright.async_api import async_playwright

async def test_all():
    print("=== RUNNING PRODUCTION READINESS & VIP BYPASS TESTS ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # TEST 1: Founder Sample & Math Anchors
        print("\n--- Test 1: Founder Sample & Math Anchors ---")
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto("http://127.0.0.1:8080/")

        await page.click('button[data-action="sample"]')
        name_val = await page.input_value('#fullName')
        dob_val = await page.input_value('#birthDate')
        print(f"Loaded Sample: {name_val}, {dob_val}")
        assert name_val == 'Adam Vega'
        assert dob_val == '1978-08-19'

        res = await page.evaluate('''() => {
            const data = window.S5Engine.calculate('Adam Vega', '1978-08-19');
            return {
                anchors: data.overlap.anchors.map(a => a.number),
                harmonics: data.overlap.secondaryHarmonics.map(h => h.number)
            };
        }''')
        print(f"Engine Calculation: Anchors={res['anchors']}, Harmonics={res['harmonics']}")
        assert res['anchors'] == [7, 8, 4], f"Expected [7, 8, 4], got {res['anchors']}"
        assert res['harmonics'] == [9, 6], f"Expected [9, 6], got {res['harmonics']}"
        print("[OK] Founder sample and math verified!")

        # TEST 2: EN | ES toggle & Benefit-First Hero Copy
        print("\n--- Test 2: Language Toggle & Benefit-First Hero Copy ---")
        await page.click('button[data-lang="es"]')
        es_hero = await page.locator('h1[data-i18n="hero_title"]').inner_text()
        assert "Patrón Oculto de Pareja" in es_hero
        print(f"Spanish switch verified: {es_hero[:45]}...")

        await page.click('button[data-lang="en"]')
        en_hero = await page.locator('h1[data-i18n="hero_title"]').inner_text()
        assert "Stop Falling For Partners Who Pull Away" in en_hero and "See Who You're Actually Meant To Be With." in en_hero, f"Unexpected en_hero: {en_hero}"
        en_sub = await page.locator('p[data-i18n="hero_sub"]').inner_text()
        assert "You attract partners who pull away!" in en_sub and "which birthdays are your true soulmate match" in en_sub and "we check all 5" in en_sub, f"Unexpected en_sub: {en_sub}"
        en_btn = await page.locator('#calc-form button[type="submit"]').inner_text()
        assert "reveal my soulmate match & love timing now" in en_btn.lower(), f"Unexpected en_btn: {en_btn}"
        assert "free teaser" not in en_btn.lower()
        print(f"English switch & Problem-First -> Solution -> Certainty Hero verified: {en_hero[:55]}...")
        print("[OK] Language switcher and Problem-First -> Solution -> Certainty copy verified!")

        # TEST 3: Post-Payment Redirect with localStorage
        print("\n--- Test 3: Post-Payment Redirect (Customer with localStorage) ---")
        # Simulate customer filled form and paid
        await page.evaluate('''() => {
            localStorage.setItem('s5_profile', JSON.stringify({
                id: 'lead_test123',
                fullName: 'Adam Vega',
                birthDate: '1978-08-19',
                email: 'adam@sovereign5.com',
                tier: null
            }));
        }''')
        await page.goto("http://127.0.0.1:8080/?tier=full&unlocked=true")
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        pages_count = await page.locator('.page').count()
        print(f"Dossier automatically rendered: {pages_count} pages")
        assert pages_count == 20, f"Expected 20 pages, got {pages_count}"
        print("[OK] Post-payment redirect with localStorage automatically restored and rendered full dossier!")

        # TEST 4: Post-Payment on New Device (Empty localStorage) Fallback Claim Bar
        print("\n--- Test 4: New Device / Empty localStorage Fallback ---")
        context_clean = await browser.new_context()
        page_clean = await context_clean.new_page()
        # Ensure clean storage
        await page_clean.goto("http://127.0.0.1:8080/?unlocked=true&tier=full")
        await page_clean.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        claim_visible = await page_clean.is_visible('#claim-bar')
        print(f"Claim bar visible on empty device: {claim_visible}")
        assert claim_visible == True, "Claim bar should be visible when customer arrives with unlocked=true but no profile!"

        # Enter details in claim bar
        await page_clean.fill('#claimFullName', 'Marcus Sterling')
        await page_clean.fill('#claimBirthDate', '1985-04-12')
        await page_clean.click('#claim-form button[type="submit"]')
        await page_clean.wait_for_selector('#claim-bar', state='hidden', timeout=5000)
        await page_clean.wait_for_selector('#dossier-actions:not(.hidden)', timeout=5000)

        pages_count_claimed = await page_clean.locator('.page').count()
        print(f"Claimed Dossier rendered: {pages_count_claimed} pages")
        assert pages_count_claimed == 20
        print("[OK] Fallback claim bar allowed customer on new device to immediately generate and unlock their dossier!")

        # TEST 5: Secret Founder VIP parameter (?vip=adam)
        print("\n--- Test 5: Founder VIP Bypass (?vip=adam) ---")
        context_public = await browser.new_context()
        page_pub = await context_public.new_page()

        # Verify Founder Sample button is hidden for public simulated visitors:
        page_sample_check = await context_public.new_page()
        await page_sample_check.goto("http://127.0.0.1:8080/?public_test=1")
        sample_pub_vis = await page_sample_check.is_visible('#btn-sample')
        print(f"Public simulated visitor sees Founder Sample button: {sample_pub_vis}")
        assert sample_pub_vis == False, "Founder Sample button must be hidden for public visitors!"
        await page_sample_check.close()

        # Regular local visit to teaser (without vip):
        await page_pub.goto("http://127.0.0.1:8080/")
        await page_pub.click('button[data-action="sample"]')
        await page_pub.click('button[type="submit"]')
        await page_pub.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        demo_btn_public = await page_pub.is_visible('button[data-action="demo-unlock"]')
        print(f"Public user sees demo button: {demo_btn_public}")
        assert demo_btn_public == False, "Public user should NOT see demo button when DEMO_MODE=false!"

        # Founder visit with ?vip=adam:
        await page_pub.goto("http://127.0.0.1:8080/?vip=adam")
        await page_pub.click('button[data-action="sample"]')
        await page_pub.click('button[type="submit"]')
        await page_pub.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        demo_btn_vip = await page_pub.is_visible('button[data-action="demo-unlock"]')
        vip_badge = await page_pub.is_visible('#vip-badge')
        print(f"Founder with ?vip=adam sees demo button: {demo_btn_vip}")
        print(f"Founder sees VIP badge in header: {vip_badge}")
        assert demo_btn_vip == True, "Founder with ?vip=adam MUST see demo button!"
        assert vip_badge == True, "Founder should see VIP badge!"

        # Click demo unlock as founder:
        await page_pub.click('button[data-action="demo-unlock"]')
        await page_pub.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        pages_vip = await page_pub.locator('.page').count()
        print(f"Founder unlocked dossier count: {pages_vip}")
        assert pages_vip == 20
        print("[OK] Secret Founder VIP Bypass (?vip=adam) works 100% perfectly!")

        # TEST 6: Cross-Browser Email Teaser Link Session Restore & Compound/System Count Consistency
        print("\n--- Test 6: Cross-Browser Email Teaser Link & Cowen Math Consistency ---")
        context_email = await browser.new_context()
        page_email = await context_email.new_page()
        await page_email.goto("http://127.0.0.1:8080/?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=getshoes7%40gmail.com")
        await page_email.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        vsl_vis = await page_email.is_visible('#vsl-video')
        assert vsl_vis is True, "Native VSL video player must be visible on restored Teaser view!"
        cowen_check = await page_email.evaluate('''() => {
            const r = window.S5Engine.calculate('Cowen Airo Celestin Vega', '2017-07-07');
            return {
                expr: r.pythagorean.expression.display,
                anchors: r.overlap.anchors.map(a => ({ n: a.number, c: a.count, s: a.systems }))
            };
        }''')
        print(f"Cowen Engine Check: Expression={cowen_check['expr']}, Anchors={cowen_check['anchors']}")
        assert cowen_check['expr'] == '18/9', f"Expected 18/9 for Cowen Expression, got {cowen_check['expr']}"
        for a in cowen_check['anchors']:
            assert len(a['s']) <= a['c'], f"System count {len(a['s'])} exceeds hit count {a['c']} for anchor {a}"
        print("[OK] Cross-browser Teaser session restore & compound/system math verified!")

        # TEST 7: Bio Link Landing (?utm_source=ig_bio&cohort=ig_reels) Always Opens Hero Form & Public Domain Never Calls 127.0.0.1
        print("\n--- Test 7: Bio Link Landing (?utm_source=...) & Zero Private-Network 127.0.0.1 Calls on Public Domain ---")
        # First, verify that even when s5_profile with tier='full' is cached in localStorage,
        # visiting ?utm_source=ig_bio&cohort=ig_reels opens the fresh Hero Input Form (#view-hero) instead of the cached dossier!
        await page_pub.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels")
        await page_pub.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        dossier_hidden = await page_pub.locator('#view-dossier').evaluate('el => el.classList.contains("hidden")')
        hero_name_val = await page_pub.input_value('#fullName')
        assert dossier_hidden is True, "Cached dossier MUST be hidden when landing via ?utm_source=ig_bio!"
        assert hero_name_val == '', f"Expected empty #fullName on fresh bio link landing, got '{hero_name_val}'"
        print("[OK] Bio link (?utm_source=ig_bio&cohort=ig_reels) opens fresh Hero Input Form even with cached VIP dossier!")

        # Second, verify in app.js source & via simulated public domain route that 127.0.0.1:8788 is NEVER called on public hostname
        import os
        app_js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.js")
        with open(app_js_path, "r", encoding="utf-8") as f:
            app_js_src = f.read()
        assert "window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'" in app_js_src
        assert "CONFIG.LOCAL_WEBHOOK_URL && isLocalHostNow" in app_js_src

        # Intercept a simulated public domain https://rj2point0.github.io/sovereign-5-system/?utm_source=ig_bio&cohort=ig_reels&force_telemetry=1
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        context_prod = await browser.new_context()
        page_prod = await context_prod.new_page()
        prod_requests = []
        page_prod.on("request", lambda req: prod_requests.append(req.url))

        async def handle_prod_route(route):
            url = route.request.url
            if "ntfy.sh" in url:
                await route.fulfill(status=200, body="ok")
                return
            if "rj2point0.github.io/sovereign-5-system/" in url:
                rel = url.split("rj2point0.github.io/sovereign-5-system/")[1].split("?")[0]
                if not rel or rel == "/":
                    rel = "index.html"
                fpath = os.path.join(base_dir, rel.replace("/", os.sep))
                if os.path.exists(fpath) and os.path.isfile(fpath):
                    ctype = "text/html" if fpath.endswith(".html") else ("application/javascript" if fpath.endswith(".js") else "text/css")
                    with open(fpath, "rb") as rf:
                        body_bytes = rf.read()
                    await route.fulfill(status=200, content_type=ctype, body=body_bytes)
                    return
            await route.abort()

        await page_prod.route("**/*", handle_prod_route)
        await page_prod.goto("https://rj2point0.github.io/sovereign-5-system/?utm_source=ig_bio&cohort=ig_reels&force_telemetry=1")
        await page_prod.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        prod_local_url = await page_prod.evaluate("() => CONFIG.LOCAL_WEBHOOK_URL")
        assert prod_local_url == "", f"Expected CONFIG.LOCAL_WEBHOOK_URL to be empty on rj2point0.github.io, got '{prod_local_url}'"
        illegal_local_calls = [u for u in prod_requests if "127.0.0.1" in u or "localhost" in u]
        assert len(illegal_local_calls) == 0, f"Public domain made illegal private-network calls: {illegal_local_calls}"
        print("[OK] Simulated public domain (rj2point0.github.io) verified: CONFIG.LOCAL_WEBHOOK_URL='' and 0 calls to 127.0.0.1!")

        # TEST 8: Fast Mobile Month/Day/Year Dropdowns + Single First-Name Submission + Instant calc_preview
        print("\n--- Test 8: Fast Mobile Month/Day/Year Dropdowns & First-Name-Only Friction Fix ---")
        ntfy_payloads = []

        async def handle_prod_route_with_capture(route):
            url = route.request.url
            if "ntfy.sh" in url:
                if route.request.method == "POST":
                    try:
                        import json as _json
                        ntfy_payloads.append(_json.loads(route.request.post_data or "{}"))
                    except Exception:
                        pass
                await route.fulfill(status=200, body="ok")
                return
            await handle_prod_route(route)

        await page_prod.unroute("**/*")
        await page_prod.route("**/*", handle_prod_route_with_capture)
        await page_prod.goto("https://rj2point0.github.io/sovereign-5-system/?utm_source=ig_bio&cohort=ig_reels&force_telemetry=1")
        await page_prod.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)

        # Verify label & placeholder lowered friction
        name_label = await page_prod.locator('label[for="fullName"]').inner_text()
        assert "first name" in name_label.lower(), f"Expected First Name in label, got '{name_label}'"

        # Type ONLY First Name ("Sarah") and select Month/Day/Year via dropdowns
        await page_prod.fill('#fullName', 'Sarah')
        await page_prod.select_option('#dobMonth', '07')
        await page_prod.select_option('#dobDay', '16')
        await page_prod.select_option('#dobYear', '1990')

        synced_dob = await page_prod.input_value('#birthDate')
        assert synced_dob == '1990-07-16', f"Expected #birthDate to sync to '1990-07-16', got '{synced_dob}'"

        # Wait briefly for instant calc_preview telemetry to fire BEFORE clicking submit
        await asyncio.sleep(0.3)
        event_types_fired = [p.get("event_type") for p in ntfy_payloads]
        print(f"Telemetry events fired before submit: {event_types_fired}")
        assert "calc_started" in event_types_fired, f"Expected calc_started in {event_types_fired}"
        assert "calc_preview" in event_types_fired, f"Expected instant calc_preview in {event_types_fired}"

        # Submit with just First Name ("Sarah") + DOB and zero email
        await page_prod.click('#calc-form button[type="submit"]')
        await page_prod.wait_for_selector('#view-teaser:not(.hidden)', timeout=6000)

        # Verify Priority #1A on Teaser View:
        # 1) Instant Relationship & Attachment Blindspot Reveal (#teaser-relationship-clash)
        clash_vis = await page_prod.is_visible('#teaser-relationship-clash')
        assert clash_vis is True, "Expected #teaser-relationship-clash to be visible on Teaser view!"
        clash_txt = await page_prod.locator('#teaser-relationship-clash').inner_text()
        assert "Chase at 2 AM" in clash_txt and "#7" in clash_txt, f"Unexpected clash text: {clash_txt[:80]}"

        # 2) Ollie Carson's 3-Part Problem Triangle Briefing Cards (#teaser-problem-triangle)
        tri_count = await page_prod.locator('#teaser-problem-triangle [data-triangle-part]').count()
        assert tri_count == 3, f"Expected 3 Problem Triangle cards, got {tri_count}"
        await page_prod.click('button[data-action="play-triangle-part"][data-part="1"]')
        tri_status_vis = await page_prod.is_visible('#triangle-audio-status')
        assert tri_status_vis is True, "Expected #triangle-audio-status to appear when Part 1 briefing is clicked!"

        # 3) Optional Partner / Crush Birthday Compatibility Calculator (#partner-compat-box)
        compat_box_vis = await page_prod.is_visible('#partner-compat-box')
        assert compat_box_vis is True, "Expected #partner-compat-box to be visible on Teaser view!"
        await page_prod.select_option('#partnerDobMonth', '10')
        await page_prod.select_option('#partnerDobDay', '26')
        await page_prod.select_option('#partnerDobYear', '1988')
        await asyncio.sleep(0.2)
        compat_res_vis = await page_prod.is_visible('#partner-compat-result')
        assert compat_res_vis is True, "Expected #partner-compat-result to auto-render when partner Month/Day/Year are selected!"
        compat_res_txt = await page_prod.locator('#partner-compat-result').inner_text()
        assert "%" in compat_res_txt and "#8" in compat_res_txt, f"Unexpected partner compat output: {compat_res_txt[:100]}"
        event_types_after_compat = [p.get("event_type") for p in ntfy_payloads]
        assert "partner_compat_checked" in event_types_after_compat, f"Expected partner_compat_checked in {event_types_after_compat}"
        print("[OK] Mobile Month/Day/Year dropdowns, Teaser Relationship Clash, 3-Part Triangle, and Partner Compatibility Checker verified!")

        # TEST 9: Reverse Order (DOB -> Name) Bidirectional calc_preview + SEO/OG/AEO + Jenny Hoyos Gate Verification
        print("\n--- Test 9: Reverse Order (DOB -> Name) calc_preview, <=38-Char og:title, 5-Circle Logo & Jenny Hoyos Gate ---")
        ntfy_payloads.clear()
        await page_prod.goto("https://rj2point0.github.io/sovereign-5-system/?utm_source=ig_bio&cohort=ig_reels&force_telemetry=1")
        await page_prod.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)

        # Select DOB dropdowns FIRST, then type Name ("Elena")
        await page_prod.select_option('#dobMonth', '11')
        await page_prod.select_option('#dobDay', '25')
        await page_prod.select_option('#dobYear', '1994')
        await page_prod.fill('#fullName', 'Elena')
        await asyncio.sleep(0.3)

        reverse_events = [p.get("event_type") for p in ntfy_payloads]
        print(f"Reverse order (DOB -> Name) telemetry events: {reverse_events}")
        assert "calc_preview" in reverse_events, f"Expected calc_preview on reverse order (DOB -> Name), got {reverse_events}"
        progress_events = [p for p in ntfy_payloads if p.get("event_type") == "field_progress"]
        assert any("dob_preview" in (p.get("extra") or {}) and "name_length" in (p.get("extra") or {}) for p in progress_events), "Expected dob_preview and name_length in field_progress extra!"

        # Check SEO Title, <=38-char OpenGraph title, 5-Circle Venn favicon.svg, JSON-LD FAQPage, and 6-item Accordion
        doc_title = await page_prod.title()
        assert doc_title == "Uncover Your Hidden Relationship Pattern & Love Code", f"Unexpected title: {doc_title}"
        og_title = await page_prod.locator('meta[property="og:title"]').get_attribute('content')
        tw_title = await page_prod.locator('meta[name="twitter:title"]').get_attribute('content')
        og_image = await page_prod.locator('meta[property="og:image"]').get_attribute('content')
        og_desc = await page_prod.locator('meta[property="og:description"]').get_attribute('content')
        assert og_title == "Your Hidden Relationship & Love Code" and len(og_title) <= 38, f"Unexpected og_title: {og_title} (len={len(og_title)})"
        assert tw_title == "Your Hidden Relationship & Love Code" and len(tw_title) <= 38
        assert og_desc == "Attracting partners who pull away? Find out right now which birthdays are your true soulmate match and what the next 12 months hold for your love life.", f"Unexpected og_desc: {og_desc}"
        assert og_image == "https://blueprint.megavegaventures.com/og-preview.png"
        favicon_href = await page_prod.locator('link[rel="icon"]').get_attribute('href')
        assert favicon_href == "favicon.svg", f"Expected favicon.svg, got {favicon_href}"
        faq_items_count = await page_prod.locator('#hero-faq details.faq-item').count()
        assert faq_items_count == 13, f"Expected 13 FAQ accordion items (all 9 birthday love groups 1-31 + 4 core Q&As), got {faq_items_count}"
        json_ld_raw = await page_prod.locator('script[type="application/ld+json"]').inner_text()
        assert '"FAQPage"' in json_ld_raw and '"WebApplication"' in json_ld_raw and "Born on the 1st, 10th, 19th, or 28th" in json_ld_raw and "Born on the 9th, 18th, or 27th" in json_ld_raw
        for f_req in ("og-preview.png", "favicon.svg", "llms.txt", "robots.txt", "sitemap.xml"):
            assert os.path.exists(os.path.join(base_dir, f_req)), f"Missing {f_req}"

        # Verify Jenny Hoyos 5th-Grade Readability Gate on short_10, short_11, short_12
        import sys as _sys
        if base_dir not in _sys.path:
            _sys.path.insert(0, base_dir)
        from generate_broll_story_tiktoks import COHORT_C_SPECS, validate_jenny_hoyos_readability
        jh_specs = [s for s in COHORT_C_SPECS if s["id"] in ("short_10", "short_11", "short_12")]
        assert len(jh_specs) == 3, f"Expected 3 Jenny Hoyos specs, found {len(jh_specs)}"
        for s in jh_specs:
            gate_res = validate_jenny_hoyos_readability(s)
            assert gate_res["fk_grade"] <= 5.5, f"Expected FK Grade <= 5.5 for {s['id']}, got {gate_res['fk_grade']}"
        print("[OK] Reverse order calc_preview, <=38-char og:title, 5-Circle favicon.svg, Partner Compatibility & Jenny Hoyos 5th-Grade Gate verified!")

        await browser.close()
    print("\nALL PRODUCTION READINESS & VIP TESTS PASSED WITH 100% SUCCESS!")

if __name__ == '__main__':
    asyncio.run(test_all())
