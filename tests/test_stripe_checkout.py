import asyncio
from playwright.async_api import async_playwright

async def test_checkout():
    print("Testing Stripe Payment Link integration...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://127.0.0.1:8080/")

        # Verify CONFIG values
        mini_link = await page.evaluate("() => CONFIG.STRIPE_LINK_MINI")
        base_link = await page.evaluate("() => CONFIG.STRIPE_LINK_BASE")
        bump_link = await page.evaluate("() => CONFIG.STRIPE_LINK_BUMP")
        upgrade_link = await page.evaluate("() => CONFIG.STRIPE_LINK_UPGRADE")
        demo_mode = await page.evaluate("() => CONFIG.DEMO_MODE")

        print(f"Mini Link ($17): {mini_link}")
        print(f"Base Link ($37): {base_link}")
        print(f"Bump Link ($84): {bump_link}")
        print(f"Upgrade Link ($47): {upgrade_link}")
        print(f"Demo Mode: {demo_mode}")

        assert mini_link == "https://buy.stripe.com/dRm8wP7VL0Md1gA0zd38404"
        assert base_link == "https://buy.stripe.com/6oU7sLek90MdbVechV38401"
        assert bump_link == "https://buy.stripe.com/eVq28r2Br9iJe3mbdR38402"
        assert upgrade_link == "https://buy.stripe.com/28E6oHb7X3Yp2kEgyb38403"
        assert demo_mode is False, "DEMO_MODE should be false for public traffic"

        # Verify visiting /?tier=love_mini&unlocked=true renders the unlocked Partner Synastry & 90-Day Love Timing report cleanly
        page_mini = await browser.new_page()
        await page_mini.goto("http://127.0.0.1:8080/?tier=love_mini&unlocked=true")
        await page_mini.wait_for_selector("#view-dossier:not(.hidden)", timeout=5000)
        assert await page_mini.is_visible("#partner-synastry-love-timing-report") is True, "Expected #partner-synastry-love-timing-report visible on ?tier=love_mini&unlocked=true"
        rep_txt = await page_mini.locator("#partner-synastry-love-timing-report").inner_text()
        assert "PARTNER SYNASTRY & 90-DAY LOVE TIMING REPORT" in rep_txt.upper()
        await page_mini.close()

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
