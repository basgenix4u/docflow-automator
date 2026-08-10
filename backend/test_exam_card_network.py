import asyncio
from playwright.async_api import async_playwright

async def run_network_trace():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        # Monitor response status
        page.on("response", lambda response: print(f"  [NETWORK] {response.status} {response.url}"))

        print("1. Opening index.php...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("\n2. Submitting login credentials...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(5000)

        body_text = await page.inner_text("body")
        print("\n--- BODY TEXT AFTER LOGIN ---")
        print(body_text[:1000])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_network_trace())
