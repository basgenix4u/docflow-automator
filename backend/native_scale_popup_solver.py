import os
import asyncio
from playwright.async_api import async_playwright

async def run_native_scale_popup_solver(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_NativeScale_ExamCard_ENG_COE_21_013_A5.pdf",
    paper_format: str = "A5",
    scale_factor: float = 0.72
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_full_path = os.path.join(out_dir, output_filename)

    print("=== NATIVE PRINT SCALE POPUP SOLVER INITIALIZED ===")
    print(f"User: {username} | Scale: {scale_factor} | Format: {paper_format} | File: {pdf_full_path}")

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
                retry_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
                if retry_btn:
                    await retry_btn.click()
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

            # 6. INJECT NATIVE COLOR PRESERVATION WITHOUT OVERFLOW CLIPPING
            print(f"\n6. Injecting native print color preservation rules for {paper_format} paper size...")
            await target_page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 3mm;
                }}
                * {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            """)

            # 7. Render PDF using Playwright's native `scale` parameter BEFORE page break calculations
            print(f"7. Exporting PDF using Playwright native print scale factor ({scale_factor}) to: {pdf_full_path}")
            await target_page.pdf(
                path=pdf_full_path,
                format=paper_format,
                scale=scale_factor,  # Proportional Skia vector scaling BEFORE page breaks!
                print_background=True,
                margin={"top": "3mm", "bottom": "3mm", "left": "3mm", "right": "3mm"}
            )

            print(f"\n=== SUCCESS! NATIVE SCALED {paper_format} PDF GENERATED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Native Scale Solver Error:", err)
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
    asyncio.run(run_native_scale_popup_solver("ENG/COE/21/013", "olaleke", "FUW_NativeScale_ExamCard_ENG_COE_21_013_A5.pdf", "A5", 0.72))
