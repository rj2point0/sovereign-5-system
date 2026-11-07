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
        partner_cta_vis = await page_prod.is_visible('#btn-partner-checkout-cta')
        assert partner_cta_vis is True, "Expected #btn-partner-checkout-cta to be visible inside #partner-compat-result!"
        partner_cta_txt = await page_prod.locator('#btn-partner-checkout-cta').inner_text()
        assert "unlock full 5-system partner compatibility & soulmate timing report" in partner_cta_txt.lower(), f"Unexpected partner CTA text: {partner_cta_txt}"

        # Verify partner_check_run telemetry payload includes user_dob, partner_dob, and compatibility_score
        partner_events = [p for p in ntfy_payloads if p.get("event_type") == "partner_check_run"]
        assert len(partner_events) >= 1, f"Expected partner_check_run in {[p.get('event_type') for p in ntfy_payloads]}"
        pe_extra = partner_events[-1].get("extra") or {}
        assert pe_extra.get("user_dob") == "1990-07-16", f"Expected user_dob=1990-07-16, got {pe_extra}"
        assert pe_extra.get("partner_dob") == "1988-10-26", f"Expected partner_dob=1988-10-26, got {pe_extra}"
        assert int(pe_extra.get("compatibility_score", 0)) >= 80, f"Expected compatibility_score >= 80, got {pe_extra}"

        # Click the dynamic Partner Compatibility Checkout CTA and verify #checkout-partner-banner + checkout_clicked telemetry
        await page_prod.click('#btn-partner-checkout-cta')
        await asyncio.sleep(0.15)
        banner_vis = await page_prod.is_visible('#checkout-partner-banner')
        assert banner_vis is True, "Expected #checkout-partner-banner to appear in #checkout when Partner CTA is clicked!"
        checkout_ev = [p for p in ntfy_payloads if p.get("event_type") == "checkout_clicked"]
        assert len(checkout_ev) >= 1 and checkout_ev[-1].get("partner_dob") == "1988-10-26", f"Expected partner_dob in checkout_clicked: {checkout_ev}"

        # Submit email in inline Partner Compatibility Email Capture Bar (#partner-compat-email-box) and verify:
        # 1) Part 1 unblurs immediately on-screen (#imessage-part1-text, #part1-unlocked-badge, #partner-secret-fear-unlocked, #imessage-part2-locked-callout)
        # 2) #vip-fast-action-offer reveals with 15-minute timer & prefilled_email wired into $17 Stripe URL
        # 3) #header-19x23-avatar, #header-19x23-badge, and #social-proof-toast render cleanly on view2
        assert await page_prod.is_visible('#header-19x23-avatar') is True, "Expected 32x32 19x23 avatar #header-19x23-avatar in header!"
        assert await page_prod.is_visible('#header-19x23-badge') is True, "Expected 19x23 96% badge #header-19x23-badge in header!"
        await asyncio.sleep(0.45)
        sp_toast_txt = await page_prod.locator('#social-proof-toast').inner_text()
        assert "19 × Day 23" in sp_toast_txt or "Partner Compatibility" in sp_toast_txt or "Mini-Read" in sp_toast_txt, f"Expected #social-proof-toast content on view2, got '{sp_toast_txt}'"

        assert await page_prod.is_visible('#partner-compat-email-box') is True, "Expected #partner-compat-email-box to be visible inside #partner-compat-result when !state.profile.email"
        p_email_txt = await page_prod.locator('#partner-compat-email-box').inner_text()
        assert "want to save this partner compatibility score" in p_email_txt.lower() and "3 dates this month they pull closer" in p_email_txt.lower() and "email our match report" in p_email_txt.lower(), f"Unexpected #partner-compat-email-box text: {p_email_txt}"
        await page_prod.fill('#partner-compat-email-input', 'sarah.compat@gmail.com')
        await page_prod.click('#btn-save-partner-email')
        await asyncio.sleep(0.2)
        assert await page_prod.is_visible('#partner-compat-email-confirmed') is True, "Expected green confirmation badge #partner-compat-email-confirmed after submitting partner email"
        assert await page_prod.is_visible('#part1-unlocked-badge') is True, "Expected #part1-unlocked-badge to appear immediately on email submit!"
        assert await page_prod.is_visible('#partner-secret-fear-unlocked') is True, "Expected #partner-secret-fear-unlocked to appear on email submit!"
        assert await page_prod.is_visible('#imessage-part2-locked-callout') is True, "Expected #imessage-part2-locked-callout to appear on email submit!"
        p2_callout_txt = await page_prod.locator('#imessage-part2-locked-callout').inner_text()
        assert "3 best days to text them this month" in p2_callout_txt.lower(), f"Unexpected #imessage-part2-locked-callout text: {p2_callout_txt}"
        p1_filter = await page_prod.evaluate("() => getComputedStyle(document.querySelector('#imessage-part1-text')).filter")
        assert p1_filter == "none", f"Expected #imessage-part1-text filter to be 'none' after email submit, got '{p1_filter}'"
        assert await page_prod.is_visible('#vip-fast-action-offer') is True, "Expected #vip-fast-action-offer to appear immediately on email submit!"
        vip_btn_txt = await page_prod.locator('#btn-vip-fast-action-17').inner_text()
        assert "best days to text them ($17)" in vip_btn_txt.lower(), f"Unexpected #btn-vip-fast-action-17 text: {vip_btn_txt}"
        vip_stripe_url = await page_prod.locator('#btn-vip-fast-action-17').get_attribute('data-stripe-url')
        assert vip_stripe_url and "prefilled_email=sarah.compat%40gmail.com" in vip_stripe_url, f"Expected prefilled_email in #btn-vip-fast-action-17 data-stripe-url, got '{vip_stripe_url}'"
        lead_evs = [p for p in ntfy_payloads if p.get("event_type") == "lead_submitted"]
        assert len(lead_evs) >= 1 and lead_evs[-1].get("partner_dob") == "1988-10-26", f"Expected partner_dob=1988-10-26 in lead_submitted payload: {lead_evs}"
        assert (lead_evs[-1].get("extra") or {}).get("trigger") == "partner_compat_email_bar", f"Expected trigger=partner_compat_email_bar, got {lead_evs[-1]}"
        print("[OK] Mobile Month/Day/Year dropdowns, Instant Part 1 Unblur, 15-Min $17 VIP Offer (prefilled_email), 19x23 Emblem & Social Proof Toast verified!")

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

        # Verify Jenny Hoyos 5th-Grade Readability Gate on short_10 through short_42
        import sys as _sys
        if base_dir not in _sys.path:
            _sys.path.insert(0, base_dir)
        from generate_broll_story_tiktoks import COHORT_C_SPECS, validate_jenny_hoyos_readability
        jh_specs = [s for s in COHORT_C_SPECS if s["id"] in ("short_10", "short_11", "short_12", "short_13", "short_14", "short_15", "short_16", "short_17", "short_18", "short_19", "short_20", "short_21", "short_22", "short_23", "short_24", "short_25", "short_26", "short_27", "short_28", "short_29", "short_30", "short_31", "short_32", "short_33", "short_34", "short_35", "short_36", "short_37", "short_38", "short_39", "short_40", "short_41", "short_42")]
        assert len(jh_specs) == 33, f"Expected 33 Jenny Hoyos / Outlier specs, found {len(jh_specs)}"
        for s in jh_specs:
            gate_res = validate_jenny_hoyos_readability(s)
            assert gate_res["fk_grade"] <= 5.5, f"Expected FK Grade <= 5.5 for {s['id']}, got {gate_res['fk_grade']}"
            if s["id"] in ("short_13", "short_31", "short_32", "short_33", "short_34", "short_35", "short_36", "short_37", "short_38", "short_39", "short_40", "short_41", "short_42"):
                assert gate_res["fk_grade"] <= 4.5, f"Expected FK Grade <= 4.5 for {s['id']}, got {gate_res['fk_grade']}"
            elif s["id"] in ("short_14", "short_15", "short_16", "short_17", "short_18", "short_19", "short_20", "short_21", "short_22", "short_23", "short_24", "short_25", "short_26", "short_27", "short_28", "short_29", "short_30"):
                assert gate_res["fk_grade"] <= 5.0, f"Expected FK Grade <= 5.0 for {s['id']}, got {gate_res['fk_grade']}"
        from seed_first_comments import TARGET_FIRST_COMMENTS, is_automod_safe_first_comment
        for tfc in TARGET_FIRST_COMMENTS:
            assert is_automod_safe_first_comment(tfc["comment"]), f"First comment for {tfc['id']} failed automod-safe check: {tfc['comment']}"
            if tfc["id"] in ("short_18", "short_19", "short_20", "short_21", "short_22", "short_23", "short_24", "short_25", "short_26", "short_27", "short_28", "short_29", "short_30", "short_31", "short_32", "short_33", "short_34", "short_35", "short_36", "short_37", "short_38", "short_39", "short_40", "short_41", "short_42"):
                assert "Compatibility % score" in tfc["comment"] and len(tfc["comment"]) <= 145, f"Expected 2-Birthday Match % Bait on {tfc['id']}, got {tfc['comment']}"
        from lead_capture_worker import build_cart_recovery_email, collect_lead_partner_checks_and_intent, calculate_5_systems
        geet_intent = collect_lead_partner_checks_and_intent("geet08190@gmail.com", "1986-02-19", "1988-08-19")
        geet_subj, geet_plain, geet_html = build_cart_recovery_email(
            {"name": "Geet", "dob": "1986-02-19", "email": "geet08190@gmail.com", "calc": calculate_5_systems("Geet", "1986-02-19")},
            intent_info=geet_intent,
        )
        assert geet_subj == "Geet — your 96% match on Dec 23 (and why Aug 19 pulls away) 💔", f"Unexpected Geet recovery subject: {geet_subj}"
        assert "dRm8wP7VL0Md1gA0zd38404?prefilled_email=geet08190%40gmail.com" in geet_html

        # Verify Real-Time Birth-Day Compatibility % Replies in comment_reply_engine.py, tiktok_comment_responder.py & ig_comment_responder.py
        from comment_reply_engine import CommentReplyEngine, parse_birth_days_from_comment
        from ig_comment_responder import IGCommentReplyGenerator
        import tiktok_comment_responder as _tt_resp
        assert hasattr(_tt_resp, "parse_birth_days_from_comment"), "tiktok_comment_responder must expose parse_birth_days_from_comment"
        assert parse_birth_days_from_comment("14th and 23rd") == [14, 23]
        assert parse_birth_days_from_comment("me 7 him 19") == [7, 19]
        assert parse_birth_days_from_comment("Oct 12 and May 4") == [12, 4]
        assert parse_birth_days_from_comment("Born on the 19th") == [19]
        assert parse_birth_days_from_comment("7") == [7]
        assert parse_birth_days_from_comment("25th") == [25]
        c_eng = CommentReplyEngine(use_llm=False)
        ig_gen = IGCommentReplyGenerator()
        for two_day_txt, exp_pair in [("14th and 23rd", (14, 23)), ("me 7 him 19", (7, 19)), ("Oct 12 and May 4", (12, 4))]:
            tt_r = c_eng.generate_reply(two_day_txt)
            ig_r = ig_gen.generate_ig_reply(two_day_txt)
            assert tt_r["bucket"] == "A_PAIR_COMPAT" and ig_r["bucket"] == "A_PAIR_COMPAT"
            assert f"Day {exp_pair[0]} × Day {exp_pair[1]}" in tt_r["reply"]
            assert "%" in tt_r["reply"] and f"{exp_pair[0]}×{exp_pair[1]} text script in our bio link" in tt_r["reply"]
            assert len(tt_r["reply"]) <= 140 and "http" not in tt_r["reply"].lower()
            assert ig_r["reply_text"] == tt_r["reply"]
        for one_day_txt, exp_d in [("Born on the 19th", 19), ("7", 7), ("25th", 25)]:
            tt_r1 = c_eng.generate_reply(one_day_txt)
            ig_r1 = ig_gen.generate_ig_reply(one_day_txt)
            assert tt_r1["bucket"] == "A_SINGLE_DAY_COMPAT" and ig_r1["bucket"] == "A_SINGLE_DAY_COMPAT"
            assert f"Day {exp_d} is Driver #" in tt_r1["reply"]
            assert "Soulmate days:" in tt_r1["reply"] and "Karmic trap:" in tt_r1["reply"]
            assert len(tt_r1["reply"]) <= 140 and "http" not in tt_r1["reply"].lower()
        print("[OK] Reverse order calc_preview, <=38-char og:title, 5-Circle favicon.svg, Partner Compatibility, Cart Recovery, 1-Day/2-Day Comment Replies & Jenny Hoyos 5th-Grade Gate (short_10-27) verified!")

        # TEST 10: 390x660 TikTok In-App Browser Mobile Viewport Above-The-Fold Audit + Optional Name + 1-Tap Quick-Day Strip + 1-Tap Instant Sample Reading + $17 Impulse Tier
        print("\n--- Test 10: 390x660 TikTok In-App Browser Viewport Audit (bottom <= 635px), Blank Name Submit, #quick-day-strip, 1-Tap Sample Demo & $17 Impulse Tier ---")
        page_mob = await browser.new_page(viewport={"width": 390, "height": 660})
        demo_events = []
        async def capture_demo_webhook(route):
            req = route.request
            if req.method == "POST" and ("ntfy.sh" in req.url or "8788/webhook" in req.url):
                try:
                    import json as _json
                    demo_events.append(_json.loads(req.post_data or "{}"))
                except Exception:
                    pass
                await route.fulfill(status=200, body="ok")
            else:
                await route.continue_()
        await page_mob.add_init_script("window.__S5_ENGAGED_MS = 120;")
        await page_mob.route("**/*", capture_demo_webhook)
        await page_mob.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels&public_test=1&force_telemetry=1")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        await asyncio.sleep(0.25)
        eng_evs = [e for e in demo_events if e.get("event_type") == "hero_engaged_3s"]
        assert len(eng_evs) >= 1, f"Expected hero_engaged_3s event on view1, got {[e.get('event_type') for e in demo_events]}"
        assert await page_mob.is_visible('.system-strip') is False, "Expected .system-strip to be hidden on <600px mobile viewport"
        assert await page_mob.is_visible('#hero-email-block') is False, "Expected #hero-email-block to be collapsed by default on <600px mobile viewport"
        assert await page_mob.is_visible('#quick-day-hero-box') is True, "Expected #quick-day-hero-box visible at top of view1"
        assert await page_mob.is_visible('#hero-live-imessage-preview') is True, "Expected #hero-live-imessage-preview visible at 0.0s on view1"
        assert await page_mob.is_visible('#hero-podcast-host-pill') is True, "Expected #hero-podcast-host-pill (Maya x Julian) visible inside #hero-live-imessage-preview on view1"
        host_pill_txt = await page_mob.locator('#hero-podcast-host-pill').inner_text()
        assert "MAYA & JULIAN · NUMEROLOGY & RELATIONSHIP EXPERTS" in host_pill_txt.upper(), f"Unexpected #hero-podcast-host-pill text: {host_pill_txt}"
        qbox = await page_mob.locator('#quick-day-hero-box').bounding_box()
        assert qbox is not None and qbox["y"] < 140, f"Expected #quick-day-hero-box at very top of view1 (y < 140px), got y={qbox['y'] if qbox else None}"
        for sel in ('#quick-day-hero-box', '#quick-day-strip', '#hero-live-imessage-preview', '#fullName', '#dobMonth', '#dobDay', '#dobYear', '#heroForm button[type="submit"]', '#hero-micro-badge', '#btn-instant-demo'):
            box = await page_mob.locator(sel).first.bounding_box()
            assert box is not None, f"Missing bounding box for {sel} at 390x660"
            bottom_y = box["y"] + box["height"]
            assert bottom_y <= 635, f"Expected {sel} bottom <= 635px on 390x660 TikTok In-App Browser viewport, got {bottom_y:.1f}px"

        # 10a) Verify submitting Hero form with #fullName left blank + Month/Day/Year selected succeeds without error
        await page_mob.fill('#fullName', '')
        await page_mob.select_option('#dobMonth', '07')
        await page_mob.select_option('#dobDay', '16')
        await page_mob.select_option('#dobYear', '1994')
        await page_mob.click('#heroForm button[type="submit"]')
        await page_mob.wait_for_selector('#view-teaser:not(.hidden)', timeout=6000)
        assert await page_mob.is_visible('#teaser-relationship-clash') is True, "Expected Teaser view to open when #fullName is left blank!"

        # 10b) Return to Hero and verify 2-Tap "Your Day × Their Day" Instant Match Calculator on view1 (#quick-day-strip -> #hero-partner-day-strip)
        await page_mob.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels&public_test=1&force_telemetry=1")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        assert await page_mob.is_visible('#hero-partner-day-strip') is False, "Expected #hero-partner-day-strip hidden on initial load"
        await page_mob.click('#quick-day-strip button[data-action="quick-day"][data-day="19"]')
        await asyncio.sleep(0.15)
        assert await page_mob.is_visible('#hero-partner-day-strip') is True, "Expected #hero-partner-day-strip revealed in-place after tapping Step 1 day"
        step2_lbl = await page_mob.locator('#hero-partner-day-label').inner_text()
        assert "2️⃣" in step2_lbl and "Day 19" in step2_lbl, f"Unexpected #hero-partner-day-label: {step2_lbl}"
        await page_mob.click('#hero-partner-day-strip button[data-action="hero-partner-day"][data-day="23"]')
        await page_mob.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        await asyncio.sleep(0.2)
        pair_evs = [e for e in demo_events if e.get("event_type") == "hero_pair_match_selected"]
        assert len(pair_evs) >= 1 and (pair_evs[-1].get("extra") or {}).get("my_day") == 19 and (pair_evs[-1].get("extra") or {}).get("partner_day") == 23, f"Expected hero_pair_match_selected(19, 23), got {pair_evs}"
        assert await page_mob.is_visible('#partner-compat-result') is True, "Expected #partner-compat-result immediately visible after 2-tap hero match"
        assert await page_mob.is_visible('#situation-chip-strip') is True, "Expected #situation-chip-strip immediately visible after 2-tap hero match"
        assert await page_mob.is_visible('#flip-chase-preview-bubble') is True, "Expected #flip-chase-preview-bubble immediately visible after 2-tap hero match"

        # Also verify 1-tap single-day skip (#btn-hero-single-day-skip) from view1 opens Teaser with #quick-day-banner
        await page_mob.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels&public_test=1&force_telemetry=1")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        await page_mob.click('#quick-day-strip button[data-action="quick-day"][data-day="25"]')
        await page_mob.wait_for_selector('#hero-partner-day-strip:not(.hidden)', timeout=3000)
        await page_mob.click('#btn-hero-single-day-skip')
        await page_mob.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        await asyncio.sleep(0.2)
        qd_ev_list = [e for e in demo_events if e.get("event_type") == "quick_day_selected"]
        assert len(qd_ev_list) >= 1, f"Expected quick_day_selected event, got {[e.get('event_type') for e in demo_events]}"
        assert (qd_ev_list[-1].get("extra") or {}).get("birth_day") == 25, f"Expected birth_day=25 in quick_day_selected: {qd_ev_list[-1]}"
        assert await page_mob.is_visible('#quick-day-banner') is True, "Expected #quick-day-banner visible on Teaser after single-day skip click"
        assert await page_mob.is_visible('#btn-jump-partner-strip') is True, "Expected #btn-jump-partner-strip inside #quick-day-banner"

        # 10c) Verify tapping a partner day (1-31) in #partner-quick-day-strip immediately fires partner_check_run without Partner Month/Year dropdowns & renders #flip-chase-preview-bubble + #btn-unlock-text-script + #downsell-script-only-box
        assert await page_mob.is_visible('#partner-quick-day-strip') is True, "Expected #partner-quick-day-strip visible inside #partner-compat-box"
        pqd_box = await page_mob.locator('#partner-quick-day-strip').bounding_box()
        assert pqd_box is not None and pqd_box["y"] >= 0 and (pqd_box["y"] + pqd_box["height"]) <= 635, f"Expected #partner-quick-day-strip immediately visible inside 390x660 viewport after quick_day_selected, got {pqd_box}"
        await page_mob.evaluate("window.__S5_HESITATION_MS = 120;")
        await page_mob.click('#partner-quick-day-strip button[data-action="partner-quick-day"][data-day="16"]')
        await asyncio.sleep(0.25)
        assert await page_mob.is_visible('#partner-compat-result') is True, "Expected #partner-compat-result to render immediately on 1-tap partner day click"
        assert await page_mob.is_visible('#partner-hesitation-callout') is True, "Expected #partner-hesitation-callout to reveal inside #partner-compat-email-box after hesitation timer!"
        assert await page_mob.is_visible('#downsell-script-only-box') is True, "Expected #downsell-script-only-box to reveal after hesitation timer!"
        ds_txt = await page_mob.locator('#downsell-script-only-box').inner_text()
        assert "WAIT — JUST WANT THE UNBLURRED TEXT MESSAGE?" in ds_txt.upper(), f"Unexpected #downsell-script-only-box text: {ds_txt}"
        hes_txt = await page_mob.locator('#partner-hesitation-callout').inner_text()
        assert "Not ready for the full $17 unlock yet?" in hes_txt and "[Day 25 × Day 16] Compatibility Breakdown + Opening Reset Line" in hes_txt, f"Unexpected #partner-hesitation-callout text: {hes_txt}"
        has_pulse_cls = await page_mob.evaluate("document.querySelector('#partner-compat-email-box').classList.contains('gold-pulse-highlight')")
        assert has_pulse_cls is True, "Expected #partner-compat-email-box to have .gold-pulse-highlight class after hesitation timer!"
        p_qd_evs = [e for e in demo_events if e.get("event_type") == "partner_check_run"]
        assert len(p_qd_evs) >= 1, f"Expected partner_check_run after tapping partner day 16, got {[e.get('event_type') for e in demo_events]}"
        assert (p_qd_evs[-1].get("extra") or {}).get("via_quick_day") is True, f"Expected via_quick_day=True in partner_check_run: {p_qd_evs[-1]}"
        assert await page_mob.is_visible('#flip-chase-preview-bubble') is True, "Expected #flip-chase-preview-bubble visible inside #partner-compat-result"
        assert await page_mob.is_visible('#julian-insider-take-box') is True, "Expected #julian-insider-take-box visible above #flip-chase-preview-bubble"
        assert await page_mob.is_visible('#situation-chip-strip') is True, "Expected #situation-chip-strip visible above #flip-chase-preview-bubble"
        sit_chip_count = await page_mob.locator('#situation-chip-strip .situation-chip').count()
        assert sit_chip_count == 4, f"Expected 4 situation chips, got {sit_chip_count}"
        initial_leadin = await page_mob.locator('#imessage-leadin-text').inner_text()
        initial_julian_take = await page_mob.locator('#julian-insider-take-text').inner_text()
        assert "Day 16" in initial_julian_take and "leaves you on read" in initial_julian_take, f"Unexpected initial #julian-insider-take-text: {initial_julian_take}"
        await page_mob.click('#situation-chip-strip .situation-chip[data-situation="cold"]')
        await asyncio.sleep(0.15)
        cold_leadin = await page_mob.locator('#imessage-leadin-text').inner_text()
        cold_julian_take = await page_mob.locator('#julian-insider-take-text').inner_text()
        assert cold_leadin != initial_leadin and "energy shifted" in cold_leadin.lower(), f"Expected #imessage-leadin-text to update on situation chip click, got '{cold_leadin}'"
        assert cold_julian_take != initial_julian_take and "acts cold" in cold_julian_take, f"Expected #julian-insider-take-text to update on situation chip click, got '{cold_julian_take}'"
        sit_evs = [e for e in demo_events if e.get("event_type") == "situation_chip_clicked"]
        assert len(sit_evs) >= 1 and (sit_evs[-1].get("extra") or {}).get("situation") == "cold", f"Expected situation_chip_clicked telemetry for 'cold', got {sit_evs}"
        bubble_txt = await page_mob.locator('#flip-chase-preview-bubble').inner_text()
        assert 'YOUR CUSTOM "FLIP THE CHASE" TEXT SCRIPT (BIRTH DAY 25 × PARTNER DAY 16)' in bubble_txt.upper(), f"Unexpected bubble header: {bubble_txt}"
        assert await page_mob.is_visible('#btn-unlock-text-script') is True, "Expected #btn-unlock-text-script visible inside #flip-chase-preview-bubble"
        unlock_btn_txt = await page_mob.locator('#btn-unlock-text-script').inner_text()
        assert "best & worst days to text them ($17)" in unlock_btn_txt.lower(), f"Unexpected #btn-unlock-text-script text: {unlock_btn_txt}"
        blur_style = await page_mob.locator('#flip-chase-preview-bubble .imessage-blurred').first.get_attribute('style')
        assert 'blur(5px)' in (blur_style or ''), f"Expected blur(5px) on .imessage-blurred, got {blur_style}"

        # Intercept Stripe redirect for #btn-unlock-text-script and verify it routes to $17 love_mini with trigger='unlock_text_script_17'
        script_stripe_urls = []
        async def mock_script_stripe_route(route):
            script_stripe_urls.append(route.request.url)
            await route.fulfill(status=200, body="stripe_mock_script")
        await page_mob.route("https://buy.stripe.com/**", mock_script_stripe_route)
        await page_mob.click('#btn-unlock-text-script')
        await asyncio.sleep(0.25)
        script_co_evs = [
            e for e in demo_events
            if e.get("event_type") == "checkout_clicked"
            and (e.get("extra") or {}).get("tier") == "love_mini"
            and (e.get("extra") or {}).get("trigger") == "unlock_text_script_17"
        ]
        assert len(script_co_evs) >= 1, f"Expected checkout_clicked with tier='love_mini' and trigger='unlock_text_script_17', got {demo_events}"
        assert any("dRm8wP7VL0Md1gA0zd38404" in u for u in script_stripe_urls), f"Expected $17 Stripe link redirect from #btn-unlock-text-script, got {script_stripe_urls}"
        await page_mob.unroute("https://buy.stripe.com/**")

        # Return to Hero to test #btn-instant-demo
        await page_mob.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels&public_test=1&force_telemetry=1")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        micro_txt = await page_mob.locator('#hero-micro-badge').inner_text()
        assert "Takes 5 seconds" in micro_txt and "No birth time needed" in micro_txt and "Instant Partner Compatibility check on next screen" in micro_txt, f"Unexpected micro-badge: {micro_txt}"
        demo_btn_txt = await page_mob.locator('#btn-instant-demo').inner_text()
        assert "preview a real sample reading (7th Birthday" in demo_btn_txt, f"Unexpected #btn-instant-demo text: {demo_btn_txt}"

        # Click #btn-instant-demo and verify demo_preview_clicked + Chloe (1998-07-16) + Partner (1996-04-13) + #sample-reading-banner
        await page_mob.click('#btn-instant-demo')
        await page_mob.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        await asyncio.sleep(0.2)
        demo_ev_list = [e for e in demo_events if e.get("event_type") == "demo_preview_clicked"]
        assert len(demo_ev_list) >= 1, f"Expected demo_preview_clicked event, got {[e.get('event_type') for e in demo_events]}"
        assert (demo_ev_list[-1].get("extra") or {}).get("sample") == "7_vs_4"
        assert await page_mob.is_visible('#sample-reading-banner') is True, "Expected #sample-reading-banner to be visible"
        banner_txt = await page_mob.locator('#sample-reading-banner').inner_text()
        assert "Viewing Sample Reading (Chloe" in banner_txt and "Tap Here To Enter Your Real Birthday" in banner_txt, f"Unexpected banner text: {banner_txt}"
        assert await page_mob.is_visible('#partner-compat-result') is True, "Expected #partner-compat-result pre-calculated on sample reading"
        assert await page_mob.locator('#partnerDobMonth').input_value() == "04"
        assert await page_mob.locator('#partnerDobDay').input_value() == "13"
        assert await page_mob.locator('#partnerDobYear').input_value() == "1996"

        # Verify $17 Impulse Tier renders and fires checkout_clicked with tier="love_mini" and redirects to dedicated $17 Stripe link
        mini_cfg = await page_mob.evaluate("() => CONFIG.STRIPE_LINK_MINI")
        assert mini_cfg == "https://buy.stripe.com/dRm8wP7VL0Md1gA0zd38404", f"Expected dedicated $17 Stripe link, got {mini_cfg}"
        assert await page_mob.is_visible('#tier-card-mini') is True, "Expected #tier-card-mini ($17 tier) visible"
        assert await page_mob.is_visible('#btn-checkout-mini') is True, "Expected #btn-checkout-mini visible"
        mini_card_txt = await page_mob.locator('#tier-card-mini').inner_text()
        base_card_txt = await page_mob.locator('#tier-card-base').inner_text()
        assert 'Flip The Chase' in mini_card_txt, f"Expected 'Flip The Chase' Text Script in #tier-card-mini, got {mini_card_txt}"
        assert 'Flip The Chase' in base_card_txt, f"Expected 'Flip The Chase' Text Script in #tier-card-base, got {base_card_txt}"
        intercepted_stripe_urls = []
        async def mock_stripe_route(route):
            intercepted_stripe_urls.append(route.request.url)
            await route.fulfill(status=200, body="stripe_mock")
        await page_mob.route("https://buy.stripe.com/**", mock_stripe_route)
        await page_mob.click('#btn-checkout-mini')
        await asyncio.sleep(0.25)
        mini_co_evs = [e for e in demo_events if e.get("event_type") == "checkout_clicked" and (e.get("extra") or {}).get("tier") == "love_mini"]
        assert len(mini_co_evs) >= 1, f"Expected checkout_clicked with tier='love_mini', got {demo_events}"
        assert (mini_co_evs[-1].get("extra") or {}).get("total") == 17
        assert any("dRm8wP7VL0Md1gA0zd38404" in u for u in intercepted_stripe_urls), f"Expected navigation to $17 Stripe link dRm8wP7VL0Md1gA0zd38404, got {intercepted_stripe_urls}"

        # Verify visiting /?tier=love_mini&unlocked=true renders the unlocked Full Text Script & Best Days To Text Report cleanly
        await page_mob.goto("http://127.0.0.1:8080/?tier=love_mini&unlocked=true")
        await page_mob.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        assert await page_mob.is_visible('#partner-synastry-love-timing-report') is True, "Expected #partner-synastry-love-timing-report visible on ?tier=love_mini&unlocked=true"
        mini_rep_txt = await page_mob.locator('#partner-synastry-love-timing-report').inner_text()
        assert "THE BEST & WORST DAYS TO TEXT THEM" in mini_rep_txt.upper()
        assert "3 DATES THIS MONTH THEY PULL CLOSER" in mini_rep_txt.upper()

        # Re-open sample reading if Stripe mock navigated, then click "Tap Here To Enter Your Real Birthday"
        await page_mob.goto("http://127.0.0.1:8080/?utm_source=ig_bio&cohort=ig_reels&force_telemetry=1")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        await page_mob.click('#btn-instant-demo')
        await page_mob.wait_for_selector('#sample-reading-banner', timeout=5000)
        await page_mob.click('#btn-enter-real-birthday')
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=5000)
        fn_val = await page_mob.locator('#fullName').input_value()
        assert fn_val == "", f"Expected #fullName to be cleared after clicking enter-real-birthday, got {fn_val!r}"
        is_fn_focused = await page_mob.evaluate("document.activeElement && document.activeElement.id === 'fullName'")
        assert is_fn_focused is True, "Expected #fullName to be focused after clicking enter-real-birthday"

        # Verify viral partner share deep-link (/?d1=19&d2=23) and #btn-share-partner-match
        demo_events.clear()
        await page_mob.goto("http://127.0.0.1:8080/?d1=19&d2=23&utm_source=partner_share&force_telemetry=1")
        await page_mob.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)
        await asyncio.sleep(0.25)
        assert await page_mob.is_visible('#partner-compat-result') is True, "Expected #partner-compat-result visible on ?d1=19&d2=23"
        assert await page_mob.is_visible('#flip-chase-preview-bubble') is True, "Expected #flip-chase-preview-bubble visible on ?d1=19&d2=23"
        assert await page_mob.is_visible('#btn-share-partner-match') is True, "Expected #btn-share-partner-match visible on ?d1=19&d2=23"
        compat_txt = await page_mob.locator('#partner-compat-result').inner_text()
        assert "BIRTH DAY 19 × PARTNER DAY 23" in compat_txt.upper(), f"Expected BIRTH DAY 19 × PARTNER DAY 23 in #partner-compat-result, got {compat_txt}"
        shared_open_evs = [e for e in demo_events if e.get("event_type") == "shared_match_opened"]
        assert len(shared_open_evs) >= 1, f"Expected shared_match_opened telemetry event on ?d1=19&d2=23, got {[e.get('event_type') for e in demo_events]}"
        assert (shared_open_evs[-1].get("extra") or {}).get("d1") == 19 and (shared_open_evs[-1].get("extra") or {}).get("d2") == 23

        await page_mob.click('#btn-share-partner-match')
        await asyncio.sleep(0.25)
        shared_click_evs = [e for e in demo_events if e.get("event_type") == "partner_match_shared"]
        assert len(shared_click_evs) >= 1, f"Expected partner_match_shared telemetry event after clicking #btn-share-partner-match, got {[e.get('event_type') for e in demo_events]}"

        # Verify #crush-text-decoder ("Paste Their Last Text" Decoder) and #live-advisor-upsell-card (Secondary Affiliate / Advisor Slot)
        assert await page_mob.is_visible('#crush-text-decoder') is True, "Expected #crush-text-decoder visible inside #partner-compat-result"
        assert await page_mob.is_visible('#crush-last-text-input') is True, "Expected #crush-last-text-input visible"
        assert await page_mob.is_visible('#btn-decode-crush-text') is True, "Expected #btn-decode-crush-text visible"
        assert await page_mob.is_visible('#crush-text-decoded-output') is False, "Expected #crush-text-decoded-output hidden before decoding"
        pre_decode_leadin = await page_mob.locator('#imessage-leadin-text').inner_text()
        await page_mob.fill('#crush-last-text-input', 'sorry been super busy this week')
        await page_mob.click('#btn-decode-crush-text')
        await asyncio.sleep(0.2)
        assert await page_mob.is_visible('#crush-text-decoded-output') is True, "Expected #crush-text-decoded-output visible after clicking #btn-decode-crush-text"
        decoded_out_txt = await page_mob.locator('#crush-text-decoded-output').inner_text()
        assert "Why a Day 23" in decoded_out_txt, f"Expected 'Why a Day 23' in #crush-text-decoded-output, got '{decoded_out_txt}'"
        post_decode_leadin = await page_mob.locator('#imessage-leadin-text').inner_text()
        assert post_decode_leadin != pre_decode_leadin and ("packed week" in post_decode_leadin.lower() or "swamped" in post_decode_leadin.lower()), f"Expected #imessage-leadin-text to update after decoding busy text, got '{post_decode_leadin}'"
        decode_evs = [e for e in demo_events if e.get("event_type") == "crush_text_decoded"]
        assert len(decode_evs) >= 1, f"Expected crush_text_decoded telemetry event, got {[e.get('event_type') for e in demo_events]}"
        dec_extra = decode_evs[-1].get("extra") or {}
        assert dec_extra.get("intent_category") == "excuse_busy" and dec_extra.get("partner_day") == 23 and "sorry been super busy" not in str(decode_evs[-1]), f"Unexpected crush_text_decoded payload: {decode_evs[-1]}"

        assert await page_mob.is_visible('#live-advisor-upsell-card') is True, "Expected #live-advisor-upsell-card visible inside #partner-compat-result"
        assert await page_mob.is_visible('#btn-live-advisor-affiliate') is True, "Expected #btn-live-advisor-affiliate visible"
        adv_btn_txt = await page_mob.locator('#btn-live-advisor-affiliate').inner_text()
        assert "priority 1-on-1 compatibility & text analysis unlock ($17 express / $37 full)" in adv_btn_txt.lower(), f"Unexpected #btn-live-advisor-affiliate text: {adv_btn_txt}"
        await page_mob.evaluate("window.open = (u) => { window.__OPENED_AFF_URL = u; return null; };")
        await page_mob.click('#btn-live-advisor-affiliate')
        await asyncio.sleep(0.2)
        adv_evs = [e for e in demo_events if e.get("event_type") == "advisor_affiliate_clicked"]
        assert len(adv_evs) >= 1, f"Expected advisor_affiliate_clicked telemetry event, got {[e.get('event_type') for e in demo_events]}"
        assert (adv_evs[-1].get("extra") or {}).get("d1") == 19 and (adv_evs[-1].get("extra") or {}).get("d2") == 23
        opened_aff_url = await page_mob.evaluate("() => window.__LAST_ADVISOR_AFFILIATE_URL || window.__OPENED_AFF_URL || ''")
        assert "dRm8wP7VL0Md1gA0zd38404" in opened_aff_url, f"Expected $17 Stripe URL dRm8wP7VL0Md1gA0zd38404 on #btn-live-advisor-affiliate click, got '{opened_aff_url}'"
        assert await page_mob.is_visible('#priority-unlock-modal') is True, "Expected #priority-unlock-modal to open on #btn-live-advisor-affiliate click"
        modal_17_href = await page_mob.locator('#btn-priority-modal-17').get_attribute('href')
        modal_37_href = await page_mob.locator('#btn-priority-modal-37').get_attribute('href')
        assert "dRm8wP7VL0Md1gA0zd38404" in (modal_17_href or ""), f"Expected $17 Stripe URL in #btn-priority-modal-17, got '{modal_17_href}'"
        assert "6oU7sLek90MdbVechV38401" in (modal_37_href or ""), f"Expected $37 Stripe URL in #btn-priority-modal-37, got '{modal_37_href}'"
        await page_mob.click('#btn-close-priority-modal')
        await asyncio.sleep(0.1)

        # 10d) Mobile Input Focus/Blur Horizontal-Alignment E2E Audit (390x660):
        # Tap/focus #partner-compat-email-input and #crush-last-text-input, then blur/click outside without typing.
        await page_mob.focus('#partner-compat-email-input')
        await page_mob.evaluate("document.querySelector('#partner-compat-email-input').blur()")
        await page_mob.focus('#crush-last-text-input')
        await page_mob.evaluate("document.querySelector('#crush-last-text-input').blur()")
        await asyncio.sleep(0.15)
        scroll_metrics = await page_mob.evaluate("() => ({ scrollWidth: document.documentElement.scrollWidth, scrollX: window.scrollX, bodyScrollLeft: document.body.scrollLeft })")
        assert scroll_metrics["scrollWidth"] <= 390, f"Expected scrollWidth <= 390 on 390x660 mobile viewport, got {scroll_metrics}"
        assert scroll_metrics["scrollX"] == 0 and scroll_metrics["bodyScrollLeft"] == 0, f"Expected scrollX === 0 after input focus/blur, got {scroll_metrics}"

        # Assert every visible heading ('YOUR BIRTH CODE', 'READING ONE SYSTEM') has boundingBox().x >= 8 (never cut off on the left!)
        h1_box = await page_mob.locator('#teaser-root h1').first.bounding_box()
        assert h1_box is not None and h1_box["x"] >= 8, f"Expected #teaser-root h1 ('YOUR BIRTH CODE') x >= 8px, got {h1_box}"
        prob_h3_box = await page_mob.locator('#teaser-root h3', has_text="Reading One System").first.bounding_box()
        assert prob_h3_box is not None and prob_h3_box["x"] >= 8, f"Expected 'Reading One System' heading x >= 8px, got {prob_h3_box}"

        # Assert Julian's badge reads 'Julian · Numerology & Relationship Expert' and his avatar is circular (44x44, borderRadius 50%)
        julian_heading_txt = await page_mob.locator('#julian-insider-take-heading').inner_text()
        assert "Julian · Numerology & Relationship Expert" in julian_heading_txt, f"Expected 'Julian · Numerology & Relationship Expert', got '{julian_heading_txt}'"
        julian_img_style = await page_mob.evaluate("() => { const img = document.querySelector('#julian-insider-take-box img'); const cs = getComputedStyle(img); return { w: img.getBoundingClientRect().width, h: img.getBoundingClientRect().height, br: cs.borderRadius }; }")
        assert 40 <= julian_img_style["w"] <= 48 and 40 <= julian_img_style["h"] <= 48 and ("50%" in julian_img_style["br"] or "22px" in julian_img_style["br"]), f"Expected circular 44x44 Julian avatar, got {julian_img_style}"

        # Assert #tier-card-base says 'for You & Your Partner.' (never 'for Your.') when name is blank
        tier_base_default_txt = await page_mob.locator('#tier-card-base').inner_text()
        assert "for You & Your Partner." in tier_base_default_txt and "for Your." not in tier_base_default_txt, f"Unexpected #tier-card-base default name text: {tier_base_default_txt}"

        # Submit email in #partner-compat-email-input and assert:
        # 1) #btn-vip-fast-action-17 has display === 'block' (does NOT split into 3 flex columns)
        # 2) Duplicate boxes (#partner-compat-email-box, #downsell-script-only-box, #downsell-fast-email-wrap) are hidden so only ONE clean $17 VIP CTA card (#vip-fast-action-offer) is visible
        await page_mob.fill('#partner-compat-email-input', 'mobile.audit@gmail.com')
        await page_mob.click('#btn-save-partner-email')
        await asyncio.sleep(0.2)
        vip_btn_display = await page_mob.evaluate("() => getComputedStyle(document.querySelector('#btn-vip-fast-action-17')).display")
        assert vip_btn_display == "block", f"Expected #btn-vip-fast-action-17 display === 'block', got '{vip_btn_display}'"
        assert await page_mob.is_visible('#vip-fast-action-offer') is True, "Expected #vip-fast-action-offer visible after email unlock"
        assert await page_mob.is_visible('#partner-compat-email-box') is False, "Expected duplicate #partner-compat-email-box hidden after Part 1 unlock"
        assert await page_mob.is_visible('#downsell-script-only-box') is False, "Expected duplicate #downsell-script-only-box hidden after Part 1 unlock"
        assert await page_mob.is_visible('#downsell-fast-email-wrap') is False, "Expected duplicate #downsell-fast-email-wrap hidden after Part 1 unlock"

        await page_mob.close()
        print("[OK] 390x844 Mobile Viewport Above-The-Fold Audit, 1-Tap Sample Reading Pill, $17 Impulse Tier & ?d1=19&d2=23 Viral Partner Share verified!")

        await browser.close()
    print("\nALL PRODUCTION READINESS & VIP TESTS PASSED WITH 100% SUCCESS!")

if __name__ == '__main__':
    asyncio.run(test_all())
