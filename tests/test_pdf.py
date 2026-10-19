import asyncio
import os
from playwright.async_api import async_playwright

async def test_pdf_export():
    async with async_playwright() as p:
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()

        html_path = os.path.abspath('index.html')
        # Load directly in unlocked full mode
        file_url = f'file:///{html_path.replace(os.sep, "/")}?unlocked=true&name=Adam%20Vega&dob=1988-11-08&email=adam@sovereign5.com'
        await page.goto(file_url)

        # Wait for dossier
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        pages_count = len(await page.query_selector_all('#dossier-root section.page'))
        print(f"[OK] Dossier rendered with {pages_count} pages")

        pdf_path = os.path.abspath('Sovereign_Blueprint_Adam_Vega.pdf')
        await page.pdf(
            path=pdf_path,
            format='Letter',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        print(f"[OK] PDF successfully generated: {pdf_path}")
        print(f"[OK] PDF size: {os.path.getsize(pdf_path)} bytes")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_pdf_export())
