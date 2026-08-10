import asyncio
from exact_architecture_a5_pdf import run_exact_architecture_a5_pdf

async def test_user1_exact_arch():
    print("Executing Exact Architecture A5 PDF Engine for BSC/BCH/24/140...")
    pdf_path = await run_exact_architecture_a5_pdf(
        username="BSC/BCH/24/140",
        password="Omotola",
        output_filename="FUW_Exact_Architecture_ExamCard_BSC_BCH_24_140_A5.pdf"
    )
    print("Resulting PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_user1_exact_arch())
