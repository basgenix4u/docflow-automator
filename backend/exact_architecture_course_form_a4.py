import os
import asyncio
from playwright.async_api import async_playwright

async def run_course_form_a4_engine(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_1Page_CourseForm_ENG_COE_21_013_A4.pdf"
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_full_path = os.path.join(out_dir, output_filename)

    print("=== EXACT ARCHITECTURE A4 COURSE FORM ENGINE INITIALIZED ===")
    print(f"User: {username} | Target Output: {pdf_full_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            # 1. Pre-clear session lock
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            # 2. Login
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

            print("--> Login Successful! Navigating to Course Form selection form...")

            # 3. Navigate to Print Completed Course Form page (id=crg)
            crg_url = "https://ug.fuwportal.edu.ng/print_course_form.php?id=crg&r_val=U3R1ZGVudA=="
            action_link = await page.query_selector("a[href*='id=crg']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto(crg_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # 4. Auto-Fill Session & Semester
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Auto-selected Session: '{opt_text}' ({first_val})")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Auto-selected Semester: '{opt_text}' ({first_val})")
                    await semester_select.select_option(first_val)

            # 5. Submit and Intercept Popup Webview
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                except Exception as e:
                    print("--> No popup window, rendering in current tab:", e)

            target_page = popup_page if popup_page else page

            # 6. Wait for JS / Images / Fonts to finish
            print("\n[Step 2] Waiting for JS / Images / Fonts to finish loading...")
            await target_page.wait_for_load_state("networkidle")
            await target_page.evaluate("document.fonts.ready")
            await target_page.wait_for_timeout(2000)

            print(f"--> Captured Target Webview URL: {target_page.url}")

            # 7. Measure document.scrollWidth / scrollHeight
            print("\n[Step 3] Measuring document.scrollWidth / scrollHeight...")
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

            # 8. Set PDF page = A4 (210 x 297 mm)
            # Printable height for A4 at 96 DPI with 6mm margins = ~1075px
            printable_a4_height = 1075.0
            print(f"\n[Step 4] Target A4 Paper Boundaries: 210mm x 297mm (Printable Height: {printable_a4_height}px)")

            # 9. Calculate fit-to-page scale
            fit_scale = printable_a4_height / doc_height
            fit_scale = max(0.40, min(1.0, fit_scale))
            print(f"\n[Step 5] Calculated fit-to-page scale: {fit_scale:.4f}")

            # 10. Inject Print CSS & Export Exactly ONE A4 Page PDF
            await target_page.add_style_tag(content="""
                @page {
                    size: A4 portrait;
                    margin: 6mm;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            """)

            print(f"\n[Step 6] Rendering entire HTML at scale ({fit_scale:.4f}) into ONE A4 PDF page...")
            await target_page.pdf(
                path=pdf_full_path,
                format="A4",
                scale=fit_scale,
                print_background=True,
                margin={"top": "6mm", "bottom": "6mm", "left": "6mm", "right": "6mm"}
            )

            print(f"\n=== SUCCESS! 1-PAGE A4 COURSE FORM PDF GENERATED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Course Form Solver Error:", err)
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
    asyncio.run(run_course_form_a4_engine("ENG/COE/21/013", "olaleke", "FUW_1Page_CourseForm_ENG_COE_21_013_A4.pdf"))
