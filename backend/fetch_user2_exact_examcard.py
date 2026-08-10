import asyncio
from playwright.async_api import async_playwright

async def fetch_exact_user2_exam_card():
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

        # Confirm logged in
        body_text = await page.inner_text("body")
        print(f"Logged in page text header: {body_text[:200]}")

        # Save exact Dashboard A5 PDF
        dash_pdf = "/home/user/docflow-automator/storage/pdfs/FUW_Dashboard_ENG_COE_21_013_A5.pdf"
        await page.pdf(
            path=dash_pdf,
            format="A5",
            print_background=True,
            margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
        )
        print(f"Saved exact Dashboard A5 PDF: {dash_pdf}")

        # Navigate directly to print_course_form.php?id=exam&r_val=U3R1ZGVudA==
        print("3. Opening Exam Card page: print_course_form.php?id=exam&r_val=U3R1ZGVudA==...")
        await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        exam_url = page.url
        print(f"Exam Card Page URL: {exam_url}")

        exam_text = await page.inner_text("body")
        print("\n--- EXAM CARD PAGE TEXT PREVIEW ---")
        print(exam_text[:1500])

        # Render EXACT Exam Card page directly as A5 PDF
        exam_pdf = "/home/user/docflow-automator/storage/pdfs/FUW_ExamCard_ENG_COE_21_013_A5.pdf"
        await page.pdf(
            path=exam_pdf,
            format="A5",
            print_background=True,
            margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
        )
        print(f"Saved exact Exam Card A5 PDF: {exam_pdf}")

        # Also let's check Course Registration / Print Course Form page: print_course_form.php?id=crg&r_val=U3R1ZGVudA==
        print("\n4. Opening Course Form page: print_course_form.php?id=crg&r_val=U3R1ZGVudA==...")
        await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=crg&r_val=U3R1ZGVudA==", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        crg_text = await page.inner_text("body")
        print("\n--- COURSE FORM PAGE TEXT PREVIEW ---")
        print(crg_text[:1500])

        crg_pdf = "/home/user/docflow-automator/storage/pdfs/FUW_CourseForm_ENG_COE_21_013_A5.pdf"
        await page.pdf(
            path=crg_pdf,
            format="A5",
            print_background=True,
            margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
        )
        print(f"Saved exact Course Form A5 PDF: {crg_pdf}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_exact_user2_exam_card())
