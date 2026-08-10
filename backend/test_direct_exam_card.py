import httpx
import asyncio

async def test_direct_session():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://ug.fuwportal.edu.ng",
        "Referer": "https://ug.fuwportal.edu.ng/index.php"
    }

    async with httpx.AsyncClient(verify=False, follow_redirects=True, headers=headers) as client:
        print("1. Fetching index.php...")
        r0 = await client.get("https://ug.fuwportal.edu.ng/index.php")
        print(f"Index status: {r0.status_code}, cookies: {dict(client.cookies)}")

        print("\n2. Posting login credentials to scriptfile_a.php...")
        data = {
            "username": "BSC/BCH/24/140",
            "password": "Omotola",
            "contentvar": "main_login"
        }
        r1 = await client.post("https://ug.fuwportal.edu.ng/scriptfile_a.php", data=data)
        print(f"Login Post status: {r1.status_code}")
        print("Login response text preview:")
        print(r1.text[:1000])

        print("\n3. Fetching main.php...")
        r2 = await client.get("https://ug.fuwportal.edu.ng/main.php")
        print(f"Main.php status: {r2.status_code}")
        print("Main.php text preview:")
        print(r2.text[:1000])

        print("\n4. Fetching print_course_form.php?id=exam&r_val=U3R1ZGVudA==...")
        r3 = await client.get("https://ug.fuwportal.edu.ng/print_course_form.php?id=exam&r_val=U3R1ZGVudA==")
        print(f"Exam Card Page status: {r3.status_code}")
        print("\n--- EXAM CARD PAGE CONTENT ---")
        print(r3.text[:2000])

        with open("/home/user/docflow-automator/backend/exam_card_response.html", "w") as f:
            f.write(r3.text)

if __name__ == "__main__":
    asyncio.run(test_direct_session())
