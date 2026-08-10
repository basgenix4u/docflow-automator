import asyncio
from popup_exam_card_solver import run_popup_exam_card_solver

async def test_user1_popup():
    print("Executing Popup Webview Solver for BSC/BCH/24/140...")
    pdf_path = await run_popup_exam_card_solver(
        username="BSC/BCH/24/140",
        password="Omotola",
        output_filename="FUW_Exact_Popup_ExamCard_BSC_BCH_24_140_A5.pdf"
    )
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_popup())
