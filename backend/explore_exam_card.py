import asyncio
from playwright.async_api import async_playwright

async def explore_exam_card():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        print("Navigating to FUW portal...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        print("Logging in with demo user BSC/BCH/24/140...")
        await page.fill("#userId", "BSC/BCH/24/140")
        await page.fill("#password", "Omotola")

        login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
        if login_btn:
            await login_btn.click()
        else:
            await page.press("#password", "Enter")

        await page.wait_for_timeout(4000)
        print(f"Logged in URL: {page.url}")

        # Find all links on main.php
        links = await page.query_selector_all("a")
        print(f"Found {len(links)} links on main page:")
        for link in links:
            text = (await link.inner_text()).strip()
            href = await link.get_attribute("href")
            onclick = await link.get_attribute("onclick")
            if text:
                print(f"  Link text: '{text}' | href={href} | onclick={onclick}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_exam_card())
