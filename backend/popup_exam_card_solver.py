import os
import asyncio
from playwright.async_api import async_playwright

async def run_popup_exam_card_solver(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_Exact_Popup_ExamCard_ENG_COE_21_013_A5.pdf"
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_full_path = os.path.join(out_dir, output_filename)

    print("=== POPUP WEBVIEW INTERCEPTOR SOLVER INITIALIZED ===")
    print(f"User: {username} | Output File: {pdf_full_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            # 1. Pre-clear session lock if active
            print("\n1. Checking portal login status & clearing stale sessions...")
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

            # 4. Auto-Fill Intermediate Session & Semester Select Form
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

            # 5. ATTACH POPUP LISTENER & CLICK SUBMIT
            print("\n5. Attaching Popup Window Listener (context.expect_page) and clicking Submit...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                    print(f"--> POPUP WINDOW INTERCEPTED! Popup URL: {popup_page.url}")
                except Exception as e:
                    print("--> No new popup tab opened; form submitted in current tab. Error:", e)

            if popup_page:
                target_render_page = popup_page
                await target_render_page.wait_for_load_state("networkidle")
                await target_render_page.wait_for_timeout(3000)
            else:
                target_render_page = page
                await target_render_page.wait_for_load_state("networkidle")
                await target_render_page.wait_for_timeout(3000)

            # Log target page text to verify course list is present
            target_text = await target_render_page.inner_text("body")
            print("\n--- RENDER TARGET PAGE CONTENT PREVIEW ---")
            print(target_text[:1500])

            # 6. Inject CSS and Render Exact A5 PDF
            print("\n6. Injecting CSS page rules for exact color printing and A5 paper format...")
            await target_render_page.add_style_tag(content="""
                @page {
                    size: A5 portrait;
                    margin: 4mm;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            """)

            print(f"7. Exporting exact webview DOM to A5 PDF: {pdf_full_path}")
            await target_render_page.pdf(
                path=pdf_full_path,
                format="A5",
                print_background=True,
                margin={"top": "4mm", "bottom": "4mm", "left": "4mm", "right": "4mm"}
            )

            print(f"\n=== SUCCESS! EXACT WEBVIEW A5 PDF RENDERED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Popup Solver Error:", err)
            return None

        finally:
            print("\n8. IMMEDIATELY LOGGING OUT to release session lock...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            print("Session context closed & released.")

if __name__ == "__main__":
    asyncio.run(run_popup_exam_card_solver(username="ENG/COE/21/013", password="olaleke"))
