import asyncio
from playwright.async_api import async_playwright

async def fetch_exam_card():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        print("1. Navigating to FUW portal...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("2. Logging in as BSC/BCH/24/140...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)
        print(f"Current URL: {page.url}")

        print("3. Navigating to 'Print Exam Card' page...")
        await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        exam_card_url = page.url
        print(f"Exam Card Page URL: {exam_card_url}")

        body_html = await page.content()
        body_text = await page.inner_text("body")

        print("\n--- EXAM CARD PAGE TEXT PREVIEW ---")
        print(body_text[:1500])

        # Check if there's a print button or select form or table
        forms = await page.query_selector_all("form")
        print(f"\nFound {len(forms)} forms on Exam Card page")

        selects = await page.query_selector_all("select")
        print(f"Found {len(selects)} select dropdowns:")
        for sel in selects:
            name = await sel.get_attribute("name")
            id_attr = await sel.get_attribute("id")
            options = await sel.query_selector_all("option")
            print(f"  Select name={name}, id={id_attr}, options_count={len(options)}")
            for opt in options:
                val = await opt.get_attribute("value")
                opt_text = (await opt.inner_text()).strip()
                print(f"    Option value='{val}', text='{opt_text}'")

        # Save HTML for inspection
        with open("/home/user/docflow-automator/backend/exam_card_page.html", "w") as f:
            f.write(body_html)

        # Print PDF of current view
        await page.pdf(path="/home/user/docflow-automator/backend/exam_card_direct.pdf", format="A4", print_background=True)
        print("\nSaved exam_card_direct.pdf")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_exam_card())
