import os
import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger("portal_document_solver")

POSSIBLE_CHROME_BINS = [
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome",
    "/root/.cache/ms-playwright/chromium-1155/chrome-linux/chrome",
    "/home/user/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome",
]

def get_chrome_executable():
    for path in POSSIBLE_CHROME_BINS:
        if os.path.exists(path):
            return path
    return None

async def run_portal_document_solver(
    username: str,
    password: str,
    document_type: str = "exam", # exam, crg, rec, result
    paper_format: str = "A5",
    output_filename: str = None
) -> str:
    """
    Production-Grade Autonomous Portal Document Engine:
    - Pre-clears session lock.
    - Authenticates & asserts session handshake on main.php.
    - Navigates to requested document type.
    - Intercepts target webview (e.g. course_registration_printout.php / exam_card_printout.php).
    - Asserts that target URL is NOT index.php.
    - Measures scrollHeight & applies fit-to-page scale.
    - Exports pristine 1-page PDF.
    - Auto-logs out cleanly to prevent device lockout.
    """
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)

    safe_name = username.replace('/', '_')
    if not output_filename:
        output_filename = f"FUW_{document_type.upper()}_{safe_name}_{paper_format.upper()}.pdf"

    pdf_full_path = os.path.join(out_dir, output_filename)

    chrome_bin = get_chrome_executable()
    logger.info(f"=== PRODUCTION PORTAL SOLVER INITIALIZED ===")
    logger.info(f"User ID: {username} | Doc Type: {document_type} | Paper: {paper_format} | Output: {pdf_full_path}")
    if chrome_bin:
        logger.info(f"Using Chromium binary: {chrome_bin}")

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-http2",  # Prevent SNI 421 Misdirected Request errors
                "--ignore-certificate-errors"
            ]
        }
        if chrome_bin:
            launch_kwargs["executable_path"] = chrome_bin

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        try:
            # Step 1: Pre-clear session lock
            logger.info("1. Pre-clearing any stale session locks...")
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception as e:
                logger.debug(f"Pre-clear notice: {e}")

            # Step 2: Authentication Loop with Verification
            authenticated = False
            attempts = 0
            max_attempts = 3

            while not authenticated and attempts < max_attempts:
                attempts += 1
                logger.info(f"2. [Attempt {attempts}/{max_attempts}] Authenticating as {username}...")
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
                if "Logout" in body_text or "MAIN MENU" in body_text or "PERSONAL SETUP" in body_text:
                    logger.info("--> Authentication Successful!")
                    authenticated = True
                elif "logged in on another device" in body_text:
                    logger.warning("--> Session lock active on server. Executing logout clearance and waiting 3s...")
                    await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                    await page.wait_for_timeout(3000)

            if not authenticated:
                raise Exception(f"Failed to authenticate user {username} within attempt limit.")

            # Step 3: Mandatory main.php Session Handshake
            logger.info("3. Executing main.php session cookie handshake...")
            await page.goto("https://ug.fuwportal.edu.ng/main.php", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Step 4: Navigate to Document Service Page
            target_url = f"https://ug.fuwportal.edu.ng/print_course_form.php?id={document_type}&r_val=U3R1ZGVudA=="
            logger.info(f"4. Navigating to document service URL: {target_url}...")

            action_link = await page.query_selector(f"a[href*='id={document_type}']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # Step 5: Auto-Fill Session & Semester Dropdowns
            logger.info("5. Auto-filling session and semester dropdowns...")
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    logger.info(f"--> Auto-selected Session: '{opt_text}' ({first_val})")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    logger.info(f"--> Auto-selected Semester: '{opt_text}' ({first_val})")
                    await semester_select.select_option(first_val)

            # Step 6: Submit & Intercept Webview Popup Window
            logger.info("6. Submitting form and intercepting target webview...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                    logger.info(f"--> POPUP WEBVIEW INTERCEPTED! URL: {popup_page.url}")
                except Exception as e:
                    logger.info(f"--> No new popup tab opened, rendered in same window: {e}")

            target_page = popup_page if popup_page else page
            await target_page.wait_for_load_state("networkidle")
            await target_page.evaluate("document.fonts.ready")
            await target_page.wait_for_timeout(2500)

            # Step 7: Webview Target URL Assertion (NEVER PRINT LOGIN SCREEN)
            captured_url = target_page.url
            logger.info(f"7. Asserting Target Webview URL: {captured_url}")

            if "index.php" in captured_url:
                raise Exception("Target URL redirected to index.php (login screen). Capture rejected.")

            # Step 8: Measure DOM Height & Calculate Fit-to-Page Scale
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

            logger.info(f"--> DOM Height = {doc_height}px | Printable {paper_format} Height = {target_printable_height}px | Fit Scale = {fit_scale:.4f}")

            # Step 9: Inject Print Isolation CSS & Export PDF
            await target_page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 5mm;
                }}
                body {{
                    background: #ffffff !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    font-family: Arial, Helvetica, sans-serif !important;
                }}
                #header, #menu, .navbar, .header, #tawk-default-container, iframe, center > font {{
                    display: none !important;
                }}
                #contents {{
                    width: 100% !important;
                    margin: 0 auto !important;
                    padding: 0 !important;
                    float: none !important;
                }}
                table {{
                    width: 100% !important;
                    border-collapse: collapse !important;
                    margin-bottom: 6px !important;
                }}
                td, th {{
                    padding: 3px 5px !important;
                    font-size: 8pt !important;
                }}
                img[src*='pictures'] {{
                    width: 110px !important;
                    height: 110px !important;
                    object-fit: cover !important;
                    border: 1px solid #000 !important;
                }}
                * {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            """)

            logger.info(f"8. Exporting 1-Page {paper_format} PDF: {pdf_full_path}")
            await target_page.pdf(
                path=pdf_full_path,
                format=paper_format,
                scale=fit_scale,
                print_background=True,
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
            )

            logger.info(f"=== SUCCESS! EXPORTED {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            logger.error(f"Portal Document Solver Error: {err}")
            return None

        finally:
            logger.info("9. Executing immediate session logout clearance...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            logger.info("Session context closed and released.")

if __name__ == "__main__":
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else "ENG/COE/21/013"
    p = sys.argv[2] if len(sys.argv) > 2 else "olaleke"
    t = sys.argv[3] if len(sys.argv) > 3 else "crg"
    fmt = sys.argv[4] if len(sys.argv) > 4 else "A4"
    asyncio.run(run_portal_document_solver(u, p, t, fmt))
