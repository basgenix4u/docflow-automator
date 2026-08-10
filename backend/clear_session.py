import asyncio
from playwright.async_api import async_playwright

async def clear_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        print("Navigating to index.php...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        # Call logout script or swapcontent2 if defined
        print("Attempting to call logout script...")
        try:
            await page.evaluate("if (typeof swapcontent2 === 'function') swapcontent2('logout','index.php');")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print("Evaluate logout error:", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(clear_session())
