import os
import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def run_portal_document_solver(
    username: str,
    password: str,
    document_type: str = "exam", # exam, crg, rec, result
    paper_format: str = "A5",
    output_filename: str = None
) -> str:
    """
    Dynamic Autonomous Portal Document Engine:
    - Log in with any student credentials.
    - Navigate to requested document type (Exam Card, Course Form, Receipt, Results).
    - Auto-fill session and semester dropdowns.
    - Intercept popup webview.
    - Apply fit-to-page scaling & print color preservation.
    - Output exact 1-page PDF.
    - Execute auto-logout clearance.
    """
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)

    safe_name = username.replace('/', '_')
    if not output_filename:
        output_filename = f"FUW_{document_type.upper()}_{safe_name}_{paper_format.upper()}.pdf"

    pdf_full_path = os.path.join(out_dir, output_filename)

    print(f"=== PORTAL DOCUMENT SOLVER INITIALIZED ===")
    print(f"User ID: {username} | Doc Type: {document_type} | Paper: {paper_format} | Output: {pdf_full_path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
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
            print(f"1. Authenticating as {username}...")
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

            print("--> Login Successful! Navigating to main.php...")
            await page.goto("https://ug.fuwportal.edu.ng/main.php", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # 3. Navigate to requested document service URL
            target_url = f"https://ug.fuwportal.edu.ng/print_course_form.php?id={document_type}&r_val=U3R1ZGVudA=="
            print(f"2. Navigating to document service URL: {target_url}...")

            action_link = await page.query_selector(f"a[href*='id={document_type}']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # 4. Auto-Fill Session & Semester Dropdowns
            print("3. Auto-filling session and semester dropdowns if present...")
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
            print("4. Submitting form & intercepting popup webview...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                    print(f"--> POPUP WEBVIEW CAPTURED! URL: {popup_page.url}")
                except Exception as e:
                    print("--> Rendered in current tab:", e)

            target_page = popup_page if popup_page else page

            # 6. Wait for JS / Images / Fonts to finish
            print("5. Waiting for JS / Images / Fonts to finish loading...")
            await target_page.wait_for_load_state("networkidle")
            await target_page.evaluate("document.fonts.ready")
            await target_page.wait_for_timeout(2000)

            # 7. Measure document height & Calculate Fit-to-Page Scale
            dims = await target_page.evaluate("""() => {
                const body = document.body;
                const html = document.documentElement;
                const height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
                const width = Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth);
                return { width, height };
            }""")
            doc_height = dims["height"]

            target_printable_height = 1075.0 if paper_format.upper() == "A4" else 755.0
            fit_scale = target_printable_height / doc_height
            fit_scale = max(0.40, min(1.0, fit_scale))

            print(f"6. DOM Height = {doc_height}px | Printable {paper_format} Height = {target_printable_height}px | Calculated Fit Scale = {fit_scale:.4f}")

            # 8. Inject Print Isolation & Color Preservation CSS
            await target_page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 4mm;
                }}
                body {{
                    background: #ffffff !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                #header, #menu, .navbar, .header, #tawk-default-container, iframe {{
                    display: none !important;
                }}
                #contents {{
                    width: 100% !important;
                    margin: 0 auto !important;
                    padding: 0 !important;
                    float: none !important;
                }}
                * {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            """)

            # 9. Render 1-Page PDF
            print(f"7. Exporting 1-Page {paper_format} PDF: {pdf_full_path}")
            await target_page.pdf(
                path=pdf_full_path,
                format=paper_format,
                scale=fit_scale,
                print_background=True,
                margin={"top": "4mm", "bottom": "4mm", "left": "4mm", "right": "4mm"}
            )

            print(f"=== SUCCESS! EXPORTED {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            print("Portal Document Solver Error:", err)
            return None

        finally:
            print("8. Executing immediate session logout clearance...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            print("Session context closed and released.")

if __name__ == "__main__":
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else "ENG/COE/21/013"
    p = sys.argv[2] if len(sys.argv) > 2 else "olaleke"
    t = sys.argv[3] if len(sys.argv) > 3 else "exam"
    fmt = sys.argv[4] if len(sys.argv) > 4 else "A5"
    asyncio.run(run_portal_document_solver(u, p, t, fmt))
