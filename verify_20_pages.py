import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def verify_and_export():
    print("=================================================================")
    print("  VERIFYING 20-PAGE LUXURY SOVEREIGN DOSSIER (EN & ES)           ")
    print("=================================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # -------------------------------------------------------------
        # 1. VERIFY ENGLISH (1280x900)
        # -------------------------------------------------------------
        print("\n--- 1. Testing English 20-Page Dossier ---")
        page_en = await browser.new_page(viewport={'width': 1280, 'height': 900})
        await page_en.goto('http://127.0.0.1:8080/?vip=adam&lang=en', wait_until='networkidle')

        await page_en.click('button[data-action="sample"]')
        await page_en.click('button[type="submit"]')
        await page_en.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        await page_en.click('button[data-action="demo-unlock"]')
        await page_en.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        await page_en.wait_for_timeout(800)

        pages_count_en = await page_en.locator('.page').count()
        print(f"EN Page Count: {pages_count_en}")
        assert pages_count_en == 20, f"Expected 20 pages, got {pages_count_en}"

        # Check DOM metrics across all 20 pages (screen mode)
        print("\nChecking vertical layout & footer clearance (Screen mode - EN):")
        metrics_en = await page_en.evaluate('''() => {
            const pages = Array.from(document.querySelectorAll('.page'));
            return pages.map((p, idx) => {
                const body = p.querySelector('.page-body');
                const foot = p.querySelector('.page-foot');
                const head = p.querySelector('.page-head');
                
                const pBox = p.getBoundingClientRect();
                const footBox = foot ? foot.getBoundingClientRect() : null;
                const bodyBox = body ? body.getBoundingClientRect() : null;
                
                let clearance = null;
                if (bodyBox && footBox) {
                    clearance = footBox.top - bodyBox.bottom;
                }
                
                const overflowY = p.scrollHeight - p.clientHeight;
                return {
                    page: idx + 1,
                    scrollHeight: p.scrollHeight,
                    clientHeight: p.clientHeight,
                    overflowY,
                    clearance: clearance ? Math.round(clearance) : null
                };
            });
        }''')

        for m in metrics_en:
            print(f"  Page {m['page']:2d}: scrollHeight={m['scrollHeight']}px, clientHeight={m['clientHeight']}px, overflowY={m['overflowY']}px, footer clearance={m['clearance']}px")
            # In screen mode, min-height is 1050px. If content is taller than 1050px, the flex container simply grows smoothly, which is expected for screen reading.
            # But footer clearance must always be >= 0 (no collision)
            if m['clearance'] is not None:
                assert m['clearance'] >= 0, f"Footer collision on EN Page {m['page']}! Clearance: {m['clearance']}px"

        # Check print emulation
        print("\nChecking Print Emulation (Letter size 8.5 x 11 in):")
        await page_en.emulate_media(media="print")
        print_metrics_en = await page_en.evaluate('''() => {
            const pages = Array.from(document.querySelectorAll('.page'));
            return pages.map((p, idx) => {
                const pBox = p.getBoundingClientRect();
                const body = p.querySelector('.page-body');
                const foot = p.querySelector('.page-foot');
                const footBox = foot ? foot.getBoundingClientRect() : null;
                const bodyBox = body ? body.getBoundingClientRect() : null;
                
                let clearance = null;
                if (bodyBox && footBox) {
                    clearance = footBox.top - bodyBox.bottom;
                }
                return {
                    page: idx + 1,
                    boxHeight: Math.round(pBox.height),
                    clearance: clearance !== null ? Math.round(clearance) : null
                };
            });
        }''')

        for pm in print_metrics_en:
            print(f"  Print EN Page {pm['page']:2d}: height={pm['boxHeight']}px (11in = 1056px), footer clearance={pm['clearance']}px")
            # In print mode, .page has height: 11in !important (1056px)
            assert pm['boxHeight'] <= 1057, f"Page {pm['page']} exceeds 11in print height! Got {pm['boxHeight']}px"
            if pm['clearance'] is not None:
                assert pm['clearance'] >= 0, f"Print footer collision on EN Page {pm['page']}! Clearance: {pm['clearance']}px"

        # Generate English PDF
        pdf_en_path = "Adam_Vega_5_System_Sovereign_Dossier_EN.pdf"
        await page_en.pdf(
            path=pdf_en_path,
            format="Letter",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        print(f"\n[OK] Exported EN PDF: {pdf_en_path} ({os.path.getsize(pdf_en_path):,} bytes)")

        # -------------------------------------------------------------
        # 2. VERIFY SPANISH (1280x900)
        # -------------------------------------------------------------
        print("\n--- 2. Testing Spanish 20-Page Dossier ---")
        page_es = await browser.new_page(viewport={'width': 1280, 'height': 900})
        await page_es.goto('http://127.0.0.1:8080/?vip=adam&lang=es', wait_until='networkidle')

        await page_es.click('button[data-action="sample"]')
        await page_es.click('button[type="submit"]')
        await page_es.wait_for_selector('#view-teaser:not(.hidden)', timeout=10000)
        await page_es.click('button[data-action="demo-unlock"]')
        await page_es.wait_for_selector('#view-dossier:not(.hidden)', timeout=10000)
        await page_es.wait_for_timeout(800)

        pages_count_es = await page_es.locator('.page').count()
        print(f"ES Page Count: {pages_count_es}")
        assert pages_count_es == 20, f"Expected 20 pages, got {pages_count_es}"

        # Check DOM metrics across all 20 pages (screen mode)
        print("\nChecking vertical layout & footer clearance (Screen mode - ES):")
        metrics_es = await page_es.evaluate('''() => {
            const pages = Array.from(document.querySelectorAll('.page'));
            return pages.map((p, idx) => {
                const body = p.querySelector('.page-body');
                const foot = p.querySelector('.page-foot');
                const footBox = foot ? foot.getBoundingClientRect() : null;
                const bodyBox = body ? body.getBoundingClientRect() : null;
                
                let clearance = null;
                if (bodyBox && footBox) {
                    clearance = footBox.top - bodyBox.bottom;
                }
                
                return {
                    page: idx + 1,
                    scrollHeight: p.scrollHeight,
                    clientHeight: p.clientHeight,
                    overflowY: p.scrollHeight - p.clientHeight,
                    clearance: clearance ? Math.round(clearance) : null
                };
            });
        }''')

        for m in metrics_es:
            print(f"  Page {m['page']:2d}: scrollHeight={m['scrollHeight']}px, clientHeight={m['clientHeight']}px, overflowY={m['overflowY']}px, footer clearance={m['clearance']}px")
            if m['clearance'] is not None:
                assert m['clearance'] >= 0, f"Footer collision on ES Page {m['page']}! Clearance: {m['clearance']}px"

        # Check print emulation
        print("\nChecking Print Emulation (Letter size 8.5 x 11 in - ES):")
        await page_es.emulate_media(media="print")
        print_metrics_es = await page_es.evaluate('''() => {
            const pages = Array.from(document.querySelectorAll('.page'));
            return pages.map((p, idx) => {
                const pBox = p.getBoundingClientRect();
                const body = p.querySelector('.page-body');
                const foot = p.querySelector('.page-foot');
                const footBox = foot ? foot.getBoundingClientRect() : null;
                const bodyBox = body ? body.getBoundingClientRect() : null;
                
                let clearance = null;
                if (bodyBox && footBox) {
                    clearance = footBox.top - bodyBox.bottom;
                }
                return {
                    page: idx + 1,
                    boxHeight: Math.round(pBox.height),
                    clearance: clearance !== null ? Math.round(clearance) : null
                };
            });
        }''')

        for pm in print_metrics_es:
            print(f"  Print ES Page {pm['page']:2d}: height={pm['boxHeight']}px (11in = 1056px), footer clearance={pm['clearance']}px")
            assert pm['boxHeight'] <= 1057, f"Page {pm['page']} exceeds 11in print height! Got {pm['boxHeight']}px"
            if pm['clearance'] is not None:
                assert pm['clearance'] >= 0, f"Print footer collision on ES Page {pm['page']}! Clearance: {pm['clearance']}px"

        # Generate Spanish PDF
        pdf_es_path = "Adam_Vega_5_System_Sovereign_Dossier_ES.pdf"
        await page_es.pdf(
            path=pdf_es_path,
            format="Letter",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        print(f"\n[OK] Exported ES PDF: {pdf_es_path} ({os.path.getsize(pdf_es_path):,} bytes)")

        # -------------------------------------------------------------
        # 3. VERIFY NO NUMBER TRUNCATION / NO ELLIPSIS ON DATA
        # -------------------------------------------------------------
        print("\n--- 3. Verifying Zero Ellipsis / Zero Data Truncation ---")
        ellipsis_elements = await page_en.evaluate('''() => {
            const truncated = [];
            document.querySelectorAll('.page *').forEach(el => {
                const cs = window.getComputedStyle(el);
                if (cs.textOverflow === 'ellipsis') {
                    truncated.push({
                        tag: el.tagName,
                        className: el.className,
                        text: el.innerText ? el.innerText.slice(0, 40) : ''
                    });
                }
            });
            return truncated;
        }''')
        print(f"Elements with text-overflow: ellipsis: {len(ellipsis_elements)}")
        assert len(ellipsis_elements) == 0, f"Found unexpected ellipsis elements: {ellipsis_elements}"

        await browser.close()

    # -------------------------------------------------------------
    # 4. SYNC TO GOOGLE DRIVE
    # -------------------------------------------------------------
    gdrive_dir = r"G:\My Drive\5_System_Numerology_MVP"
    if os.path.exists(gdrive_dir):
        print(f"\n--- 4. Syncing PDFs to Google Drive ({gdrive_dir}) ---")
        for f in [pdf_en_path, pdf_es_path]:
            target_path = os.path.join(gdrive_dir, f)
            shutil.copy2(f, target_path)
            print(f"  Copied {f} -> {target_path} ({os.path.getsize(target_path):,} bytes)")
    else:
        print(f"Notice: Google Drive directory {gdrive_dir} not found on this machine.")

    print("\n=================================================================")
    print("  ALL 20-PAGE VERIFICATIONS & EXPORTS PASSED SUCCESSFULLY!       ")
    print("=================================================================")

if __name__ == '__main__':
    asyncio.run(verify_and_export())
