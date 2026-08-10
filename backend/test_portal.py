import asyncio
from playwright.async_api import async_playwright

async def test_fuw_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("Navigating to FUW portal...")
        await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle", timeout=30000)

        title = await page.title()
        print(f"Page title: {title}")

        # Find login inputs
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} input fields")
        for inp in inputs:
            name = await inp.get_attribute("name")
            id_attr = await inp.get_attribute("id")
            type_attr = await inp.get_attribute("type")
            placeholder = await inp.get_attribute("placeholder")
            print(f"  Input: name={name}, id={id_attr}, type={type_attr}, placeholder={placeholder}")

        # Look for buttons or forms
        forms = await page.query_selector_all("form")
        print(f"Found {len(forms)} form elements")

        # Let's see all text content or login section
        body_text = await page.inner_text("body")
        print("Body preview (first 500 chars):")
        print(body_text[:500])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fuw_login())
