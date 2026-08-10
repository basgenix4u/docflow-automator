import asyncio
from app.services.fuw_portal import execute_fuw_portal_automation

async def test_fuw_automation_user2():
    data, logs, pdf_path = await execute_fuw_portal_automation(
        username="ENG/COE/21/013",
        password="olaleke",
        page_format="A5"
    )
    print("Extracted Data:", data)
    print("Generated PDF Path:", pdf_path)

if __name__ == "__main__":
    asyncio.run(test_fuw_automation_user2())
