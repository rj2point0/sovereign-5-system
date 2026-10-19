import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def generate():
    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    artifact_dir = r'C:\Users\User\.gemini\antigravity\brain\5be548e1-0bfd-4f21-b5d4-67c12098b05e'
    gdrive_dir = r'G:\My Drive\5_System_Numerology_MVP'
    os.makedirs(gdrive_dir, exist_ok=True)
    os.makedirs(artifact_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=chrome_path, headless=True)
        
        # 1. Mobile context (iPhone 14 / modern smartphone: 390x844, scale 2 for crisp retina display)
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        # Step A: View 1 - Hero Calculator with Founder Sample
        await page.goto('http://127.0.0.1:8080')
        await page.wait_for_selector('#view-hero', timeout=5000)
        # Click sample button
        await page.click('button[data-action="sample"]')
        await page.wait_for_timeout(300)
        
        v1_path = os.path.abspath('view1_hero_mobile.png')
        await page.screenshot(path=v1_path, full_page=False)
        print(f"[OK] Captured View 1 Hero: {v1_path}")

        # Step B: View 2 - 20% Free Teaser + Blurred Matrix + Order Bump
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        await page.wait_for_timeout(1000)
        
        # Capture Teaser overview and matrix
        v2_path = os.path.abspath('view2_teaser_mobile.png')
        await page.screenshot(path=v2_path, full_page=False)
        print(f"[OK] Captured View 2 Teaser: {v2_path}")

        # Also scroll down to capture blurred matrix + checkout card
        await page.evaluate("document.querySelector('#checkout').scrollIntoView({ behavior: 'instant' });")
        await page.wait_for_timeout(500)
        v2_checkout_path = os.path.abspath('view2_checkout_bump_mobile.png')
        await page.screenshot(path=v2_checkout_path, full_page=False)
        print(f"[OK] Captured View 2 Checkout/Bump: {v2_checkout_path}")

        # Step C: View 3 - Unlocked Full Dossier
        await page.click('button[data-action="demo-unlock"]')
        await page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        await page.wait_for_timeout(1000)
        
        v3_path = os.path.abspath('view3_dossier_mobile.png')
        await page.screenshot(path=v3_path, full_page=False)
        print(f"[OK] Captured View 3 Dossier: {v3_path}")

        # Step D: Generate Full PDF (Desktop context for exact Letter size print output)
        print_page = await browser.new_page()
        await print_page.goto('http://127.0.0.1:8080/?unlocked=true&name=Adam%20Vega&dob=1988-11-08')
        await print_page.wait_for_selector('#view-dossier:not(.hidden)', timeout=5000)
        await print_page.wait_for_timeout(1000)

        pdf_path = os.path.abspath('Adam_Vega_5_System_Sovereign_Dossier.pdf')
        await print_page.pdf(
            path=pdf_path,
            format='Letter',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        print(f"[OK] Exported PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

        await browser.close()

    # Step E: Copy all artifacts to Google Drive and Artifact Directory
    files_to_copy = [
        ('Adam_Vega_5_System_Sovereign_Dossier.pdf', pdf_path),
        ('view1_hero_mobile.png', v1_path),
        ('view2_teaser_mobile.png', v2_path),
        ('view2_checkout_bump_mobile.png', v2_checkout_path),
        ('view3_dossier_mobile.png', v3_path),
    ]

    for fname, src in files_to_copy:
        # Copy to Google Drive
        dest_gdrive = os.path.join(gdrive_dir, fname)
        shutil.copy2(src, dest_gdrive)
        # Copy to Artifact directory
        dest_art = os.path.join(artifact_dir, fname)
        shutil.copy2(src, dest_art)

    print(f"\n[ALL COMPLETE] Synced to Google Drive: {gdrive_dir}")
    print(f"[ALL COMPLETE] Synced to Artifact Dir: {artifact_dir}")

if __name__ == '__main__':
    asyncio.run(generate())
