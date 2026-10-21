import asyncio
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def test_share():
    print("Testing 1-Tap Viral Share Button (EN & ES)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        # Test EN Teaser
        await page.goto("http://127.0.0.1:8080/?vip=adam&lang=en")
        await page.click('button[data-action="sample"]')
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)

        teaser_share = await page.locator('#view-teaser button[data-action="share-code"]').inner_text()
        print(f"EN Teaser Share Button text: {teaser_share}")
        assert "share with a friend" in teaser_share.lower()

        # Click share button in Teaser (in headless browser without navigator.share, it should fallback to clipboard)
        await page.click('#view-teaser button[data-action="share-code"]')
        await page.wait_for_selector('#toast.show', timeout=3000)
        toast_en = await page.locator('#toast').inner_text()
        print(f"EN Teaser Toast: {toast_en}")
        assert "link copied" in toast_en.lower() or "sovereign-5-system" in toast_en.lower()

        # Unlock Dossier
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)

        # Check Dossier Share button in action bar
        dossier_share = await page.locator('#dossier-actions button[data-action="share-code"]').inner_text()
        print(f"EN Dossier Share Button text: {dossier_share}")
        assert "share with a friend" in dossier_share.lower()

        # Test ES
        context_es = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page_es = await context_es.new_page()
        await page_es.goto("http://127.0.0.1:8080/?vip=adam&lang=es")
        await page_es.click('button[data-action="sample"]')
        await page_es.click('button[type="submit"]')
        await page_es.wait_for_selector('#view-teaser:not(.hidden)', timeout=5000)

        es_teaser_share = await page_es.locator('#view-teaser button[data-action="share-code"]').inner_text()
        print(f"ES Teaser Share Button text: {es_teaser_share}")
        assert "compartir con un amigo" in es_teaser_share.lower()

        await page_es.click('#view-teaser button[data-action="share-code"]')
        await page_es.wait_for_selector('#toast.show', timeout=3000)
        toast_es = await page_es.locator('#toast').inner_text()
        print(f"ES Teaser Toast: {toast_es}")
        assert "portapapeles" in toast_es.lower() or "sovereign-5-system" in toast_es.lower()

        await browser.close()
    print("ALL VIRAL SHARE BUTTON TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    asyncio.run(test_share())
