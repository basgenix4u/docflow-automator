import os
import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def run_vercel_examcard_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("1. Opening live Vercel web app: https://docflow-automator-tau.vercel.app/ ...")
        await page.goto("https://docflow-automator-tau.vercel.app/", wait_until="networkidle", timeout=30000)

        print("\n2. Entering student demo credentials for ENG/COE/21/013...")
        user_input = await page.query_selector("input[placeholder*='ENG/COE']")
        pass_input = await page.query_selector("input[type='password']")

        if user_input and pass_input:
            await user_input.fill("ENG/COE/21/013")
            await pass_input.fill("olaleke")
            print("--> Credentials filled: ENG/COE/21/013 / olaleke")

            # Click Generate & Auto-Open PDF button
            gen_btn = await page.query_selector("button:has-text('Generate')")
            if gen_btn:
                print("\n3. Clicking 'Generate & Auto-Open PDF' button on Vercel app...")

                popup_page = None
                try:
                    async with context.expect_page(timeout=35000) as popup_info:
                        await gen_btn.click()
                    popup_page = await popup_info.value
                    print(f"\n--> SUCCESS! POPUP PDF TAB OPENED: {popup_page.url}")
                except Exception as e:
                    print("--> Click executed; checking page state / API response:", e)

                await page.wait_for_timeout(6000)

                body_text = await page.inner_text("body")
                print("\n--- VERCEL PAGE TEXT AFTER GENERATION ---")
                print(body_text[:1200])

        else:
            print("Could not find input fields on Vercel app!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_vercel_examcard_test())
