import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
        page = await browser.new_page()
        html_path = os.path.abspath('index.html')
        file_url = f'file:///{html_path.replace(os.sep, "/")}'
        await page.goto(file_url)
        res = await page.evaluate('''() => {
            const E = window.S5Engine;
            return E.calculate('Adam Vega', '1978-08-19');
        }''')
        print('Life Path:', res['pythagorean']['lifePath'])
        print('Expression:', res['pythagorean']['expression'])
        print('Soul Urge:', res['pythagorean']['soulUrge'])
        print('Personality:', res['pythagorean']['personality'])
        print('First name consonants:', res['pythagorean']['firstNameConsonants'])
        print('Chaldean:', res['chaldean']['firstName'], res['chaldean']['lastName'], res['chaldean']['total'])
        print('Vedic:', res['vedic'])
        print('Lo Shu counts:', res['loShu']['counts'])
        print('Lo Shu dominant:', res['loShu']['dominantElement'], res['loShu']['dominantNumber'])
        print('Overlap ranking:', [a['number'] for a in res['overlap']['ranking']])
        for a in res['overlap']['anchors']:
            print(f"Anchor #{a['number']} ({a['title']}): count={a['count']}, systems={a['systems']}, sources={a['sources']}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
