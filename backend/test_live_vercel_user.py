import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def test_live_vercel_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        # Track network requests
        page.on("request", lambda request: print(f"  [REQ] {request.method} {request.url}"))
        page.on("response", lambda response: print(f"  [RES {response.status}] {response.url}"))

        print("1. Opening live Vercel application: https://docflow-automator-tau.vercel.app/ ...")
        await page.goto("https://docflow-automator-tau.vercel.app/", wait_until="networkidle", timeout=30000)

        title = await page.title()
        print(f"--> Live Vercel Page Title: '{title}'")

        body_text = await page.inner_text("body")
        print("\n--- VERCEL PAGE TEXT PREVIEW ---")
        print(body_text[:800])

        print("\n2. Filling student credentials into dynamic input fields...")
        # Fill User ID and Password
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} input fields on Vercel app")

        user_input = await page.query_selector("input[placeholder*='ENG/COE']")
        pass_input = await page.query_selector("input[type='password']")

        if user_input and pass_input:
            await user_input.fill("ENG/COE/21/013")
            await pass_input.fill("olaleke")
            print("--> Filled credentials: ENG/COE/21/013 / olaleke")

            # Click Generate & Auto-Open PDF button
            gen_btn = await page.query_selector("button:has-text('Generate')")
            if gen_btn:
                print("\n3. Clicking 'Generate & Export Document' button on Vercel app...")

                popup_page = None
                try:
                    async with context.expect_page(timeout=15000) as popup_info:
                        await gen_btn.click()
                    popup_page = await popup_info.value
                    print(f"--> AUTO-OPENED PDF TAB DETECTED! URL: {popup_page.url}")
                except Exception as e:
                    print("--> Click executed; checking page state / API response:", e)

                await page.wait_for_timeout(6000)

                after_text = await page.inner_text("body")
                print("\n--- VERCEL PAGE TEXT AFTER GENERATION ---")
                print(after_text[:1200])

        else:
            print("Could not find credential input fields on Vercel app!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_live_vercel_e2e())
