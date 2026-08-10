import asyncio
from playwright.async_api import async_playwright

async def login_and_fetch_exam_card():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        print("Navigating to index.php...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("Entering credentials...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)

        body_text = await page.inner_text("body")
        print("Page preview after login:")
        print(body_text[:800])

        if "IBRAHIM" in body_text or "MAIN MENU" in body_text:
            print("\nSUCCESSFULLY LOGGED IN! Searching for Exam Card link...")

            # Find Print Exam Card link
            exam_card_link = await page.query_selector("a:has-text('Exam Card')")
            if not exam_card_link:
                exam_card_link = await page.query_selector("a[href*='id=exam']")

            if exam_card_link:
                href = await exam_card_link.get_attribute("href")
                print(f"Found Exam Card link: href={href}")
                await exam_link_click(page, exam_card_link)
            else:
                print("Exam Card link not found in DOM directly, trying navigation to print_course_form.php?id=exam&r_val=U3R1ZGVudA==")
                await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
                await page.wait_for_timeout(3000)
                await dump_exam_card_page(page)

        elif "logged in on another device" in body_text:
            print("Session lock active. Retrying with session clearance...")

        await browser.close()

async def exam_link_click(page, link):
    await link.click()
    await page.wait_for_timeout(4000)
    await dump_exam_card_page(page)

async def dump_exam_card_page(page):
    print(f"\n--- EXAM CARD PAGE CONTENT (URL: {page.url}) ---")
    text = await page.inner_text("body")
    print(text[:2500])

    # Check for select dropdowns or forms
    selects = await page.query_selector_all("select")
    print(f"\nSelect elements found: {len(selects)}")
    for sel in selects:
        name = await sel.get_attribute("name")
        print(f"  Select name={name}")
        opts = await sel.query_selector_all("option")
        for opt in opts:
            val = await opt.get_attribute("value")
            t = (await opt.inner_text()).strip()
            print(f"    Option val='{val}', text='{t}'")

    # Capture PDF
    await page.pdf(path="/home/user/docflow-automator/backend/fuw_exam_card_official.pdf", format="A4", print_background=True)
    print("\nOfficial FUW Exam Card saved as /home/user/docflow-automator/backend/fuw_exam_card_official.pdf")

if __name__ == "__main__":
    asyncio.run(login_and_fetch_exam_card())
