import os
import asyncio
from playwright.async_api import async_playwright

async def test_pristine_isolated_exam_card():
    out_file = "/home/user/docflow-automator/storage/pdfs/FUW_Pristine_A5_ExamCard_ENG_COE_21_013.pdf"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            print("Logging in as ENG/COE/21/013...")
            await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
            await page.fill("#userId", "ENG/COE/21/013")
            await page.fill("#password", "olaleke")

            login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
            if login_btn:
                await login_btn.click()
            else:
                await page.press("#password", "Enter")

            await page.wait_for_timeout(4000)

            body_text = await page.inner_text("body")
            if "logged in on another device" in body_text:
                print("Session lock detected on server. Triggering auto-logout clearance...")
                await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(3000)
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.fill("#userId", "ENG/COE/21/013")
                await page.fill("#password", "olaleke")
                retry_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
                if retry_btn:
                    await retry_btn.click()
                else:
                    await page.press("#password", "Enter")
                await page.wait_for_timeout(4000)

            print("Login successful!")

            # Navigate to Exam Card Selection Form
            action_link = await page.query_selector("a[href*='id=exam']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # Auto-Fill Session & Semester
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

            # Submit and intercept popup
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                except Exception as e:
                    print("No popup intercept:", e)

            target_page = popup_page if popup_page else page
            await target_page.wait_for_load_state("networkidle")
            await target_page.wait_for_timeout(3000)

            print(f"Captured Target Webview URL: {target_page.url}")

            # Inject clean isolation CSS for pristine A5 rendering
            print("Injecting clean print isolation CSS...")
            await target_page.add_style_tag(content="""
                @page {
                    size: A5 portrait;
                    margin: 5mm;
                }
                body {
                    background: #ffffff !important;
                    font-size: 8.5pt !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    font-family: Arial, Helvetica, sans-serif !important;
                }
                /* Hide navigation, headers, footers, Tawk.to, etc. */
                #header, #menu, .navbar, .header, #tawk-default-container, iframe, center > font {
                    display: none !important;
                }
                #contents {
                    width: 100% !important;
                    margin: 0 auto !important;
                    padding: 0 !important;
                    float: none !important;
                }
                table {
                    width: 100% !important;
                    border-collapse: collapse !important;
                    margin-bottom: 6px !important;
                }
                td, th {
                    padding: 3px 5px !important;
                    font-size: 8pt !important;
                }
                img[src*='pictures'] {
                    width: 110px !important;
                    height: 110px !important;
                    object-fit: cover !important;
                    border: 1px solid #000 !important;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            """)

            print(f"Rendering pristine A5 PDF: {out_file}")
            await target_page.pdf(
                path=out_file,
                format="A5",
                print_background=True,
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
            )

            print(f"SUCCESS! Pristine A5 PDF created: {out_file}")

        finally:
            try:
                await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
            except Exception:
                pass
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_pristine_isolated_exam_card())
