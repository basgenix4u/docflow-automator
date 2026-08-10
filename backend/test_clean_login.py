import httpx
import asyncio

async def test_clean_login():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://ug.fuwportal.edu.ng",
        "Referer": "https://ug.fuwportal.edu.ng/index.php"
    }

    async with httpx.AsyncClient(verify=False, follow_redirects=True, headers=headers) as client:
        # 1. Clear session first
        await client.post("https://ug.fuwportal.edu.ng/scriptfile_a.php", data={"username": "BSC/BCH/24/140", "contentvar": "logout"})

        # 2. Get index.php to initialize fresh PHPSESSID cookie
        await client.get("https://ug.fuwportal.edu.ng/index.php")

        # 3. Post login
        data = {
            "username": "BSC/BCH/24/140",
            "password": "Omotola",
            "contentvar": "main_login"
        }
        res_login = await client.post("https://ug.fuwportal.edu.ng/scriptfile_a.php", data=data)
        print("Login response status:", res_login.status_code)
        print("Login response text:")
        print(res_login.text[:800])

if __name__ == "__main__":
    asyncio.run(test_clean_login())
