import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def run():
    print("Starting bilingual test and PDF generation...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # ---------------- 1. TEST ENGLISH ----------------
        context_en = await browser.new_context(viewport={'width': 1280, 'height': 900})
        page_en = await context_en.new_page()
        await page_en.goto('http://127.0.0.1:8080/?lang=en&vip=adam')

        # Click Founder Sample
        await page_en.click('button[data-action="sample"]')
        name_val = await page_en.input_value('#fullName')
        dob_val = await page_en.input_value('#birthDate')
        print(f"Sample loaded: Name={name_val}, DOB={dob_val}")
        assert name_val == 'Adam Vega', f"Expected Adam Vega, got {name_val}"
        assert dob_val == '1978-08-19', f"Expected 1978-08-19, got {dob_val}"

        # Submit form to open teaser
        await page_en.click('button[type="submit"]')
        await page_en.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        print("Teaser view visible.")

        # Unlock via Demo Mode
        await page_en.click('button[data-action="demo-unlock"]')
        await page_en.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        print("Dossier view unlocked.")

        # Verify pages count
        pages_count_en = await page_en.locator('.page').count()
        print(f"English Dossier Pages: {pages_count_en}")
        assert pages_count_en == 20, f"Expected 20 pages, got {pages_count_en}"

        # Measure page heights in print emulation
        await page_en.emulate_media(media="print")
        for i in range(pages_count_en):
            box = await page_en.locator(f'.page[data-page="{i+1}"]').bounding_box()
            title = await page_en.locator(f'.page[data-page="{i+1}"]').get_attribute('data-page')
            # 11in at 96dpi is 1056px
            print(f"EN Page {i+1} height: {box['height']:.1f}px (limit: 1056px)")
            if box['height'] > 1056.5:
                print(f"WARNING: EN Page {i+1} exceeds 1056px!")

        # Export English PDF
        pdf_en_path = "Adam_Vega_5_System_Sovereign_Dossier_EN.pdf"
        await page_en.pdf(
            path=pdf_en_path,
            format="Letter",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        print(f"Exported EN PDF: {pdf_en_path} ({os.path.getsize(pdf_en_path)} bytes)")

        # ---------------- 2. TEST SPANISH ----------------
        context_es = await browser.new_context(viewport={'width': 1280, 'height': 900})
        page_es = await context_es.new_page()
        await page_es.goto('http://127.0.0.1:8080/?lang=es&vip=adam')

        # Verify hero title in Spanish
        hero_title = await page_es.locator('h1[data-i18n="hero_title"]').inner_text()
        print(f"ES Hero Title: {hero_title[:45]}...")
        assert "20%" in hero_title

        # Click Founder Sample
        await page_es.click('button[data-action="sample"]')
        assert await page_es.input_value('#birthDate') == '1978-08-19'

        # Submit form to open teaser
        await page_es.click('button[type="submit"]')
        await page_es.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        
        # Check teaser Spanish elements
        teaser_h1 = await page_es.locator('#teaser-root h1').inner_text()
        print(f"ES Teaser H1: {teaser_h1}")
        assert "código" in teaser_h1 or "descifrado" in teaser_h1

        # Check Archetype in teaser
        archetype_h2 = await page_es.locator('#teaser-root h2').inner_text()
        print(f"ES #1 Anchor: {archetype_h2}")
        assert archetype_h2 == "El Analista", f"Expected El Analista, got {archetype_h2}"

        # Unlock via Demo Mode
        await page_es.click('button[data-action="demo-unlock"]')
        await page_es.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)

        # Verify pages count
        pages_count_es = await page_es.locator('.page').count()
        print(f"Spanish Dossier Pages: {pages_count_es}")
        assert pages_count_es == 20, f"Expected 20 pages, got {pages_count_es}"

        # Measure page heights in print emulation
        await page_es.emulate_media(media="print")
        for i in range(pages_count_es):
            box = await page_es.locator(f'.page[data-page="{i+1}"]').bounding_box()
            print(f"ES Page {i+1} height: {box['height']:.1f}px (limit: 1056px)")
            if box['height'] > 1056.5:
                print(f"WARNING: ES Page {i+1} exceeds 1056px!")

        # Export Spanish PDF
        pdf_es_path = "Adam_Vega_5_System_Sovereign_Dossier_ES.pdf"
        await page_es.pdf(
            path=pdf_es_path,
            format="Letter",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        print(f"Exported ES PDF: {pdf_es_path} ({os.path.getsize(pdf_es_path)} bytes)")

        # Capture mobile screenshots of Spanish version too
        mobile_context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto('http://127.0.0.1:8080/?lang=es&vip=adam')
        await mobile_page.screenshot(path='view1_hero_mobile_es.png')
        print("Captured mobile View 1 ES")

        await mobile_page.click('button[data-action="sample"]')
        await mobile_page.click('button[type="submit"]')
        await mobile_page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        await mobile_page.screenshot(path='view2_teaser_mobile_es.png')
        print("Captured mobile View 2 ES")

        await mobile_page.click('button[data-action="demo-unlock"]')
        await mobile_page.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        await mobile_page.screenshot(path='view3_dossier_mobile_es.png')
        print("Captured mobile View 3 ES")

        await browser.close()

    # ---------------- 3. COPY TO GOOGLE DRIVE / ARTIFACTS ----------------
    dest_dir = r"G:\My Drive\5_System_Numerology_MVP"
    if os.path.exists(dest_dir):
        for f in [pdf_en_path, pdf_es_path, 'view1_hero_mobile_es.png', 'view2_teaser_mobile_es.png', 'view3_dossier_mobile_es.png']:
            if os.path.exists(f):
                shutil.copy2(f, os.path.join(dest_dir, f))
                print(f"Copied {f} to {dest_dir}")
    else:
        print(f"Directory {dest_dir} not accessible, checked local.")

    print("\nALL VERIFICATIONS AND GENERATIONS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    asyncio.run(run())
