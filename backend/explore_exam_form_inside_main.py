import asyncio
from playwright.async_api import async_playwright

async def explore_inside_main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Opening FUW portal index.php...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("2. Entering credentials for ENG/COE/21/013...")
        await page.fill("#userId", "ENG/COE/21/013")
        await page.fill("#password", "olaleke")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)
        print(f"Logged in page URL: {page.url}")

        # Check if we are on main.php or index.php
        body_text = await page.inner_text("body")
        print("Page Body Text preview:")
        print(body_text[:500])

        if "logged in on another device" in body_text:
            print("Session lock detected. Waiting 3 seconds and retrying...")
            await page.wait_for_timeout(3000)

        # On main.php, click 'Print Exam Card'
        print("\n3. Locating 'Print Exam Card' link on main.php...")
        exam_link = await page.query_selector("a[href*='id=exam']")
        if not exam_link:
            exam_link = await page.query_selector("a:has-text('Exam Card')")

        if exam_link:
            print("Clicking Exam Card link...")
            await exam_link.click()
            await page.wait_for_timeout(4000)

            print(f"URL after click: {page.url}")

            # Inspect all forms, selects, options, inputs on the Exam Card page
            forms = await page.query_selector_all("form")
            print(f"\nForms found: {len(forms)}")

            selects = await page.query_selector_all("select")
            print(f"\nSelect dropdowns found: {len(selects)}")
            for sel in selects:
                name = await sel.get_attribute("name")
                id_attr = await sel.get_attribute("id")
                options = await sel.query_selector_all("option")
                print(f"  Select name='{name}', id='{id_attr}' (Options count: {len(options)}):")
                for opt in options:
                    val = await opt.get_attribute("value")
                    opt_text = (await opt.inner_text()).strip()
                    print(f"    Option val='{val}', text='{opt_text}'")

            # Check buttons / inputs
            inputs = await page.query_selector_all("input, button, a.btn")
            print(f"\nInteractive inputs found: {len(inputs)}")
            for inp in inputs:
                t = await inp.get_attribute("type")
                n = await inp.get_attribute("name")
                v = await inp.get_attribute("value")
                txt = (await inp.inner_text()).strip()
                print(f"  Element type={t}, name={n}, value={v}, text={txt}")

            # Dump page content
            content = await page.content()
            with open("/home/user/docflow-automator/backend/exam_form_inside_page.html", "w") as f:
                f.write(content)

        else:
            print("Exam card link not found on page.")

        # Always logout
        try:
            await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
        except Exception:
            pass

        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_inside_main())
