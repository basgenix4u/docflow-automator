import os
import asyncio
from playwright.async_api import async_playwright

async def safe_fetch_exact_a5_exam_card(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    output_filename: str = "FUW_Exact_Portal_ExamCard_ENG_COE_21_013_A5.pdf"
):
    out_path = f"/home/user/docflow-automator/storage/pdfs/{output_filename}"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    async with async_playwright() as p:
        # Launch Chromium
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            print(f"1. Pre-clearing any stale session lock for user {username}...")
            try:
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.evaluate("""
                    if (typeof $ === 'function') {
                        $.post('scriptfile_a.php', { contentvar: 'logout', username: '""" + username + """' });
                    }
                """)
                await page.wait_for_timeout(1000)
            except Exception as e:
                print("Pre-clear warning:", e)

            print(f"2. Logging in to portal as {username}...")
            await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")

            await page.fill("#userId", username)
            await page.fill("#password", password)

            login_btn = await page.query_selector("button, input[type='submit'], input[type='button'], a.btn")
            if login_btn:
                await login_btn.click()
            else:
                await page.press("#password", "Enter")

            await page.wait_for_timeout(4000)

            body_text = await page.inner_text("body")
            if "logged in on another device" in body_text:
                print("Session lock active. Calling logout endpoint and retrying...")
                await page.evaluate("$.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(2000)
                await page.goto("https://ug.fuwportal.edu.ng/index.php", wait_until="networkidle")
                await page.fill("#userId", username)
                await page.fill("#password", password)
                if login_btn:
                    await login_btn.click()
                else:
                    await page.press("#password", "Enter")
                await page.wait_for_timeout(4000)

            print("3. Navigating to Exam Card page (print_course_form.php?id=exam&r_val=U3R1ZGVudA==)...")
            await page.goto("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==", wait_until="networkidle")
            await page.wait_for_timeout(3000)

            # Inject CSS for Exact Color Printing & A5 Size Scaling
            print("4. Injecting CSS page rules for exact color printing and A5 paper format...")
            await page.add_style_tag(content="""
                @page {
                    size: A5 portrait;
                    margin: 4mm;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            """)

            # Render Exact Live Portal DOM to A5 PDF
            print("5. Rendering exact live DOM to A5 PDF...")
            await page.pdf(
                path=out_path,
                format="A5",
                print_background=True,
                margin={"top": "4mm", "bottom": "4mm", "left": "4mm", "right": "4mm"}
            )
            print(f"SUCCESS! Rendered exact live Exam Card A5 PDF to: {out_path}")

        except Exception as err:
            print("Automation error:", err)

        finally:
            print("6. IMMEDIATELY LOGGING OUT to prevent session lockout on user's device...")
            try:
                await page.evaluate("""
                    if (typeof $ === 'function') {
                        $.post('scriptfile_a.php', { contentvar: 'logout' });
                    }
                """)
                await page.wait_for_timeout(1000)
            except Exception as ex:
                print("Logout cleanup error:", ex)

            await browser.close()
            print("Browser closed. Session released completely.")

if __name__ == "__main__":
    asyncio.run(safe_fetch_exact_a5_exam_card())
