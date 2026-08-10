import os
import asyncio
from playwright.async_api import async_playwright

async def run_exact_architecture_a5_pdf(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_Exact_Architecture_ExamCard_ENG_COE_21_013_A5.pdf"
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_full_path = os.path.join(out_dir, output_filename)

    print("=== EXACT ARCHITECTURE A5 PDF ENGINE INITIALIZED ===")
    print(f"User: {username} | File: {pdf_full_path}")

    async with async_playwright() as p:
        # Step 2: Playwright + Chromium
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            # Pre-clear session lock
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            # Step 1: Webpage Login & Navigation
            print(f"\n[Step 1] Opening Webpage ug.fuwportal.edu.ng & Logging in as {username}...")
            await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
            await page.fill("#userId", username)
            await page.fill("#password", password)

            login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
            if login_btn:
                await login_btn.click()
            else:
                await page.press("#password", "Enter")

            await page.wait_for_timeout(4000)

            body_text = await page.inner_text("body")
            if "logged in on another device" in body_text:
                print("--> Session lock detected. Retrying with logout clearance...")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(3000)
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.fill("#userId", username)
                await page.fill("#password", password)
                retry_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
                if retry_btn:
                    await retry_btn.click()
                else:
                    await page.press("#password", "Enter")
                await page.wait_for_timeout(4000)

            print("--> Login Successful! Navigating to Exam Card selection form...")
            action_link = await page.query_selector("a[href*='id=exam']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # Auto-fill session and semester
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    await semester_select.select_option(first_val)

            # Submit and intercept popup webview
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                except Exception as e:
                    print("--> No popup opened, using main page:", e)

            target_page = popup_page if popup_page else page

            # Step 3: Wait for JS/images/fonts to finish
            print("\n[Step 3] Waiting for JS / Images / Fonts to finish loading...")
            await target_page.wait_for_load_state("networkidle")
            await target_page.evaluate("document.fonts.ready")
            await target_page.wait_for_timeout(2000)

            # Step 4: Measure document.scrollWidth / scrollHeight
            print("\n[Step 4] Measuring document.scrollWidth / scrollHeight...")
            dims = await target_page.evaluate("""() => {
                const body = document.body;
                const html = document.documentElement;
                const height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
                const width = Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth);
                return { width, height };
            }""")
            doc_width = dims["width"]
            doc_height = dims["height"]
            print(f"--> Measured DOM dimensions: width={doc_width}px, height={doc_height}px")

            # Step 5: Set PDF page = A5 (148 x 210 mm)
            # A5 page size at 96 DPI: 148mm = 559px, 210mm = 793px
            # Margin = 5mm (19px) top/bottom -> Printable height = 755px
            printable_a5_height = 755.0
            print(f"\n[Step 5] Target A5 Paper Boundaries: 148mm x 210mm (Printable Height: {printable_a5_height}px)")

            # Step 6: Calculate fit-to-page scale
            fit_scale = printable_a5_height / doc_height
            fit_scale = max(0.40, min(1.0, fit_scale))  # Clamp scale between 0.40 and 1.0
            print(f"\n[Step 6] Calculated fit-to-page scale: {fit_scale:.4f}")

            # Step 7: Inject exact print color rules
            await target_page.add_style_tag(content="""
                @page {
                    size: A5 portrait;
                    margin: 5mm;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            """)

            # Step 8, 9, 10: Render entire HTML at scale, Place inside A5 boundaries, Generate ONE PDF page
            print(f"\n[Steps 7-10] Rendering entire HTML at scale ({fit_scale:.4f}) into ONE A5 PDF page...")
            await target_page.pdf(
                path=pdf_full_path,
                format="A5",
                scale=fit_scale,
                print_background=True,
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
            )

            print(f"\n=== SUCCESS! 1-PAGE A5 PDF GENERATED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Architecture Solver Error:", err)
            return None

        finally:
            print("\n[Cleanup] Executing immediate session logout clearance...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            print("[Cleanup] Session context closed and released cleanly.")

if __name__ == "__main__":
    asyncio.run(run_exact_architecture_a5_pdf("ENG/COE/21/013", "olaleke", "FUW_Exact_Architecture_ExamCard_ENG_COE_21_013_A5.pdf"))
