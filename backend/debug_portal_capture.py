import os
import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def debug_capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Pre-clearing session...")
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

        # Confirm main.php
        await page.goto("https://ug.fuwportal.edu.ng/main.php", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Test A: Course Form (id=crg)
        print("\n=== TESTING COURSE FORM (id=crg) ===")
        await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=crg&r_val=U3R1ZGVudA==", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        session_select = await page.query_selector("select[name*='session'], select[id*='session']")
        if session_select:
            opts = await session_select.query_selector_all("option")
            print(f"Session options count: {len(opts)}")
            for o in opts:
                v = await o.get_attribute("value")
                t = (await o.inner_text()).strip()
                print(f"  Option val='{v}', text='{t}'")
            if len(opts) > 1:
                await session_select.select_option(await opts[1].get_attribute("value"))

        semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
        if semester_select:
            opts = await semester_select.query_selector_all("option")
            print(f"Semester options count: {len(opts)}")
            for o in opts:
                v = await o.get_attribute("value")
                t = (await o.inner_text()).strip()
                print(f"  Option val='{v}', text='{t}'")
            if len(opts) > 1:
                await semester_select.select_option(await opts[1].get_attribute("value"))

        submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

        popup_page = None
        if submit_btn:
            try:
                async with context.expect_page(timeout=8000) as popup_info:
                    await submit_btn.click()
                popup_page = await popup_info.value
            except Exception as e:
                print("No popup for crg:", e)

        target_crg = popup_page if popup_page else page
        await target_crg.wait_for_load_state("networkidle")
        await target_crg.wait_for_timeout(3000)

        print(f"Captured CRG Webview URL: {target_crg.url}")
        crg_text = await target_crg.inner_text("body")
        print("\n--- CRG TEXT PREVIEW ---")
        print(crg_text[:1500])

        await target_crg.screenshot(path="/home/user/docflow-automator/backend/debug_crg.png", full_page=True)
        crg_html = await target_crg.content()
        with open("/home/user/docflow-automator/backend/debug_crg.html", "w") as f:
            f.write(crg_html)

        # Cleanup & Logout
        try:
            await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
        except Exception:
            pass
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_capture())
