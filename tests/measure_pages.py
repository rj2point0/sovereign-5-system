import asyncio
import os
from playwright.async_api import async_playwright

async def measure_pages():
    async with async_playwright() as p:
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()

        html_path = os.path.abspath('index.html')
        file_url = f'file:///{html_path.replace(os.sep, "/")}?unlocked=true&name=Adam%20Vega&dob=1988-11-08'
        await page.goto(file_url)
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)

        # Emulate print media
        await page.emulate_media(media="print")

        # Measure each section.page
        heights = await page.evaluate("""() => {
            const pages = Array.from(document.querySelectorAll('#dossier-root section.page'));
            return pages.map((p, idx) => {
                const rect = p.getBoundingClientRect();
                return {
                    index: idx + 1,
                    title: p.querySelector('.page-head span:last-child')?.textContent || (p.classList.contains('cover') ? 'Cover' : 'Unknown'),
                    scrollHeight: p.scrollHeight,
                    clientHeight: p.clientHeight,
                    offsetRatio: (p.scrollHeight / 1056).toFixed(2) // 11 inches at 96 DPI = 1056px
                };
            });
        }""")

        for h in heights:
            print(f"Page {h['index']:02d} ({h['title']}): scrollHeight={h['scrollHeight']}px (approx {h['offsetRatio']} pages)")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(measure_pages())
