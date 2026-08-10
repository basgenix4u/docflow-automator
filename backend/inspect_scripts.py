import asyncio
from playwright.async_api import async_playwright

async def inspect_swapcontent():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

        scripts = await page.query_selector_all("script")
        print(f"Found {len(scripts)} scripts on index.php")
        for i, script in enumerate(scripts):
            content = await script.inner_text()
            if "swapcontent" in content or "scriptfile" in content or "login" in content:
                print(f"\n--- Script {i} ---")
                print(content[:1500])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_swapcontent())
