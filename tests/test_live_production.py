import asyncio
from playwright.async_api import async_playwright

async def verify_live_pages():
    print("Testing live site: https://rj2point0.github.io/sovereign-5-system/")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Test 1: Live site loads
        resp = await page.goto("https://rj2point0.github.io/sovereign-5-system/")
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        print("Live site returned HTTP 200 OK!")

        # Test 2: Verify Founder Sample button is HIDDEN on public landing page
        sample_pub_vis = await page.is_visible('#btn-sample')
        print(f"Public visitor sees Founder Sample button: {sample_pub_vis}")
        assert sample_pub_vis is False, "Founder Sample button MUST be hidden on public landing page!"
        print("Founder Sample button cleanly hidden for public visitors!")

        # Verify Founder Sample button IS visible with ?vip=adam
        page_vip = await browser.new_page()
        await page_vip.goto("https://rj2point0.github.io/sovereign-5-system/?vip=adam")
        sample_vip_vis = await page_vip.is_visible('#btn-sample')
        print(f"VIP visitor sees Founder Sample button: {sample_vip_vis}")
        assert sample_vip_vis is True, "Founder Sample button MUST be visible with ?vip=adam!"
        await page_vip.close()

        # Fill form as public user and verify calculation ritual
        await page.fill('#fullName', 'Adam Vega')
        await page.fill('#birthDate', '1978-08-19')
        await page.fill('#email', 'adam@sovereign5.com')
        await page.click('button[type="submit"]')
        await page.wait_for_selector("#view-teaser:not(.hidden)", timeout=8000)
        print("Calculation ritual and 20% teaser reveal verified on live site!")

        # Test 3: Post-payment redirect verification
        await page.goto("https://rj2point0.github.io/sovereign-5-system/?tier=full&unlocked=true")
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

        print("\n=== ALL LIVE PRODUCTION VERIFICATIONS PASSED ===")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(verify_live_pages())
