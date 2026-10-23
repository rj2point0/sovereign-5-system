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

        # TEST 2: EN | ES toggle
        print("\n--- Test 2: Language Toggle ---")
        await page.click('button[data-lang="es"]')
        es_hero = await page.locator('h1[data-i18n="hero_title"]').inner_text()
        assert "20%" in es_hero
        print(f"Spanish switch verified: {es_hero[:40]}...")

        await page.click('button[data-lang="en"]')
        en_hero = await page.locator('h1[data-i18n="hero_title"]').inner_text()
        assert "Western Numerology" in en_hero
        print(f"English switch verified: {en_hero[:40]}...")
        print("[OK] Language switcher verified!")

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

        await browser.close()
    print("\nALL PRODUCTION READINESS & VIP TESTS PASSED WITH 100% SUCCESS!")

if __name__ == '__main__':
    asyncio.run(test_all())
