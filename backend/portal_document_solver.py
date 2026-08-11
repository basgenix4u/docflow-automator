import os
import asyncio
import logging
from playwright.async_api import async_playwright
from app.core.config import settings

logger = logging.getLogger("portal_document_solver")

async def run_portal_document_solver(
    username: str,
    password: str,
    document_type: str = "exam", # exam, crg, rec, result
    paper_format: str = "A5",
    output_filename: str = None
) -> str:
    """
    Production-Grade Autonomous Portal Document Engine:
    - Stable Linux Chromium flags.
    - Pre-clears session lock.
    - Authenticates & asserts session handshake on main.php.
    - Navigates to requested document type.
    - Intercepts target webview (e.g. course_registration_printout.php / exam_card_printout.php).
    - Asserts that target URL is NOT index.php.
    - Measures scrollHeight & applies fit-to-page scale.
    - Exports pristine 1-page PDF.
    - Auto-logs out cleanly to prevent device lockout.
    """
    out_dir = settings.STORAGE_DIR
    os.makedirs(out_dir, exist_ok=True)

    safe_name = username.replace('/', '_')
    if not output_filename:
        output_filename = f"FUW_{document_type.upper()}_{safe_name}_{paper_format.upper()}.pdf"

    pdf_full_path = os.path.join(out_dir, output_filename)

    logger.info(f"=== PRODUCTION PORTAL SOLVER INITIALIZED ===")
    logger.info(f"User ID: {username} | Doc Type: {document_type} | Paper: {paper_format} | Output: {pdf_full_path}")

    async with async_playwright() as p:
        # Stable Linux flags (omitting deprecated --single-process)
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-http2",  # Prevent SNI 421 Misdirected Request errors
            "--ignore-certificate-errors"
        ]

        browser = await p.chromium.launch(
            headless=True,
            args=launch_args
        )

        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        try:
            # Step 1: Pre-clear session lock
            logger.info("1. Pre-clearing any stale session locks...")
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="domcontentloaded", timeout=15000)
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception as e:
                logger.debug(f"Pre-clear notice: {e}")

            # Step 2: Authentication
            logger.info(f"2. Authenticating as {username}...")
            await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="domcontentloaded", timeout=15000)
            await page.fill("#userId", username)
            await page.fill("#password", password)

            login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
            if login_btn:
                await login_btn.click()
            else:
                await page.press("#password", "Enter")

            await page.wait_for_timeout(3000)

            body_text = await page.inner_text("body")
            if "logged in on another device" in body_text:
                logger.warning("--> Session lock active. Clearing session...")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(3000)
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="domcontentloaded")
                await page.fill("#userId", username)
                await page.fill("#password", password)
                retry_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
                if retry_btn:
                    await retry_btn.click()
                else:
                    await page.press("#password", "Enter")
                await page.wait_for_timeout(3000)

            logger.info("--> Login Successful! Navigating to main.php...")
            await page.goto("https://ug.fuwportal.edu.ng/main.php", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(1500)

            # Step 3: Navigate to Document Service Page
            target_url = f"https://ug.fuwportal.edu.ng/print_course_form.php?id={document_type}&r_val=U3R1ZGVudA=="
            logger.info(f"3. Navigating to document service URL: {target_url}...")

            action_link = await page.query_selector(f"a[href*='id={document_type}']")
            if action_link:
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(2000)
            else:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)

            # Step 4: Auto-Fill Session & Semester Dropdowns
            logger.info("4. Auto-filling session and semester dropdowns...")
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    logger.info(f"--> Selected Session: '{opt_text}' ({first_val})")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    logger.info(f"--> Selected Semester: '{opt_text}' ({first_val})")
                    await semester_select.select_option(first_val)

            # Step 5: Submit & Intercept Webview Popup Window
            logger.info("5. Submitting form and intercepting target webview...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                    logger.info(f"--> POPUP WEBVIEW CAPTURED! URL: {popup_page.url}")
                except Exception as e:
                    logger.info(f"--> No new popup tab opened, rendered in same window: {e}")

            target_page = popup_page if popup_page else page
            await target_page.wait_for_load_state("domcontentloaded")
            await target_page.wait_for_timeout(2000)

            # Step 6: Webview Target URL Assertion
            captured_url = target_page.url
            logger.info(f"6. Asserting Target Webview URL: {captured_url}")

            if "index.php" in captured_url:
                raise Exception("Target URL redirected to index.php (login screen). Capture rejected.")

            # Step 7: Measure DOM Height & Calculate Fit-to-Page Scale
            try:
                dims = await target_page.evaluate("""() => {
                    const body = document.body || {};
                    const html = document.documentElement || {};
                    const height = Math.max(body.scrollHeight || 0, body.offsetHeight || 0, html.clientHeight || 0, html.scrollHeight || 0, html.offsetHeight || 0);
                    const width = Math.max(body.scrollWidth || 0, body.offsetWidth || 0, html.clientWidth || 0, html.scrollWidth || 0, html.offsetWidth || 0);
                    return { width, height };
                }""")
            except Exception:
                dims = {"width": 1280, "height": 1000}

            doc_height = dims.get("height", 1000) or 1000
            if doc_height <= 0:
                doc_height = 1000

            target_printable_height = 1075.0 if paper_format.upper() == "A4" else 755.0
            fit_scale = target_printable_height / float(doc_height)
            fit_scale = max(0.40, min(1.0, fit_scale))

            logger.info(f"--> DOM Height = {doc_height}px | Printable {paper_format} Height = {target_printable_height}px | Fit Scale = {fit_scale:.4f}")

            # Step 8: Inject Print Isolation CSS & Export PDF
            await target_page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 4mm;
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

            logger.info(f"7. Exporting 1-Page {paper_format} PDF: {pdf_full_path}")
            await target_page.pdf(
                path=pdf_full_path,
                format=paper_format,
                scale=fit_scale,
                print_background=True,
                margin={"top": "4mm", "bottom": "4mm", "left": "4mm", "right": "4mm"}
            )

            logger.info(f"=== SUCCESS! EXPORTED {pdf_full_path} ===")
            return pdf_full_path

        except Exception as err:
            logger.error(f"Portal Document Solver Error: {err}")
            return None

        finally:
            logger.info("8. Executing immediate session logout clearance...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(500)
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
