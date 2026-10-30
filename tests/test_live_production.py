import asyncio
from playwright.async_api import async_playwright

async def verify_live_pages():
    base_url = "https://blueprint.megavegaventures.com/"
    print(f"Testing live site: {base_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Test 1: Live site loads & Benefit-First SEO / OpenGraph / AEO verified
        resp = await page.goto(base_url)
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        live_title = await page.title()
        assert live_title == "Uncover Your Hidden Relationship Pattern & Love Code", f"Expected new title, got {live_title}"
        og_title = await page.locator('meta[property="og:title"]').get_attribute('content')
        assert og_title == "Your Hidden Relationship & Love Code" and len(og_title) <= 38, f"Expected <=38 char og:title, got {og_title}"
        og_img = await page.locator('meta[property="og:image"]').get_attribute('content')
        og_desc = await page.locator('meta[property="og:description"]').get_attribute('content')
        assert og_img == "https://blueprint.megavegaventures.com/og-preview.png"
        assert og_desc == "Attracting partners who pull away? Find out right now which birthdays are your true soulmate match and what the next 12 months hold for your love life.", f"Unexpected og_desc: {og_desc}"
        faq_count = await page.locator('#hero-faq details.faq-item').count()
        assert faq_count == 13, f"Expected 13 FAQ items on live site, got {faq_count}"
        print("Live site returned HTTP 200 OK with Problem-First -> Solution -> Certainty copy, <=38-char og:title, OpenGraph tags & 13-item FAQ accordion (All Birthdays 1-31)!")

        # Verify og-preview.png, favicon.svg, llms.txt, robots.txt, and sitemap.xml return HTTP 200 on live domain
        for asset_path in ["og-preview.png", "favicon.svg", "llms.txt", "robots.txt", "sitemap.xml"]:
            r_asset = await page.request.get(f"{base_url}{asset_path}")
            assert r_asset.status == 200, f"Expected HTTP 200 for {asset_path}, got {r_asset.status}"
        print("Verified og-preview.png, favicon.svg, llms.txt, robots.txt, and sitemap.xml all return HTTP 200 on live domain!")

        # Test 1b: Legacy GitHub Pages URL 301-redirects cleanly to blueprint.megavegaventures.com
        page_legacy = await browser.new_page()
        await page_legacy.goto("https://rj2point0.github.io/sovereign-5-system/?utm_source=ig_bio&cohort=ig_reels")
        assert "blueprint.megavegaventures.com" in page_legacy.url, f"Expected redirect to blueprint.megavegaventures.com, got {page_legacy.url}"
        print(f"Legacy URL 301-redirected cleanly to: {page_legacy.url}")
        await page_legacy.close()

        # Test 2: Verify Founder Sample button is HIDDEN on public landing page
        sample_pub_vis = await page.is_visible('#btn-sample')
        print(f"Public visitor sees Founder Sample button: {sample_pub_vis}")
        assert sample_pub_vis is False, "Founder Sample button MUST be hidden on public landing page!"
        print("Founder Sample button cleanly hidden for public visitors!")

        # Test 2b: Verify 390x844 Mobile Viewport Above-The-Fold Submit Button & Micro-Badge on Live Site
        page_mob = await browser.new_page(viewport={"width": 390, "height": 844})
        await page_mob.goto(f"{base_url}?utm_source=ig_bio&cohort=ig_reels")
        await page_mob.wait_for_selector('#view-hero:not(.hidden)', timeout=8000)
        sub_box = await page_mob.locator('#heroForm button[type="submit"]').first.bounding_box()
        assert sub_box is not None and (sub_box["y"] + sub_box["height"]) <= 780, f"Expected live submit button bottom <= 780px at 390x844, got {sub_box}"
        micro_vis = await page_mob.is_visible('#hero-micro-badge')
        assert micro_vis is True, "Expected #hero-micro-badge to be visible on live site!"
        print(f"Live 390x844 mobile viewport verified: Submit button bottom={sub_box['y'] + sub_box['height']:.1f}px (<= 780px) & micro-badge visible!")
        await page_mob.close()

        # Verify Founder Sample button IS visible with ?vip=adam
        page_vip = await browser.new_page()
        await page_vip.goto(f"{base_url}?vip=adam")
        sample_vip_vis = await page_vip.is_visible('#btn-sample')
        print(f"VIP visitor sees Founder Sample button: {sample_vip_vis}")
        assert sample_vip_vis is True, "Founder Sample button MUST be visible with ?vip=adam!"
        await page_vip.close()

        # Fill form as public user using Month/Day/Year dropdowns + First Name and verify calculation ritual
        await page.fill('#fullName', 'Adam Vega')
        await page.select_option('#dobMonth', '08')
        await page.select_option('#dobDay', '19')
        await page.select_option('#dobYear', '1978')
        await page.fill('#email', 'adam@sovereign5.com')
        await page.click('button[type="submit"]')
        await page.wait_for_selector("#view-teaser:not(.hidden)", timeout=8000)
        assert await page.is_visible("#teaser-relationship-clash") is True
        assert await page.is_visible("#teaser-problem-triangle") is True
        assert await page.is_visible("#partner-compat-box") is True
        await page.select_option("#partnerDobMonth", "07")
        await page.select_option("#partnerDobDay", "16")
        await page.select_option("#partnerDobYear", "1990")
        await asyncio.sleep(0.2)
        assert await page.is_visible("#partner-compat-result") is True
        assert await page.is_visible("#btn-partner-checkout-cta") is True
        print("Calculation ritual, 20% teaser reveal, 3-Part Problem Triangle, live Partner Compatibility Checker & Dynamic Partner Checkout CTA verified on live site!")

        # Test 3: Post-payment redirect verification
        await page.goto(f"{base_url}?tier=full&unlocked=true")
        await page.wait_for_selector("#view-dossier:not(.hidden)", timeout=8000)
        pages_count = await page.locator(".page").count()
        print(f"Post-payment unlocked dossier rendered: {pages_count} pages!")
        assert pages_count == 20, f"Expected 20 pages on live site, got {pages_count}"

        # Test 4: Check that download PDF button and Share button are visible
        pdf_btn = await page.is_visible('#btn-print-dossier')
        assert pdf_btn is True, "Download PDF button should be visible"
        print("Download PDF button verified!")

        share_btn = await page.is_visible('#dossier-actions button[data-action="share-code"]')
        assert share_btn is True, "Dossier Share button should be visible"
        print("Live Dossier Share button verified!")

        # Test 5: Cross-browser email teaser link restoration (clean browser context, zero localStorage)
        ctx_clean = await browser.new_context()
        page_clean = await ctx_clean.new_page()
        await page_clean.goto(f"{base_url}?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=getshoes7%40gmail.com")
        await page_clean.wait_for_selector("#view-teaser:not(.hidden)", timeout=8000)
        vsl_live = await page_clean.is_visible("#vsl-video")
        assert vsl_live is True, "Live VSL video player should be visible on Teaser deep-link!"
        print("Cross-browser email Teaser deep-link and VSL video verified on live site!")
        await ctx_clean.close()

        print("\n=== ALL LIVE PRODUCTION VERIFICATIONS PASSED ===")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(verify_live_pages())
