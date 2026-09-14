import os
import time
import asyncio
from intelligent_fuw_exam_card import run_intelligent_exam_card_solver

async def main():
    print("Waiting 15 seconds for portal session lock to release...")
    await asyncio.sleep(15)
    print("Executing Intelligent Portal Solver...")
    pdf_path = await run_intelligent_exam_card_solver(os.environ.get("FUW_PORTAL_USERNAME", ""), os.environ.get("FUW_PORTAL_PASSWORD", ""), "exam", "A5")
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(main())
