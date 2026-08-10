import asyncio
from single_page_popup_solver import run_single_page_popup_solver

async def test_user1_single_page():
    print("Executing Single-Page A5 Solver for REDACTED_USERNAME...")
    pdf_path = await run_single_page_popup_solver(
        username="REDACTED_USERNAME",
        password="REDACTED_PASSWORD",
        output_filename="FUW_1Page_ExamCard_BSC_BCH_24_140_A5.pdf",
        paper_format="A5"
    )
    print("Resulting 1-Page PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_single_page())
