import asyncio
from playwright.async_api import async_playwright

async def click_exam_card_link():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        print("1. Navigating to FUW portal...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("2. Logging in as BSC/BCH/24/140...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        # Click login button
        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)
        print(f"Logged in URL: {page.url}")

        print("3. Clicking 'Print Exam Card' link...")
        # Find link with text 'Print Exam Card'
        exam_link = await page.query_selector("a:has-text('Print Exam Card')")
        if not exam_link:
            exam_link = await page.query_selector("a[href*='id=exam']")

        if exam_link:
            href = await exam_link.get_attribute("href")
            print(f"Found exam card link: href={href}")
            await exam_link.click()
            await page.wait_for_timeout(5000)
            print(f"URL after clicking: {page.url}")

            body_text = await page.inner_text("body")
            print("\n--- EXAM CARD CONTENT PREVIEW ---")
            print(body_text[:2000])

            # Check for select dropdowns, tables, or iframe/form
            selects = await page.query_selector_all("select")
            print(f"\nSelect dropdowns found: {len(selects)}")
            for sel in selects:
                name = await sel.get_attribute("name")
                id_attr = await sel.get_attribute("id")
                options = await sel.query_selector_all("option")
                print(f"  Select name={name}, id={id_attr}:")
                for opt in options:
                    val = await opt.get_attribute("value")
                    opt_text = (await opt.inner_text()).strip()
                    print(f"    Option val='{val}', text='{opt_text}'")

            # Save HTML
            content = await page.content()
            with open("/home/user/docflow-automator/backend/exam_card_clicked.html", "w") as f:
                f.write(content)

            # Generate PDF
            await page.pdf(path="/home/user/docflow-automator/backend/exam_card_live.pdf", format="A4", print_background=True)
            print("Saved exam_card_live.pdf")

        else:
            print("Could not find 'Print Exam Card' link on page!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_exam_card_link())
