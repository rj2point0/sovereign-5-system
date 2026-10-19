import asyncio
from playwright.async_api import async_playwright

async def test_checkout():
    print("Testing Stripe Payment Link integration...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://127.0.0.1:8080/")

        # Verify CONFIG values
        base_link = await page.evaluate("() => CONFIG.STRIPE_LINK_BASE")
        bump_link = await page.evaluate("() => CONFIG.STRIPE_LINK_BUMP")
        upgrade_link = await page.evaluate("() => CONFIG.STRIPE_LINK_UPGRADE")
        demo_mode = await page.evaluate("() => CONFIG.DEMO_MODE")

        print(f"Base Link: {base_link}")
        print(f"Bump Link: {bump_link}")
        print(f"Upgrade Link: {upgrade_link}")
        print(f"Demo Mode: {demo_mode}")

        assert base_link == "https://buy.stripe.com/6oU7sLek90MdbVechV38401"
        assert bump_link == "https://buy.stripe.com/eVq28r2Br9iJe3mbdR38402"
        assert upgrade_link == "https://buy.stripe.com/28E6oHb7X3Yp2kEgyb38403"
        assert demo_mode is False, "DEMO_MODE should be false for public traffic"

        # Fill Founder Sample and go to teaser
        await page.click('button[data-action="sample"]')
        await page.click('button[type="submit"]')
        await page.wait_for_selector("#view-teaser:not(.hidden)")

        # Verify that for standard public visitors, the demo unlock button is NOT visible
        public_demo_btn = await page.is_visible('button[data-action="demo-unlock"]')
        print(f"Public visitor can see demo-unlock button: {public_demo_btn}")
        assert public_demo_btn is False, "Demo unlock button should be hidden from public visitors"

        # Verify VIP founder bypass (?vip=adam)
        page_vip = await browser.new_page()
        await page_vip.goto("http://127.0.0.1:8080/?vip=adam")
        await page_vip.click('button[data-action="sample"]')
        await page_vip.click('button[type="submit"]')
        await page_vip.wait_for_selector("#view-teaser:not(.hidden)")
        vip_btn = await page_vip.is_visible('button[data-action="demo-unlock"]')
        print(f"VIP Founder bypass button visible with ?vip=adam: {vip_btn}")
        assert vip_btn is True, "Founder with ?vip=adam should see the VIP unlock button"

        print("[OK] All Stripe links, demo mode restrictions, and founder VIP tests PASSED!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_checkout())
