import os
import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def test_http1_fix():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-http2",  # Force HTTP 1.1 to prevent SNI Misdirected Request 421
                "--ignore-certificate-errors"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        try:
            print("1. Pre-clearing session lock...")
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

            print("2. Logging in as ENG/COE/21/013...")
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
                print("--> Session lock detected. Retrying with logout clearance...")
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
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

            print("--> Login Successful! Navigating to main.php...")
            await page.goto("https://ug.fuwportal.edu.ng/main.php", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            print("\n3. Navigating to print_course_form.php?id=crg&r_val=U3R1ZGVudA==...")
            await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=crg&r_val=U3R1ZGVudA==", wait_until="networkidle")
            await page.wait_for_timeout(3000)

            text = await page.inner_text("body")
            print("\n--- PAGE TEXT PREVIEW ---")
            print(text[:1500])

            # Auto-Fill Session & Semester
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                opts = await session_select.query_selector_all("option")
                print(f"\nFound {len(opts)} session options")
                if len(opts) > 1:
                    first_val = await opts[1].get_attribute("value")
                    opt_txt = (await opts[1].inner_text()).strip()
                    print(f"Selecting session: '{opt_txt}' ({first_val})")
                    await session_select.select_option(first_val)

            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                opts = await semester_select.query_selector_all("option")
                print(f"Found {len(opts)} semester options")
                if len(opts) > 1:
                    first_val = await opts[1].get_attribute("value")
                    opt_txt = (await opts[1].inner_text()).strip()
                    print(f"Selecting semester: '{opt_txt}' ({first_val})")
                    await semester_select.select_option(first_val)

            # Submit and intercept popup
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

            popup_page = None
            if submit_btn:
                print("Submitting form & intercepting popup...")
                try:
                    async with context.expect_page(timeout=8000) as popup_info:
                        await submit_btn.click()
                    popup_page = await popup_info.value
                except Exception as e:
                    print("No popup, rendered in same tab:", e)

            target_page = popup_page if popup_page else page
            await target_page.wait_for_load_state("networkidle")
            await target_page.wait_for_timeout(3000)

            print(f"\n4. Target Webview URL: {target_page.url}")
            target_text = await target_page.inner_text("body")
            print("\n--- TARGET WEBVIEW TEXT PREVIEW ---")
            print(target_text[:2000])

            # Render A4 PDF
            out_pdf = "/home/user/docflow-automator/storage/pdfs/FUW_CRG_HTTP1_FIX_A4.pdf"
            await target_page.pdf(path=out_pdf, format="A4", print_background=True)
            print(f"\nSaved A4 PDF: {out_pdf}")

        finally:
            try:
                await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
            except Exception:
                pass
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_http1_fix())
