# Thaura.ai Link Crawler

Automated link testing for **Thaura.ai** using **Python + Pytest + Playwright**.

## Purpose

This project checks website links automatically and helps identify:

* Broken links / 4xx / 5xx responses
* Incorrect destinations
* HTTP links on the HTTPS website
* Internal and external links
* Links loaded after scrolling
* Duplicate page/link testing

## Test Flow

The crawler follows this order:

```text
Open Page
   ↓
Header Links
   ↓
Full Page Scroll
   ↓
Content Links
   ↓
Footer Links
   ↓
Next Unique Internal Page
```

### Important behavior

* A page is tested only **once**.
* A link is tested only **once**, even if it appears in multiple places.
* The crawler scrolls the complete page to discover dynamically/lazy-loaded links.
* New internal pages are added to the queue automatically.
* External links are checked but are not recursively crawled.

## Project Structure

```text
thaura_task02_link_test/
│
├── tests/
│   ├── __init__.py
│   └── test_link_crawler.py
│
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

> `.venv/` is local only and should not be committed to GitHub.

## Requirements

* Python 3.x
* Pytest
* Playwright
* Chromium

## Windows Setup

Open PowerShell inside the project:

```powershell
cd E:\thaura_task02_link_test
```

Create virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Install Playwright Chromium:

```powershell
playwright install chromium
```

## Run Test

```powershell
pytest -v -s
```

The Playwright browser will open and start crawling:

```text
Header
→ Full Page Scroll
→ Content
→ Footer
→ Next Internal Page
```

## Report

After execution, the crawler generates:

```text
thaura_link_report.csv
```

The report contains:

```text
source_page
area
link_text
url
internal
status
final_url
result
error
```

Example:

```text
PASS | Header  | 200 | Pricing | https://thaura.ai/pricing
PASS | Footer  | 200 | Contact | https://thaura.ai/contact
FAIL | Content | 404 | Example | https://thaura.ai/example
```

## Main Test

The main pytest file is:

```text
tests/test_link_crawler.py
```

Run only this test:

```powershell
pytest tests/test_link_crawler.py -v -s
```

## Linux

```bash
cd ~/thaura_task02_link_test

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

pytest -v -s
```

## Target Website

```text
https://thaura.ai/
```
