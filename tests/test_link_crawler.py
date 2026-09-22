import csv
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://thaura.ai/"
REPORT_FILE = Path("thaura_link_report.csv")
MAX_PAGES = 200


def normalize_url(href, base_url):
    if not href:
        return None
    href = href.strip()
    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    url = urljoin(base_url, href)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    return url.split("#")[0]


def is_internal(url):
    return urlparse(url).netloc.lower() == urlparse(BASE_URL).netloc.lower()


def get_area(anchor):
    return anchor.evaluate(
        """el => {
            if (el.closest('header')) return 'Header';
            if (el.closest('footer')) return 'Footer';
            if (el.closest('nav')) return 'Navigation';
            return 'Content';
        }"""
    )


def scroll_full_page(page):
    last_height = 0
    stable_rounds = 0
    for _ in range(50):
        height = page.evaluate("document.body.scrollHeight")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height and new_height == height:
            stable_rounds += 1
        else:
            stable_rounds = 0
        last_height = new_height
        if stable_rounds >= 2:
            break
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    yield page
    context.close()


def test_thaura_link_crawler(page):
    tested_pages = set()
    queued_pages = set()
    tested_links = set()
    page_queue = [BASE_URL]
    report_rows = []

    while page_queue and len(tested_pages) < MAX_PAGES:
        current_page_url = normalize_url(page_queue.pop(0), BASE_URL)
        if not current_page_url or current_page_url in tested_pages:
            continue
        tested_pages.add(current_page_url)

        print("\n" + "=" * 100)
        print(f"PAGE {len(tested_pages)}: {current_page_url}")
        print("=" * 100)

        try:
            response = page.goto(current_page_url, wait_until="commit", timeout=30000)
            page.wait_for_timeout(2500)
            page_status = response.status if response else None
            if page_status and page_status >= 400:
                pytest.fail(f"Page failed: {current_page_url} -> HTTP {page_status}")

            # Header -> Content/full scroll -> Footer
            print("\n[1] HEADER LINKS")
            for anchor in page.locator("header a[href]").all():
                href = anchor.get_attribute("href")
                url = normalize_url(href, page.url)
                if not url or url in tested_links:
                    continue
                text = (anchor.inner_text() or "").strip()
                tested_links.add(url)
                result = test_single_link(page, current_page_url, url, text, "Header")
                report_rows.append(result)
                queue_internal(result, page_queue, queued_pages, tested_pages)

            print("\n[2] FULL PAGE SCROLL / CONTENT")
            scroll_full_page(page)
            for anchor in page.locator("a[href]").all():
                href = anchor.get_attribute("href")
                url = normalize_url(href, page.url)
                if not url or url in tested_links:
                    continue
                area = get_area(anchor)
                if area == "Footer":
                    continue
                text = (anchor.inner_text() or "").strip()
                tested_links.add(url)
                result = test_single_link(page, current_page_url, url, text, area)
                report_rows.append(result)
                queue_internal(result, page_queue, queued_pages, tested_pages)

            print("\n[3] FOOTER LINKS")
            for anchor in page.locator("footer a[href]").all():
                href = anchor.get_attribute("href")
                url = normalize_url(href, page.url)
                if not url or url in tested_links:
                    continue
                text = (anchor.inner_text() or "").strip()
                tested_links.add(url)
                result = test_single_link(page, current_page_url, url, text, "Footer")
                report_rows.append(result)
                queue_internal(result, page_queue, queued_pages, tested_pages)

        except Exception as exc:
            report_rows.append({
                "source_page": current_page_url,
                "area": "PAGE",
                "link_text": "",
                "url": current_page_url,
                "internal": is_internal(current_page_url),
                "status": 0,
                "final_url": "",
                "result": "FAIL",
                "error": str(exc),
            })
            print(f"PAGE ERROR: {exc}")

    write_report(report_rows)
    failures = [r for r in report_rows if r["result"] == "FAIL"]
    print("\n" + "=" * 100)
    print("THAURA.AI LINK CRAWLER TEST COMPLETED")
    print("=" * 100)
    print(f"Unique Pages Tested : {len(tested_pages)}")
    print(f"Unique Links Tested : {len(tested_links)}")
    print(f"PASS                : {len(report_rows) - len(failures)}")
    print(f"FAIL                : {len(failures)}")
    print(f"CSV Report          : {REPORT_FILE}")
    print("=" * 100)
    assert not failures, f"{len(failures)} broken/failed link(s) found. See {REPORT_FILE}"


def queue_internal(result, page_queue, queued_pages, tested_pages):
    if result["internal"] and result["status"] < 400:
        url = result["final_url"] or result["url"]
        url = normalize_url(url, BASE_URL)
        if url and url not in tested_pages and url not in queued_pages:
            page_queue.append(url)
            queued_pages.add(url)


def test_single_link(page, source_page, url, text, area):
    result = {
        "source_page": source_page,
        "area": area,
        "link_text": text,
        "url": url,
        "internal": is_internal(url),
        "status": 0,
        "final_url": "",
        "result": "FAIL",
        "error": "",
    }
    try:
        if urlparse(BASE_URL).scheme == "https" and urlparse(url).scheme == "http":
            result["error"] = "Mixed-content HTTP link"
            return result

        response = page.goto(url, wait_until="commit", timeout=30000)
        page.wait_for_timeout(1200)
        status = response.status if response else 0
        result["status"] = status
        result["final_url"] = page.url

        if status >= 400:
            result["error"] = f"HTTP {status}"
            return result
        result["result"] = "PASS"
        print(f"PASS | {area:<12} | {status:<3} | {text[:35]:<35} | {url}")
    except Exception as exc:
        result["error"] = str(exc)
        print(f"FAIL | {area:<12} | {url} | {exc}")
    finally:
        # Return to source page so the next link is tested from the same page.
        try:
            if page.url != source_page:
                page.goto(source_page, wait_until="commit", timeout=30000)
                page.wait_for_timeout(700)
        except Exception:
            pass
    return result


def write_report(rows):
    if not rows:
        return
    fieldnames = [
        "source_page", "area", "link_text", "url", "internal",
        "status", "final_url", "result", "error"
    ]
    with REPORT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
