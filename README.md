# Thaura.ai Task 02 – Link Validation

Playwright + Pytest automation project for testing Thaura.ai links.

## 1. Clone

```powershell
git clone <repository-url>
cd thaura_task02_link_tests
```

## 2. Setup

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
```

This installs Python dependencies, Playwright Chromium, and Allure.

## 3. Run Tests

```powershell
.\run_tests.ps1
```

## 4. Open Allure Report

```powershell
.\open_report.ps1
```

## Manual Commands

Run tests:

```powershell
python -m pytest
```

Open Allure:

```powershell
.\tools\allure\node_modules\.bin\allure.cmd serve allure-results
```

## Tested

* Internal links
* External links
* HTTP status
* 404/broken links
* Redirects
* HTTPS mixed-content links
* Download links
* Duplicate links/pages
* Lazy-loaded links
* Header, content and footer links
