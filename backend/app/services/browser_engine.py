import time
import json
import logging
from typing import Dict, Any, Tuple, List
from playwright.async_api import async_playwright

logger = logging.getLogger("browser_engine")

async def execute_custom_workflow(
    portal_url: str,
    steps: List[Dict[str, Any]],
    demo_username: str = "",
    demo_password: str = ""
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Executes dynamic workflow steps in an isolated browser context.
    """
    start_time = time.time()
    logs: List[Dict[str, Any]] = []
    extracted_data: Dict[str, Any] = {}

    def log(msg: str, level: str = "INFO"):
        logs.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "level": level, "message": msg})
        logger.info(msg)

    log(f"Starting custom workflow execution on portal {portal_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        try:
            log(f"Navigating to {portal_url}...")
            await page.goto(portal_url, wait_until="networkidle", timeout=30000)

            for idx, step in enumerate(steps, 1):
                action = step.get("action")
                selector = step.get("selector")
                val = step.get("value")
                target_var = step.get("target_var")

                log(f"Step {idx}: Action={action}, Selector={selector}")

                if action == "fill" and selector and val is not None:
                    # Substitute demo credentials if specified
                    if val == "$USERNAME":
                        val = demo_username
                    elif val == "$PASSWORD":
                        val = demo_password
                    await page.fill(selector, val)
                    log(f"Filled '{selector}'")

                elif action == "click" and selector:
                    await page.click(selector)
                    log(f"Clicked '{selector}'")
                    await page.wait_for_timeout(2000)

                elif action == "extract" and selector and target_var:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        extracted_data[target_var] = text.strip()
                        log(f"Extracted '{target_var}' = '{text.strip()[:50]}...'")

                elif action == "wait":
                    wait_ms = int(val) if val and str(val).isdigit() else 2000
                    await page.wait_for_timeout(wait_ms)
                    log(f"Waited {wait_ms} ms")

            log("Workflow steps completed successfully.")

        except Exception as e:
            log(f"Workflow step execution error: {str(e)}", level="ERROR")
            extracted_data["error"] = str(e)
        finally:
            await browser.close()

    return extracted_data, logs
