import os
import asyncio
from playwright.async_api import async_playwright

CHROME_BIN = "/home/user/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"

async def test_live_vercel_proof():
    proof_pdf = "/home/user/docflow-automator/storage/pdfs/FUW_LIVE_VERCEL_PROOF_ENG_COE_21_013_A5.pdf"
    os.makedirs(os.path.dirname(proof_pdf), exist_ok=True)

    print("=== LIVE VERCEL E2E AUTOMATION TEST INITIALIZED ===")
    print("Target Vercel App: https://docflow-automator-tau.vercel.app/")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        page.on("request", lambda req: print(f"  [REQ] {req.method} {req.url}"))
        page.on("response", lambda res: print(f"  [RES {res.status}] {res.url}"))

        print("\n1. Navigating to live Vercel web app...")
        await page.goto("https://docflow-automator-tau.vercel.app/", wait_until="networkidle", timeout=30000)

        print("\n2. Entering student demo credentials on Vercel UI...")
        user_input = await page.query_selector("input[placeholder*='ENG/COE']")
        pass_input = await page.query_selector("input[type='password']")

        if user_input and pass_input:
            await user_input.fill("ENG/COE/21/013")
            await pass_input.fill("olaleke")
            print("--> User ID = ENG/COE/21/013 | Passcode = olaleke")

            gen_btn = await page.query_selector("button:has-text('Generate')")
            if gen_btn:
                print("\n3. Clicking 'Generate & Auto-Open PDF' button...")

                popup_page = None
                try:
                    async with context.expect_page(timeout=45000) as popup_info:
                        await gen_btn.click()
                    popup_page = await popup_info.value
                    print(f"\n--> SUCCESS! POPUP PDF TAB OPENED: {popup_page.url}")
                except Exception as e:
                    print("--> Click executed; checking page state / API response:", e)

                await page.wait_for_timeout(6000)

                # Check if generated PDF card is visible on Vercel UI
                view_link = await page.query_selector("a:has-text('View PDF')")
                download_link = await page.query_selector("a:has-text('Download')")

                if download_link:
                    download_url = await download_link.get_attribute("href")
                    print(f"--> Live PDF Download URL: {download_url}")

                    # Fetch the generated PDF directly from the live URL
                    response = await page.request.get(download_url)
                    if response.ok:
                        pdf_bytes = await response.body()
                        with open(proof_pdf, "wb") as f:
                            f.write(pdf_bytes)
                        print(f"\n=== SUCCESS! Downloaded live proof PDF to: {proof_pdf} ===")
                        return proof_pdf

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_live_vercel_proof())
