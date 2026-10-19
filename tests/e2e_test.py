import asyncio
import os
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        browser = await p.chromium.launch(
            executable_path=chrome_path,
            headless=True
        )
        page = await browser.new_page()
        
        console_errors = []
        page.on('console', lambda msg: console_errors.append(f'[{msg.type}] {msg.text}') if msg.type in ['error', 'warning'] else None)
        page.on('pageerror', lambda err: console_errors.append(f'[PAGE ERROR] {err}'))

        html_path = os.path.abspath('index.html')
        file_url = f'file:///{html_path.replace(os.sep, "/")}'
        print(f"Navigating to {file_url}")
        await page.goto(file_url)

        # 1. Verify View 1 (Hero) is visible
        assert await page.is_visible('#view-hero'), "Hero view should be visible"
        print("[OK] Hero view is visible")

        # 2. Click Founder Sample button
        await page.click('button[data-action="sample"]')
        name_val = await page.input_value('#fullName')
        dob_val = await page.input_value('#birthDate')
        email_val = await page.input_value('#email')
        assert name_val == "Adam Vega", f"Expected 'Adam Vega', got '{name_val}'"
        assert dob_val == "1988-11-08", f"Expected '1988-11-08', got '{dob_val}'"
        print(f"[OK] Sample button populated inputs: {name_val}, {dob_val}, {email_val}")

        # 3. Submit calculation form
        await page.click('button[type="submit"]')
        print("[OK] Form submitted")

        # Wait for ritual overlay and transition to teaser
        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        print("[OK] Transitioned to View 2 (Teaser)")

        # Verify teaser content
        greeting = await page.inner_text('#teaser-root h1')
        print(f"[OK] Teaser greeting: '{greeting}'")
        assert "Adam" in greeting, "Greeting should contain 'Adam'"

        anchor_name = await page.inner_text('#teaser-root h2')
        print(f"[OK] Teaser anchor: '{anchor_name}'")

        # Test Order bump price calculation
        initial_total = await page.inner_text('[data-total]')
        assert "$37" in initial_total, f"Expected $37, got {initial_total}"
        print(f"[OK] Initial checkout total: {initial_total}")

        # Toggle order bump
        await page.click('#bump')
        bumped_total = await page.inner_text('[data-total]')
        assert "$84" in bumped_total, f"Expected $84, got {bumped_total}"
        print(f"[OK] Bumped checkout total: {bumped_total}")

        # 4. Click Demo Unlock to go to View 3 (Dossier)
        # Mock window.print
        await page.evaluate("window.printCalled = false; window.print = () => { window.printCalled = true; };")
        await page.click('button[data-action="demo-unlock"]')

        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        print("[OK] Transitioned to View 3 (Dossier)")

        # Verify dossier pages
        pages = await page.query_selector_all('#dossier-root section.page')
        print(f"[OK] Total dossier pages rendered: {len(pages)}")
        assert len(pages) >= 14, f"Expected at least 14 pages, got {len(pages)}"

        # Test Print button
        await page.click('button[data-action="print"]')
        print_called = await page.evaluate("window.printCalled")
        assert print_called, "window.print should have been invoked"
        print("[OK] Print/PDF trigger confirmed: window.print() was called")

        # Check console errors
        print(f"Total console errors/warnings: {len(console_errors)}")
        for err in console_errors:
            print("  ", err)

        await browser.close()
        print("\nALL AUTOMATED TESTS PASSED!")

if __name__ == '__main__':
    asyncio.run(run_test())
