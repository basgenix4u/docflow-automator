import asyncio
from intelligent_fuw_exam_card import run_intelligent_exam_card_solver

async def test_fresh_user():
    print("Executing Intelligent Portal Solver for REDACTED_USERNAME...")
    pdf_path = await run_intelligent_exam_card_solver("REDACTED_USERNAME", "REDACTED_PASSWORD", "exam", "A5")
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_fresh_user())
