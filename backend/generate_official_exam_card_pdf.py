import os
import asyncio
from playwright.async_api import async_playwright

async def render_fuw_exam_card_pdf():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Federal University Wukari — Official Student Examination Card</title>
        <style>
            @page {
                size: A4 portrait;
                margin: 12mm;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #0f172a;
                background-color: #ffffff;
                margin: 0;
                padding: 0;
            }
            .card-container {
                border: 2px solid #0284c7;
                border-radius: 8px;
                padding: 20px;
                position: relative;
            }
            .header-table {
                width: 100%;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 12px;
                margin-bottom: 16px;
            }
            .logo-cell {
                width: 15%;
                vertical-align: middle;
                text-align: center;
            }
            .title-cell {
                width: 70%;
                text-align: center;
                vertical-align: middle;
            }
            .passport-cell {
                width: 15%;
                vertical-align: middle;
                text-align: center;
            }
            .univ-name {
                font-size: 18pt;
                font-weight: 800;
                color: #0f172a;
                text-transform: uppercase;
                margin: 0;
                letter-spacing: 0.5px;
            }
            .sub-title {
                font-size: 12pt;
                font-weight: 700;
                color: #0284c7;
                margin: 4px 0 0 0;
                text-transform: uppercase;
            }
            .session-title {
                font-size: 10pt;
                font-weight: 600;
                color: #475569;
                margin-top: 2px;
            }
            .passport-box {
                width: 90px;
                height: 110px;
                border: 2px dashed #94a3b8;
                border-radius: 6px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: #f8fafc;
                margin: 0 auto;
            }
            .passport-text {
                font-size: 8pt;
                color: #64748b;
                font-weight: bold;
                text-align: center;
                margin-top: 4px;
            }
            .badge-verified {
                display: inline-block;
                background-color: #dcfce7;
                color: #15803d;
                border: 1px solid #86efac;
                font-size: 9pt;
                font-weight: bold;
                padding: 3px 10px;
                border-radius: 4px;
                margin-top: 6px;
            }
            .section-header {
                background-color: #f1f5f9;
                border-left: 4px solid #0284c7;
                padding: 6px 10px;
                font-size: 10pt;
                font-weight: bold;
                color: #0f172a;
                margin-top: 14px;
                margin-bottom: 10px;
                text-transform: uppercase;
            }
            .info-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
            }
            .info-table td {
                padding: 5px 8px;
                font-size: 9.5pt;
                vertical-align: top;
            }
            .label-td {
                font-weight: bold;
                color: #475569;
                width: 20%;
            }
            .val-td {
                color: #0f172a;
                font-weight: 600;
                width: 30%;
            }
            .courses-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
                margin-bottom: 16px;
            }
            .courses-table th {
                background-color: #0284c7;
                color: #ffffff;
                font-size: 9pt;
                font-weight: bold;
                text-align: left;
                padding: 7px 10px;
                border: 1px solid #0284c7;
                text-transform: uppercase;
            }
            .courses-table td {
                border: 1px solid #cbd5e1;
                padding: 7px 10px;
                font-size: 9pt;
                color: #1e293b;
            }
            .courses-table tr:nth-child(even) {
                background-color: #f8fafc;
            }
            .sig-col {
                width: 22%;
                text-align: center;
                color: #94a3b8;
                font-style: italic;
                font-size: 8pt;
            }
            .rules-box {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                background-color: #f8fafc;
                font-size: 8pt;
                color: #334155;
                line-height: 1.4;
            }
            .rules-title {
                font-weight: bold;
                color: #0f172a;
                margin-bottom: 4px;
                text-transform: uppercase;
            }
            .footer-signatures {
                margin-top: 24px;
                width: 100%;
            }
            .sig-box {
                width: 45%;
                display: inline-block;
                text-align: center;
                vertical-align: top;
            }
            .sig-line {
                border-top: 1px solid #64748b;
                margin-top: 35px;
                padding-top: 4px;
                font-size: 9pt;
                font-weight: bold;
                color: #0f172a;
            }
            .verification-footer {
                margin-top: 16px;
                text-align: center;
                font-size: 7.5pt;
                color: #64748b;
                border-top: 1px dashed #cbd5e1;
                padding-top: 8px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="card-container">
            <table class="header-table">
                <tr>
                    <td class="logo-cell">
                        <div style="font-size: 24pt; font-weight: bold; color: #0284c7;">FUW</div>
                    </td>
                    <td class="title-cell">
                        <div class="univ-name">Federal University Wukari</div>
                        <div class="sub-title">Official Student Examination Card</div>
                        <div class="session-title">First Semester • 2025/2026 Academic Session</div>
                        <div class="badge-verified">OFFICIAL PORTAL VALIDATED DOCKET</div>
                    </td>
                    <td class="passport-cell">
                        <div class="passport-box">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            <span class="passport-text">AFFIX PASSPORT</span>
                        </div>
                    </td>
                </tr>
            </table>

            <div class="section-header">1. Candidate Personal & Academic Details</div>
            <table class="info-table">
                <tr>
                    <td class="label-td">Student Name:</td>
                    <td class="val-td" style="color: #0284c7; font-size: 10.5pt;">IBRAHIM, Abibat Abiodun</td>
                    <td class="label-td">Matric / Reg No:</td>
                    <td class="val-td" style="color: #0f172a; font-size: 10.5pt;">BSC/BCH/24/140</td>
                </tr>
                <tr>
                    <td class="label-td">Faculty:</td>
                    <td class="val-td">Biosciences</td>
                    <td class="label-td">Department:</td>
                    <td class="val-td">Biochemistry</td>
                </tr>
                <tr>
                    <td class="label-td">Programme:</td>
                    <td class="val-td">B.Sc. Biochemistry</td>
                    <td class="label-td">Current Level:</td>
                    <td class="val-td">200 Level</td>
                </tr>
                <tr>
                    <td class="label-td">Level Adviser:</td>
                    <td class="val-td">Mr. BILYAMINU Habibu .</td>
                    <td class="label-td">Adviser Email:</td>
                    <td class="val-td">habibu@fuwukari.edu.ng</td>
                </tr>
            </table>

            <div class="section-header">2. Registered Examination Courses (First Semester 2025/2026)</div>
            <table class="courses-table">
                <thead>
                    <tr>
                        <th style="width: 8%;">S/N</th>
                        <th style="width: 15%;">Course Code</th>
                        <th style="width: 42%;">Course Title</th>
                        <th style="width: 12%;">Units</th>
                        <th class="sig-col" style="color: #ffffff; font-style: normal;">Invigilator Sign</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><strong>BCH 201</strong></td>
                        <td>Introductory Biochemistry I</td>
                        <td>3 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td><strong>BCH 203</strong></td>
                        <td>Bioenergetics & Biochemical Metabolism</td>
                        <td>3 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td><strong>BCH 205</strong></td>
                        <td>Analytical Biochemistry & Biophysical Techniques</td>
                        <td>2 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td><strong>CHM 211</strong></td>
                        <td>General Organic Chemistry I</td>
                        <td>3 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>5</td>
                        <td><strong>MCB 201</strong></td>
                        <td>General Microbiology I</td>
                        <td>3 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>6</td>
                        <td><strong>BIO 201</strong></td>
                        <td>General Genetics</td>
                        <td>2 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr>
                        <td>7</td>
                        <td><strong>GST 211</strong></td>
                        <td>Environment & Sustainable Development</td>
                        <td>2 Units</td>
                        <td class="sig-col">[ Signature ]</td>
                    </tr>
                    <tr style="background-color: #e0f2fe; font-weight: bold;">
                        <td colspan="3" style="text-align: right; text-transform: uppercase;">Total Registered Credit Units:</td>
                        <td>18 Units</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <div class="rules-box">
                <div class="rules-title">Important Candidate Instructions & Examination Rules</div>
                <ol style="margin: 0; padding-left: 16px;">
                    <li>This Examination Card must be produced by the candidate at every examination session alongside a valid University Identity Card.</li>
                    <li>Candidates must arrive at the designated Examination Hall at least 30 minutes prior to scheduled commencement time.</li>
                    <li>Mobile phones, smart watches, bags, and unauthorized printed/electronic materials are strictly prohibited inside the hall.</li>
                    <li>Invigilators must sign the card against each course upon receipt of answer scripts.</li>
                </ol>
            </div>

            <div class="footer-signatures">
                <div class="sig-box" style="float: left;">
                    <div class="sig-line">
                        Candidate Signature & Date<br/>
                        <span style="font-size: 7.5pt; color: #64748b; font-weight: normal;">(IBRAHIM, Abibat Abiodun)</span>
                    </div>
                </div>
                <div class="sig-box" style="float: right;">
                    <div class="sig-line">
                        Dean, Faculty of Biosciences / Registrar<br/>
                        <span style="font-size: 7.5pt; color: #64748b; font-weight: normal;">Federal University Wukari</span>
                    </div>
                </div>
                <div style="clear: both;"></div>
            </div>

            <div class="verification-footer">
                VERIFICATION HASH: FUW-EXAM-2026-BSC-BCH-24-140-8F92A • GENERATED VIA DOCFLOW AUTOMATOR ENGINE • UG.FUWPORTAL.EDU.NG
            </div>
        </div>
    </body>
    </html>
    """

    out_path = "/home/user/docflow-automator/storage/pdfs/FUW_Exam_Card_BSC_BCH_24_140.pdf"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")

        await page.pdf(
            path=out_path,
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )

        await browser.close()

    print(f"Generated official Exam Card PDF at: {out_path}")

if __name__ == "__main__":
    asyncio.run(render_fuw_exam_card_pdf())
