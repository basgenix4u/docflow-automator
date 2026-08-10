import os
import asyncio
from playwright.async_api import async_playwright

async def render_exact_a5_exam_card():
    # Exact portal A5 layout matching ug.fuwportal.edu.ng dashboard & print_course_form.php
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Federal University Wukari — Student Examination Card (A5 Output)</title>
        <style>
            @page {
                size: A5 portrait;
                margin: 6mm;
            }
            body {
                font-family: Arial, Helvetica, sans-serif;
                color: #1e293b;
                background-color: #ffffff;
                margin: 0;
                padding: 0;
                font-size: 8.5pt;
            }
            .portal-container {
                border: 1.5px solid #0284c7;
                border-radius: 6px;
                padding: 12px;
            }
            .header-bar {
                text-align: center;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 8px;
                margin-bottom: 10px;
            }
            .univ-header {
                font-size: 13pt;
                font-weight: 800;
                color: #0f172a;
                text-transform: uppercase;
                margin: 0;
            }
            .portal-sub {
                font-size: 9.5pt;
                font-weight: 700;
                color: #0284c7;
                margin: 2px 0;
                text-transform: uppercase;
            }
            .session-sub {
                font-size: 8pt;
                color: #475569;
                font-weight: 600;
            }
            .badge-session {
                display: inline-block;
                background: #e0f2fe;
                color: #0369a1;
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 7.5pt;
                margin-top: 4px;
                border: 1px solid #bae6fd;
            }
            .profile-grid {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }
            .profile-grid td {
                padding: 3px 5px;
                font-size: 8pt;
                vertical-align: top;
            }
            .lbl {
                font-weight: bold;
                color: #64748b;
                width: 22%;
            }
            .val {
                color: #0f172a;
                font-weight: 700;
                width: 28%;
            }
            .passport-box {
                width: 70px;
                height: 85px;
                border: 1.5px dashed #94a3b8;
                border-radius: 4px;
                background-color: #f8fafc;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
            }
            .sec-title {
                background: #f1f5f9;
                border-left: 3px solid #0284c7;
                padding: 4px 8px;
                font-size: 8.5pt;
                font-weight: bold;
                color: #0f172a;
                margin-top: 8px;
                margin-bottom: 6px;
                text-transform: uppercase;
            }
            .courses-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
                margin-bottom: 10px;
            }
            .courses-table th {
                background-color: #0284c7;
                color: #ffffff;
                font-size: 7.5pt;
                font-weight: bold;
                text-align: left;
                padding: 5px 6px;
                border: 1px solid #0284c7;
                text-transform: uppercase;
            }
            .courses-table td {
                border: 1px solid #cbd5e1;
                padding: 4px 6px;
                font-size: 7.5pt;
                color: #0f172a;
            }
            .courses-table tr:nth-child(even) {
                background-color: #f8fafc;
            }
            .sig-space {
                text-align: center;
                color: #94a3b8;
                font-size: 7pt;
                font-style: italic;
            }
            .notes-box {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 6px;
                background-color: #f8fafc;
                font-size: 7pt;
                color: #334155;
                line-height: 1.3;
            }
            .sig-row {
                margin-top: 14px;
                width: 100%;
            }
            .sig-cell {
                width: 48%;
                display: inline-block;
                text-align: center;
            }
            .sig-line-text {
                border-top: 1px solid #475569;
                margin-top: 25px;
                padding-top: 2px;
                font-size: 7.5pt;
                font-weight: bold;
            }
            .footer-meta {
                margin-top: 10px;
                text-align: center;
                font-size: 6.5pt;
                color: #64748b;
                border-top: 1px dashed #cbd5e1;
                padding-top: 4px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="portal-container">
            <div class="header-bar">
                <table style="width: 100%;">
                    <tr>
                        <td style="width: 15%; text-align: center; font-weight: bold; font-size: 16pt; color: #0284c7;">FUW</td>
                        <td style="width: 70%; text-align: center;">
                            <div class="univ-header">Federal University Wukari</div>
                            <div class="portal-sub">Student Examination Card & Docket</div>
                            <div class="session-sub">First Semester • 2025/2026 Academic Session</div>
                            <div class="badge-session">UG PORTAL VERIFIED • A5 SIZE EXPORT</div>
                        </td>
                        <td style="width: 15%; text-align: center;">
                            <div class="passport-box">
                                <span style="font-size: 6.5pt; color: #64748b; font-weight: bold;">PASSPORT</span>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>

            <div class="sec-title">Student Profile & Academic Details</div>
            <table class="profile-grid">
                <tr>
                    <td class="lbl">Student Name:</td>
                    <td class="val" style="color: #0284c7;">ABDULALIM, Abdulbasit</td>
                    <td class="lbl">Matric No:</td>
                    <td class="val">ENG/COE/21/013</td>
                </tr>
                <tr>
                    <td class="lbl">Faculty:</td>
                    <td class="val">Engineering</td>
                    <td class="lbl">Department:</td>
                    <td class="val">Computer Engineering</td>
                </tr>
                <tr>
                    <td class="lbl">Programme:</td>
                    <td class="val">B.Eng. Computer Engineering</td>
                    <td class="lbl">Current Level:</td>
                    <td class="val">500 Level</td>
                </tr>
            </table>

            <div class="sec-title">Registered Examination Courses</div>
            <table class="courses-table">
                <thead>
                    <tr>
                        <th style="width: 8%;">#</th>
                        <th style="width: 18%;">Code</th>
                        <th style="width: 44%;">Course Title</th>
                        <th style="width: 10%;">Units</th>
                        <th style="width: 20%; text-align: center;">Invigilator</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><strong>COE 501</strong></td>
                        <td>Computer Systems Architecture</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td><strong>COE 503</strong></td>
                        <td>Microprocessor & Embedded Systems Design</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td><strong>COE 505</strong></td>
                        <td>Data Communication & Computer Networks</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td><strong>COE 507</strong></td>
                        <td>Digital Signal Processing</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>5</td>
                        <td><strong>COE 597</strong></td>
                        <td>Final Year Project Phase I</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>6</td>
                        <td><strong>EEE 501</strong></td>
                        <td>Control Engineering II</td>
                        <td>3</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td><strong>GST 311</strong></td>
                        <td>Entrepreneurship & Innovation</td>
                        <td>2</td>
                        <td class="sig-space">[ Sign ]</td>
                    </tr>
                    <tr style="background-color: #e0f2fe; font-weight: bold;">
                        <td colspan="3" style="text-align: right;">TOTAL REGISTERED UNITS:</td>
                        <td>20</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <div class="notes-box">
                <strong>INSTRUCTIONS TO CANDIDATES:</strong><br/>
                1. This Exam Card must be presented at the entrance of every examination hall.<br/>
                2. Mobile phones, smart watches, and unauthorized materials are strictly prohibited.<br/>
                3. Invigilators must sign against each course after script submission.
            </div>

            <div class="sig-row">
                <div class="sig-cell" style="float: left;">
                    <div class="sig-line-text">
                        Student Signature<br/>
                        <span style="font-size: 6.5pt; font-weight: normal; color: #64748b;">(ABDULALIM, Abdulbasit)</span>
                    </div>
                </div>
                <div class="sig-cell" style="float: right;">
                    <div class="sig-line-text">
                        Dean of Engineering / Registrar<br/>
                        <span style="font-size: 6.5pt; font-weight: normal; color: #64748b;">Federal University Wukari</span>
                    </div>
                </div>
                <div style="clear: both;"></div>
            </div>

            <div class="footer-meta">
                VERIFICATION KEY: FUW-EXAM-2026-ENG-COE-21-013-A5-EXPORT • UG.FUWPORTAL.EDU.NG
            </div>
        </div>
    </body>
    </html>
    """

    out_file = "/home/user/docflow-automator/storage/pdfs/FUW_ExamCard_ENG_COE_21_013_Exact_A5.pdf"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")

        # Render EXACT A5 PDF Output
        await page.pdf(
            path=out_file,
            format="A5",
            print_background=True,
            margin={"top": "5mm", "bottom": "5mm", "left": "5mm", "right": "5mm"}
        )

        await browser.close()

    print(f"Rendered exact A5 Examination Card PDF: {out_file}")

if __name__ == "__main__":
    asyncio.run(render_exact_a5_exam_card())
