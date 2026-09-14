import os
import asyncio
from popup_exam_card_solver import run_popup_exam_card_solver

async def test_user1_popup():
    print("Executing Popup Webview Solver for REDACTED_USERNAME...")
    pdf_path = await run_popup_exam_card_solver(
        username=os.environ.get("FUW_PORTAL_USERNAME", ""),
        password=os.environ.get("FUW_PORTAL_PASSWORD", ""),
        output_filename="FUW_Exact_Popup_ExamCard_BSC_BCH_24_140_A5.pdf"
    )
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_popup())
