import os
import time
import json
import logging
from typing import Dict, Any, Tuple, List
from popup_exam_card_solver import run_popup_exam_card_solver

logger = logging.getLogger("fuw_portal")

async def execute_fuw_portal_automation(
    username: str = "ENG/COE/21/013",
    password: str = "olaleke",
    portal_url: str = "https://ug.fuwportal.edu.ng/index.php",
    page_format: str = "A5"
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Executes popup webview interception to capture the exact live exam_card_printout.php DOM and export to A5 PDF.
    """
    start_time = time.time()
    logs: List[Dict[str, Any]] = []

    def log(msg: str, level: str = "INFO"):
        logs.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "level": level, "message": msg})
        logger.info(msg)

    log(f"Initiating Popup Interceptor Automation for portal: {portal_url}")
    log(f"Target student ID: {username}")

    safe_name = username.replace('/', '_')
    out_filename = f"FUW_Exact_Popup_ExamCard_{safe_name}_A5.pdf"

    pdf_file_path = await run_popup_exam_card_solver(
        username=username,
        password=password,
        output_filename=out_filename
    )

    extracted_data = {
        "portal_url": portal_url,
        "student_id": username,
        "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "popup_webview_url": "https://ug.fuwportal.edu.ng/exam_card_printout.php",
        "pdf_export_path": pdf_file_path
    }

    if pdf_file_path:
        log(f"Exact Popup Webview A5 PDF successfully exported: {pdf_file_path}")
    else:
        log("Failed to capture popup webview PDF", level="ERROR")
        extracted_data["error"] = "Automation could not capture popup webview"

    duration_ms = int((time.time() - start_time) * 1000)
    log(f"Total automation duration: {duration_ms} ms")

    return extracted_data, logs, pdf_file_path or ""
