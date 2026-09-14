import os
import asyncio
from test_course_form_webview import run_course_form_exact_a4

async def test_user1_course_form():
    print("Executing Exact Architecture A4 Course Form Engine for FUW_USERNAME...")
    pdf_path = await run_course_form_exact_a4(
        username=os.environ.get("FUW_PORTAL_USERNAME", ""),
        password=os.environ.get("FUW_PORTAL_PASSWORD", ""),
        output_filename="FUW_1Page_CourseForm_BSC_BCH_24_140_A4.pdf"
    )
    print("Resulting A4 Course Form PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_course_form())
