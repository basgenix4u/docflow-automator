import time
import httpx
import logging
from typing import Dict, Any, List, Tuple
from playwright.async_api import async_playwright

logger = logging.getLogger("security_scanner")

async def scan_portal_security(portal_url: str) -> Tuple[int, int, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Scans target portal for authentication security controls and HTTP security headers.
    Returns: (score_0_100, vulnerability_count, tests_executed_list, detailed_report_dict)
    """
    tests_executed: List[Dict[str, Any]] = []
    vulnerabilities: List[Dict[str, Any]] = []
    score = 100

    logger.info(f"Initiating security scan on target portal: {portal_url}")

    # 1. HTTP Headers & Transport Audit
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            resp = await client.get(portal_url)
            headers = resp.headers

            # Test A: HTTPS Transport
            is_https = portal_url.startswith("https://")
            tests_executed.append({
                "name": "HTTPS Encryption",
                "category": "TRANSPORT",
                "passed": is_https,
                "details": "Portal enforces SSL/TLS transport" if is_https else "Portal communicates over unencrypted HTTP"
            })
            if not is_https:
                score -= 25
                vulnerabilities.append({"severity": "CRITICAL", "title": "Missing HTTPS", "description": "Traffic sent in cleartext."})

            # Test B: Security Headers
            security_headers = {
                "strict-transport-security": ("HSTS Header", "HIGH", 10),
                "x-content-type-options": ("MIME Sniffing Protection", "MEDIUM", 5),
                "x-frame-options": ("Clickjacking Protection (X-Frame-Options)", "HIGH", 10),
                "content-security-policy": ("Content Security Policy (CSP)", "HIGH", 10),
                "x-xss-protection": ("Legacy XSS Protection", "LOW", 2)
            }

            for header, (name, severity, penalty) in security_headers.items():
                header_present = header in headers
                tests_executed.append({
                    "name": name,
                    "category": "HTTP_HEADERS",
                    "passed": header_present,
                    "value": headers.get(header, "NOT_SET"),
                    "details": f"Header '{header}' is {'present' if header_present else 'missing'}"
                })
                if not header_present:
                    score -= penalty
                    vulnerabilities.append({
                        "severity": severity,
                        "title": f"Missing Header: {name}",
                        "description": f"The '{header}' HTTP security header is not configured on response."
                    })

            # Test C: Cookies Audit
            cookies = resp.cookies
            for cookie in cookies.jar:
                is_secure = cookie.secure
                is_httponly = "httponly" in [k.lower() for k in cookie._rest.keys()]
                tests_executed.append({
                    "name": f"Cookie Security: {cookie.name}",
                    "category": "SESSION_SECURITY",
                    "passed": is_secure and is_httponly,
                    "details": f"Secure={is_secure}, HttpOnly={is_httponly}"
                })
                if not is_secure or not is_httponly:
                    score -= 5
                    vulnerabilities.append({
                        "severity": "MEDIUM",
                        "title": f"Insecure Cookie Flags ({cookie.name})",
                        "description": f"Cookie {cookie.name} lacks Secure or HttpOnly flags."
                    })

    except Exception as e:
        logger.error(f"HTTP header audit error: {str(e)}")

    # 2. Form & DOM Security Controls Audit via Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        try:
            await page.goto(portal_url, wait_until="networkidle", timeout=15000)

            # Test D: Form CSRF Protection
            forms = await page.query_selector_all("form")
            has_csrf = False
            for form in forms:
                inputs = await form.query_selector_all("input[type='hidden']")
                for inp in inputs:
                    name = (await inp.get_attribute("name") or "").lower()
                    if "csrf" in name or "token" in name or "nonce" in name:
                        has_csrf = True
                        break

            tests_executed.append({
                "name": "Form CSRF Token Protection",
                "category": "AUTHENTICATION",
                "passed": has_csrf,
                "details": "CSRF hidden input token detected" if has_csrf else "No explicit CSRF anti-forgery token found in login form"
            })
            if not has_csrf:
                score -= 15
                vulnerabilities.append({
                    "severity": "HIGH",
                    "title": "Missing CSRF Anti-Forgery Token",
                    "description": "Login form does not include an explicit CSRF token parameter."
                })

            # Test E: Password Input Security
            pwd_input = await page.query_selector("input[type='password']")
            if pwd_input:
                autocomplete = await pwd_input.get_attribute("autocomplete")
                tests_executed.append({
                    "name": "Password Input Autocomplete Configuration",
                    "category": "AUTHENTICATION",
                    "passed": autocomplete != "off",
                    "details": f"Autocomplete attribute: {autocomplete or 'default'}"
                })

        except Exception as e:
            logger.error(f"DOM security audit error: {str(e)}")
        finally:
            await browser.close()

    # Normalize score
    final_score = max(0, min(100, score))
    vulnerability_count = len(vulnerabilities)

    report = {
        "portal_url": portal_url,
        "scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": final_score,
        "total_tests": len(tests_executed),
        "vulnerabilities_found": vulnerability_count,
        "vulnerabilities": vulnerabilities,
        "tests": tests_executed
    }

    return final_score, vulnerability_count, tests_executed, report
