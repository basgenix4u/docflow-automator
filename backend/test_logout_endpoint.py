import httpx
import asyncio

async def test_logout_actions():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://ug.fuwportal.edu.ng",
        "Referer": "https://ug.fuwportal.edu.ng/index.php"
    }

    async with httpx.AsyncClient(verify=False, follow_redirects=True, headers=headers) as client:
        print("Testing logout contentvar...")
        for cv in ["logout", "main_logout", "user_logout", "destroy_session"]:
            data = {
                "username": "BSC/BCH/24/140",
                "contentvar": cv
            }
            res = await client.post("https://ug.fuwportal.edu.ng/scriptfile_a.php", data=data)
            print(f"Post contentvar={cv} -> status={res.status_code}, length={len(res.text)}, text={res.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_logout_actions())
