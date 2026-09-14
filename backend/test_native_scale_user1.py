import os
import asyncio
from native_scale_popup_solver import run_native_scale_popup_solver

async def test_user1_native_scale():
    print("Executing Native Scale Solver for FUW_USERNAME...")
    pdf_path = await run_native_scale_popup_solver(
        username=os.environ.get("FUW_PORTAL_USERNAME", ""),
        password=os.environ.get("FUW_PORTAL_PASSWORD", ""),
        output_filename="FUW_NativeScale_ExamCard_BSC_BCH_24_140_A5.pdf",
        paper_format="A5",
        scale_factor=0.72
    )
    print("Resulting Native Scaled PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_native_scale())
