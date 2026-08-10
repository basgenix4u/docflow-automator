import os
import time
import asyncio
from playwright.async_api import async_playwright

async def run_intelligent_exam_card_solver(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    target_action: str = "exam",
    paper_format: str = "A5"
):
    out_dir = "/home/user/docflow-automator/storage/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_filename = f"FUW_{target_action.upper()}_{username.replace('/', '_')}_{paper_format}.pdf"
    pdf_full_path = os.path.join(out_dir, pdf_filename)

    print(f"=== INTELLIGENT PORTAL SOLVER ENGINES ACTIVATED ===")
    print(f"Target User: {username} | Action: {target_action} | Format: {paper_format}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        try:
            # 1. Login with Session-Lock Recovery Loop
            authenticated = False
            attempts = 0
            max_attempts = 3

            while not authenticated and attempts < max_attempts:
                attempts += 1
                print(f"\n[Attempt {attempts}/{max_attempts}] Authenticating to https://ug.fuwportal.edu.ng/index.php...")

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
                if "Logout" in body_text or "MAIN MENU" in body_text or "ABDULALIM" in body_text or "IBRAHIM" in body_text:
                    print("--> Authentication Successful!")
                    authenticated = True
                elif "logged in on another device" in body_text:
                    print("--> Session lock detected on portal server. Triggering auto-logout clearance and waiting 4s...")
                    try:
                        await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                    except Exception:
                        pass
                    await page.wait_for_timeout(4000)
                else:
                    print("--> Login response pending, retrying...")
                    await page.wait_for_timeout(3000)

            if not authenticated:
                print("Could not complete authentication within attempt limit.")
                return None

            # 2. Dynamic Target Page Navigation
            target_url = f"https://ug.fuwportal.edu.ng/print_course_form.php?id={target_action}&r_val=U3R1ZGVudA=="
            print(f"\n[Solver] Navigating to target portal service URL: {target_url}")

            # Direct navigation or JS click to bypass hidden CSS menu
            action_link = await page.query_selector(f"a[href*='id={target_action}']")
            if action_link:
                print("--> Found action link in DOM. Triggering JavaScript click...")
                await page.evaluate("el => el.click()", action_link)
                await page.wait_for_timeout(3000)
            else:
                print("--> Navigating directly to action URL...")
                await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # 3. Autonomous Form Auto-Filler & Submitter Engine
            print("\n[Solver] Inspecting DOM for intermediate form selections (Session, Semester)...")

            # Detect Session Select Dropdown
            session_select = await page.query_selector("select[name*='session'], select[id*='session']")
            if session_select:
                options = await session_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Auto-selecting Academic Session: '{opt_text}' (val='{first_val}')")
                    await session_select.select_option(first_val)

            # Detect Semester Select Dropdown
            semester_select = await page.query_selector("select[name*='semester'], select[id*='semester']")
            if semester_select:
                options = await semester_select.query_selector_all("option")
                if len(options) > 1:
                    first_val = await options[1].get_attribute("value")
                    opt_text = (await options[1].inner_text()).strip()
                    print(f"--> Auto-selecting Semester: '{opt_text}' (val='{first_val}')")
                    await semester_select.select_option(first_val)

            # Detect Submit / Generate Button
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], input[value*='Print'], input[value*='Submit'], input[value*='Generate']")
            if submit_btn:
                btn_val = await submit_btn.get_attribute("value") or await submit_btn.inner_text()
                print(f"--> Triggering form submission button: '{btn_val.strip()}'")
                await submit_btn.click()
                await page.wait_for_timeout(4000)

            # 4. Inject Print CSS & Capture 100% Exact A5 Vector PDF
            print(f"\n[Solver] Injecting exact color preservation and {paper_format} layout styling...")
            await page.add_style_tag(content=f"""
                @page {{
                    size: {paper_format} portrait;
                    margin: 4mm;
                }}
                * {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            """)

            print(f"[Solver] Exporting exact live portal view to PDF: {pdf_full_path}")
            await page.pdf(
                path=pdf_full_path,
                format=paper_format,
                print_background=True,
                margin={"top": "4mm", "bottom": "4mm", "left": "4mm", "right": "4mm"}
            )

            print(f"\n=== SUCCESS! PDF EXPORT COMPLETED: {pdf_full_path} ===")
            return pdf_full_path

        except Exception as e:
            print("Solver Execution Error:", str(e))
            return None

        finally:
            print("\n[Solver] Executing immediate session release (auto-logout) to prevent device lockouts...")
            try:
                await page.evaluate("if (typeof $ === 'function') $.post('scriptfile_a.php', { contentvar: 'logout' });")
                await page.wait_for_timeout(1000)
            except Exception:
                pass
            await browser.close()
            print("[Solver] Session context closed and released.")

if __name__ == "__main__":
    asyncio.run(run_intelligent_exam_card_solver(username="BSC/BCH/24/140", password="Omotola", target_action="exam", paper_format="A5"))
