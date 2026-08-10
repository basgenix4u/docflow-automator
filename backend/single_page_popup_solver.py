import os
import asyncio
from playwright.async_api import async_playwright

async def run_single_page_popup_solver(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_1Page_ExamCard_ENG_COE_21_013_A5.pdf",
    paper_format: str = "A5"
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_full_path = os.path.join(out_dir, output_filename)

    print("=== SINGLE-PAGE AUTO-FITTING POPUP SOLVER INITIALIZED ===")
    print(f"User: {username} | Format: {paper_format} | File: {pdf_full_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            # 1. Pre-clear session lock
            print("\n1. Pre-clearing session state...")
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            # 2. Login
            print(f"2. Logging in as {username}...")
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
                print("--> Session lock detected. Retrying with auto-logout clearance...")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(3000)
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.fill("#userId", username)
                await page.fill("#password", password)
                if login_btn:
                    await login_btn.click()
                else:
                    await page.press("#password", "Enter")
                await page.wait_for_timeout(4000)

            print("--> Login Successful!")

            # 3. Navigate to Exam Card Selection Form
            print("\n3. Navigating to Print Exam Card form (print_course_form.php?id=exam&r_val=U3R1ZGVudA==)...")
            action_link = await page.query_selector("a[href*='id=exam']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # 4. Auto-Fill Session & Semester Dropdowns
            print("\n4. Auto-filling session and semester dropdowns...")
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Selected Academic Session: '{opt_text}' ({first_val})")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Selected Semester: '{opt_text}' ({first_val})")
                    await semester_select.select_option(first_val)

            # 5. Attach Popup Interceptor & Click Submit
            print("\n5. Intercepting popup window and submitting form...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                    print(f"--> POPUP WEBVIEW CAPTURED! URL: {popup_page.url}")
                except Exception as e:
                    print("--> No new popup window, rendered in same tab:", e)

            target_page = popup_page if popup_page else page
            await target_page.wait_for_load_state("networkidle")
            await target_page.wait_for_timeout(3000)

            # 6. INJECT SINGLE-PAGE AUTO-FITTING CSS CONSTRAINTS
            print(f"\n6. Injecting Single-Page Auto-Fitting CSS rules for {paper_format} paper size...")

            zoom_level = "0.75" if paper_format.upper() == "A5" else "0.88"

            await target_page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 2mm;
                }}
                html, body {{
                    height: 100% !important;
                    max-height: 100vh !important;
                    overflow: hidden !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    box-sizing: border-box !important;
                }}
                body {{
                    zoom: {zoom_level} !important;
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    transform-origin: top left;
                }}
                table {{
                    margin-top: 1px !important;
                    margin-bottom: 2px !important;
                }}
                td, th {{
                    padding: 1.5px 3px !important;
                    font-size: 7pt !important;
                    line-height: 1.05 !important;
                }}
                img {{
                    max-height: 55px !important;
                    width: auto !important;
                }}
            """)

            # 7. Export Exactly 1 Page PDF
            print(f"7. Exporting EXACT SINGLE-PAGE {paper_format} PDF to: {pdf_full_path}")
            await target_page.pdf(
                path=pdf_full_path,
                format=paper_format,
                print_background=True,
                margin={"top": "2mm", "bottom": "2mm", "left": "2mm", "right": "2mm"}
            )

            print(f"\n=== SUCCESS! 1-PAGE {paper_format} PDF GENERATED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Single Page Solver Error:", err)
            return None

        finally:
            print("\n8. Executing immediate session logout clearance...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            print("Session context closed and released cleanly.")

if __name__ == "__main__":
    asyncio.run(run_single_page_popup_solver("ENG/COE/21/013", "olaleke", "FUW_1Page_ExamCard_ENG_COE_21_013_A5.pdf", "A5"))
