import asyncio
from playwright.async_api import async_playwright

async def inspect_exam_form_fields():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Logging in as ENG/COE/21/013...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        # Clear session first to be safe
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

        print("2. Navigating to print_course_form.php?id=exam&r_val=U3R1ZGVudA==...")
        await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        print(f"Current URL: {page.url}")

        # Check all form elements
        forms = await page.query_selector_all("form")
        print(f"\nFound {len(forms)} forms on Exam Card page:")
        for idx, form in enumerate(forms, 1):
            action = await form.get_attribute("action")
            method = await form.get_attribute("method")
            id_attr = await form.get_attribute("id")
            print(f"  Form {idx}: action={action}, method={method}, id={id_attr}")

        # Check all select dropdowns
        selects = await page.query_selector_all("select")
        print(f"\nFound {len(selects)} select dropdowns:")
        for sel in selects:
            name = await sel.get_attribute("name")
            id_attr = await sel.get_attribute("id")
            options = await sel.query_selector_all("option")
            print(f"  Select name='{name}', id='{id_attr}' (Options count: {len(options)}):")
            for opt in options:
                val = await opt.get_attribute("value")
                opt_text = (await opt.inner_text()).strip()
                print(f"    Option val='{val}', text='{opt_text}'")

        # Check all submit / button inputs
        inputs = await page.query_selector_all("input, button, a.btn")
        print(f"\nFound {len(inputs)} interactive input/button elements:")
        for inp in inputs:
            type_attr = await inp.get_attribute("type")
            name_attr = await inp.get_attribute("name")
            val_attr = await inp.get_attribute("value")
            text_attr = (await inp.inner_text()).strip()
            print(f"  Element: type={type_attr}, name={name_attr}, value={val_attr}, text={text_attr}")

        await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_exam_form_fields())
