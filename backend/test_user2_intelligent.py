import os
import asyncio
from intelligent_fuw_exam_card import run_intelligent_exam_card_solver

async def test_user2_intelligent():
    print("Executing Intelligent Portal Solver for REDACTED_USERNAME...")
    pdf_path = await run_intelligent_exam_card_solver(os.environ.get("FUW_PORTAL_USERNAME", ""), os.environ.get("FUW_PORTAL_PASSWORD", ""), "exam", "A5")
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user2_intelligent())
