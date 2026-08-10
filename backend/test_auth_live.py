import asyncio
from playwright.async_api import async_playwright

async def test_fuw_login_auth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("Navigating to FUW portal...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("Filling credentials...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        # Find login button
        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            btn_text = await login_btn.inner_text()
            print(f"Clicking button: {btn_text}")
            await login_btn.click()
        else:
            print("Pressing Enter on password input...")
            await page.press("#password", "Enter")

        # Wait for potential AJAX response / page load
        await page.wait_for_timeout(5000)

        # Check URL and page content
        current_url = page.url
        print(f"Current URL after login attempt: {current_url}")

        body_text = await page.inner_text("body")
        print("\n--- Response Body Preview (first 1000 chars) ---")
        print(body_text[:1000])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fuw_login_auth())
