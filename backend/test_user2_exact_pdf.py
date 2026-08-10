import asyncio
from playwright.async_api import async_playwright

async def render_exact_portal_pdf():
    async with async_playwright() as p:
        # Launch browser with custom viewport for A5 ratio or standard web
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Opening FUW portal index.php...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("2. Entering credentials for ENG/COE/21/013...")
        await page.fill("#userId", "ENG/COE/21/013")
        await page.fill("#password", "olaleke")

        # Click login button
        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            print("Clicking login button...")
            await login_btn.click()
        else:
            print("Pressing enter on password field...")
            await page.press("#password", "Enter")

        # Wait 5 seconds for login response / redirection / AJAX content load
        await page.wait_for_timeout(5000)

        current_url = page.url
        print(f"Current URL after login attempt: {current_url}")

        body_text = await page.inner_text("body")
        print("\n--- BODY TEXT AFTER LOGIN ---")
        print(body_text[:1200])

        # If redirected to main.php or logged in
        if "Logout" in body_text or "MAIN MENU" in body_text or "main.php" in current_url:
            print("\nSUCCESSFULLY LOGGED IN! Capturing exact dashboard PDF in A5...")

            # Render EXACT dashboard page to A5 PDF
            await page.pdf(
                path="/home/user/docflow-automator/storage/pdfs/FUW_Dashboard_ENG_COE_21_013_A5.pdf",
                format="A5",
                print_background=True,
                margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
            )
            print("Saved exact dashboard A5 PDF: /home/user/docflow-automator/storage/pdfs/FUW_Dashboard_ENG_COE_21_013_A5.pdf")

            # Look for Print Exam Card link or click it directly
            exam_link = await page.query_selector("a:has-text('Exam Card')")
            if not exam_link:
                exam_link = await page.query_selector("a[href*='id=exam']")

            if exam_link:
                href = await exam_link.get_attribute("href")
                print(f"\nFound Exam Card link: {href}. Clicking...")
                await exam_link.click()
                await page.wait_for_timeout(5000)

                print(f"Exam Card page URL: {page.url}")
                exam_text = await page.inner_text("body")
                print("\n--- EXAM CARD PAGE TEXT ---")
                print(exam_text[:1500])

                # Render EXACT Exam Card page directly as A5 PDF
                await page.pdf(
                    path="/home/user/docflow-automator/storage/pdfs/FUW_ExamCard_ENG_COE_21_013_A5.pdf",
                    format="A5",
                    print_background=True,
                    margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
                )
                print("Saved exact Exam Card A5 PDF: /home/user/docflow-automator/storage/pdfs/FUW_ExamCard_ENG_COE_21_013_A5.pdf")

            else:
                print("Exam card link not found on main menu.")

        elif "logged in on another device" in body_text:
            print("\nSession lock detected on ENG/COE/21/013.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(render_exact_portal_pdf())
