import asyncio
from playwright.async_api import async_playwright

async def inspect_popup_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Logging in as ENG/COE/21/013...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        try:
            await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
            await page.wait_for_timeout(1000)
            await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
        except Exception:
            pass

        await page.fill("#userId", "ENG/COE/21/013")
        await page.fill("#password", "olaleke")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)

        print("2. Navigating to print_course_form.php?id=exam&r_val=U3R1ZGVudA==")
        action_link = await page.query_selector("a[href*='id=exam']")
        if action_link:
            await page.evaluate("el => el.click()", action_link)
            await page.wait_for_timeout(3000)
        else:
            await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
            await page.wait_for_timeout(3000)

        # Select Session & Semester
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

        submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")

        popup_page = None
        if submit_btn:
            async with context.expect_page(timeout=8000) as popup_info:
                await submit_btn.click()
            popup_page = await popup_info.value

        target_page = popup_page if popup_page else page
        await target_page.wait_for_load_state("networkidle")
        await target_page.wait_for_timeout(3000)

        # Capture raw screenshot of popup page
        await target_page.screenshot(path="/home/user/docflow-automator/backend/popup_exam_card_raw.png", full_page=True)
        print("Saved raw PNG screenshot: /home/user/docflow-automator/backend/popup_exam_card_raw.png")

        # Capture raw HTML
        raw_html = await target_page.content()
        with open("/home/user/docflow-automator/backend/popup_exam_card_raw.html", "w") as f:
            f.write(raw_html)
        print("Saved raw HTML: /home/user/docflow-automator/backend/popup_exam_card_raw.html")

        # Cleanup
        try:
            await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
        except Exception:
            pass
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_popup_html())
