import asyncio
import os
import json
from playwright.async_api import async_playwright

async def verify_math():
    async with async_playwright() as p:
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        page = await browser.new_page()

        html_path = os.path.abspath('index.html')
        file_url = f'file:///{html_path.replace(os.sep, "/")}'
        await page.goto(file_url)

        # Run direct calculation in JS context
        result = await page.evaluate("""() => {
            const E = window.S5Engine;
            const res = E.calculate('Adam Vega', '1988-11-08');
            return {
                pythagorean: {
                    lifePath: res.pythagorean.lifePath,
                    expression: res.pythagorean.expression,
                    soulUrge: res.pythagorean.soulUrge,
                    personality: res.pythagorean.personality,
                    firstNameConsonants: res.pythagorean.firstNameConsonants,
                },
                chaldean: {
                    first: res.chaldean.firstName,
                    last: res.chaldean.lastName,
                    total: res.chaldean.total,
                },
                vedic: {
                    moolank: res.vedic.moolank.value,
                    bhagyank: res.vedic.bhagyank.value,
                    namank: res.vedic.namank.value,
                    moolankRuler: res.vedic.moolank.ruler.planet,
                },
                loShu: {
                    counts: res.loShu.counts,
                    dominantElement: res.loShu.dominantElement,
                    dominantNumber: res.loShu.dominantNumber,
                    hasWealthEight: res.loShu.hasWealthEight,
                },
                kabbalistic: {
                    dominantPillar: res.kabbalistic.dominantPillar,
                    activeSephirot: res.kabbalistic.activeSephirot,
                },
                overlap: {
                    anchors: res.overlap.anchors.map(a => ({
                        number: a.number,
                        count: a.count,
                        role: a.role,
                        title: a.title,
                        systems: a.systems,
                    }))
                },
                cycles: {
                    yearLength: res.cycles.yearLength,
                    periodsCount: res.cycles.periods.length,
                    currentN: res.cycles.current.n,
                    currentName: res.cycles.current.name,
                }
            };
        }""")

        print("Calculation for Adam Vega (1988-11-08):")
        print(json.dumps(result, indent=2))

        # Check Pythagorean
        # Adam Vega:
        # Birth: 1988-11-08
        # Year 1988 -> 1+9+8+8 = 26 -> 8
        # Month 11 -> 1+1 = 2
        # Day 08 -> 8
        # Life Path = 8 + 2 + 8 = 18 -> 9
        assert result['pythagorean']['lifePath']['value'] == 9, f"Expected LP 9, got {result['pythagorean']['lifePath']['value']}"
        print("[OK] Life Path is 9 (correct)")

        # Adam = A(1)+D(4)+A(1)+M(4) = 10
        # Vega = V(4)+E(5)+G(7)+A(1) = 17
        # Total Expression = 10 + 17 = 27 -> 9
        assert result['pythagorean']['expression']['value'] == 9, f"Expected Exp 9, got {result['pythagorean']['expression']['value']}"
        assert result['pythagorean']['expression']['compound'] == 27
        print("[OK] Expression is 27/9 (correct)")

        # Soul Urge (Vowels):
        # A(1), A(1), E(5), A(1) = 8
        assert result['pythagorean']['soulUrge']['value'] == 8
        print("[OK] Soul Urge is 8 (correct)")

        # First Name Consonants: D(4), M(4) = 8
        assert result['pythagorean']['firstNameConsonants']['value'] == 8
        print("[OK] First Name Consonants is 8 (correct)")

        # Chaldean:
        # A(1), D(4), A(1), M(4) = 10
        # V(6), E(5), G(3), A(1) = 15
        # Total = 25 -> 7
        assert result['chaldean']['first']['compound'] == 10
        assert result['chaldean']['last']['compound'] == 15
        assert result['chaldean']['total']['compound'] == 25
        assert result['chaldean']['total']['value'] == 7
        print("[OK] Chaldean Total is 25/7 (correct)")

        # Vedic:
        # Day 8 -> Moolank 8 (Shani / Saturn)
        assert result['vedic']['moolank'] == 8
        assert result['vedic']['moolankRuler'] == 'Shani'
        # Compact: 19881108 -> sum = 1+9+8+8+1+1+0+8 = 36 -> 9 (Bhagyank 9)
        assert result['vedic']['bhagyank'] == 9
        # Namank: Chaldean total root = 7 (Ketu)
        assert result['vedic']['namank'] == 7
        print("[OK] Vedic Moolank 8, Bhagyank 9, Namank 7 (correct)")

        # Lo Shu:
        # 19881108 + extra (LP 9, Exp 9, Chaldean 7)
        # Digits: 1, 9, 8, 8, 1, 1, 0, 8, 9, 9, 7
        # 8 count = 3 (1988, 11, 08 has three 8s!)
        assert result['loShu']['counts']['8'] == 3
        assert result['loShu']['hasWealthEight'] is True
        print("[OK] Lo Shu counts 8 three times, hasWealthEight is True (correct)")

        # Overlap anchors:
        # 8 appears in Soul Urge (8), First Name Consonants (8), Vedic Moolank (8), Lo Shu Dominant Element Earth (8) -> total 4 hits!
        # 9 appears in Life Path (9), Expression (9), Vedic Bhagyank (9) -> total 3 hits!
        # Anchor #1 is 8 (The Magnate)
        assert result['overlap']['anchors'][0]['number'] == 8
        assert result['overlap']['anchors'][0]['role'] == 'primary'
        print("[OK] Anchor #1 is 8 (The Magnate) with top frequency (correct)")

        # Rosicrucian cycles:
        assert result['cycles']['periodsCount'] == 7
        print("[OK] 7 Rosicrucian cycles generated (correct)")

        await browser.close()
        print("\nALL MATHEMATICAL VERIFICATIONS PASSED 100%!")

if __name__ == '__main__':
    asyncio.run(verify_math())
