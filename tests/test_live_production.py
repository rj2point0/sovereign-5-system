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

        # Test 2: Sample fill and calculation ritual
        await page.click('button[data-action="sample"]')
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
