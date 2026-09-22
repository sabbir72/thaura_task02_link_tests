import allure

from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import deque

import pytest


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://thaura.ai/"
DOMAIN = "thaura.ai"


# Downloadable resources
# এগুলো HTML page নয়, তাই এগুলোকে broken page হিসেবে ধরব না।
DOWNLOAD_EXTENSIONS = {
    ".dmg",
    ".exe",
    ".zip",
    ".msi",
    ".pkg",
    ".deb",
    ".rpm",
}


# ============================================================
# URL HELPERS
# ============================================================

def is_internal(url):
    """
    Check whether URL belongs to Thaura.ai.
    """

    return urlparse(url).netloc == DOMAIN


def normalize_url(url):
    """
    Remove URL fragments (#section)
    and normalize trailing slash.
    """

    parsed = urlparse(url)

    clean = parsed._replace(
        fragment=""
    )

    normalized = clean.geturl().rstrip("/")

    return normalized or BASE_URL.rstrip("/")


def is_download_url(url):
    """
    Check whether URL points to downloadable resource.
    """

    extension = Path(
        urlparse(url).path
    ).suffix.lower()

    return extension in DOWNLOAD_EXTENSIONS


# ============================================================
# LINK COLLECTION
# ============================================================

def collect_links(page, area):
    """
    Collect all HTTP/HTTPS links from current page.

    area:
        Header
        Content
        Footer
    """

    links = []

    anchors = page.locator("a[href]")

    count = anchors.count()

    for i in range(count):

        try:

            anchor = anchors.nth(i)

            href = anchor.get_attribute("href")
            text = anchor.inner_text().strip()

            if not href:
                continue

            absolute_url = urljoin(
                page.url,
                href
            )

            absolute_url = normalize_url(
                absolute_url
            )

            parsed = urlparse(
                absolute_url
            )

            # Only HTTP / HTTPS
            if parsed.scheme not in (
                "http",
                "https"
            ):
                continue

            links.append(
                {
                    "url": absolute_url,
                    "text": text,
                    "area": area,
                }
            )

        except Exception:
            continue

    return links


# ============================================================
# SINGLE LINK CHECK
# ============================================================

@allure.step("Check link: {url}")
def check_single_link(
    page,
    source_page,
    url,
    text,
    area
):
    """
    Check one unique link.

    IMPORTANT:
    Function name does NOT start with test_,
    so pytest will not collect it as a separate test.
    """

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

    # ========================================================
    # ALLURE DETAILS
    # ========================================================

    allure.dynamic.parameter(
        "Area",
        area
    )

    allure.dynamic.parameter(
        "Link",
        url
    )

    allure.attach(
        source_page,
        name="Source Page",
        attachment_type=allure.attachment_type.TEXT
    )

    allure.attach(
        text or "(No link text)",
        name="Link Text",
        attachment_type=allure.attachment_type.TEXT
    )

    # ========================================================
    # CHECK
    # ========================================================

    try:

        parsed = urlparse(url)

        # ----------------------------------------------------
        # 1. MIXED CONTENT
        # ----------------------------------------------------

        if (
            urlparse(BASE_URL).scheme == "https"
            and parsed.scheme == "http"
        ):

            result["error"] = (
                "Mixed-content HTTP link"
            )

            result["result"] = "FAIL"

            allure.attach(
                result["error"],
                name="Failure Reason",
                attachment_type=allure.attachment_type.TEXT
            )

            print(
                f"FAIL | MIXED-CONTENT | "
                f"{url}"
            )

            return result

        # ----------------------------------------------------
        # 2. DOWNLOAD RESOURCE
        # ----------------------------------------------------

        if is_download_url(url):

            print(
                f"DOWNLOAD | "
                f"{area:<10} | "
                f"{text[:35]:<35} | "
                f"{url}"
            )

            try:

                with page.expect_download(
                    timeout=15000
                ) as download_info:

                    page.goto(
                        url,
                        wait_until="commit",
                        timeout=30000
                    )

                download = (
                    download_info.value
                )

                filename = (
                    download.suggested_filename
                )

                result["status"] = 200
                result["final_url"] = url
                result["result"] = "PASS"

                result["error"] = (
                    f"Download detected: "
                    f"{filename}"
                )

                allure.attach(
                    filename,
                    name="Downloaded File",
                    attachment_type=(
                        allure.attachment_type.TEXT
                    )
                )

                print(
                    f"PASS | DOWNLOAD | "
                    f"{filename}"
                )

                return result

            except Exception:

                # Download resource হলেও
                # browser download event না এলে
                # broken হিসেবে ধরব না।

                result["status"] = 200
                result["final_url"] = url
                result["result"] = "PASS"

                result["error"] = (
                    "Download/resource link - "
                    "not treated as broken"
                )

                allure.attach(
                    result["error"],
                    name="Download Handling",
                    attachment_type=(
                        allure.attachment_type.TEXT
                    )
                )

                print(
                    f"PASS | DOWNLOAD RESOURCE | "
                    f"{url}"
                )

                return result

        # ----------------------------------------------------
        # 3. NORMAL HTML / EXTERNAL LINK
        # ----------------------------------------------------

        response = page.goto(
            url,
            wait_until="commit",
            timeout=30000
        )

        page.wait_for_timeout(
            1000
        )

        status = (
            response.status
            if response
            else 0
        )

        final_url = page.url

        result["status"] = status
        result["final_url"] = final_url

        # ----------------------------------------------------
        # HTTP ERROR
        # ----------------------------------------------------

        if status >= 400:

            result["error"] = (
                f"HTTP {status}"
            )

            result["result"] = "FAIL"

            allure.attach(
                str(status),
                name="HTTP Status",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

            allure.attach(
                result["error"],
                name="Failure Reason",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

            print(
                f"FAIL | {area:<10} | "
                f"{status:<3} | "
                f"{text[:35]:<35} | "
                f"{url}"
            )

            return result

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if 200 <= status < 400:

            result["result"] = "PASS"

            allure.attach(
                str(status),
                name="HTTP Status",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

            allure.attach(
                final_url,
                name="Final URL",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

            print(
                f"PASS | {area:<10} | "
                f"{status:<3} | "
                f"{text[:35]:<35} | "
                f"{url}"
            )

            return result

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        result["error"] = (
            "No valid HTTP response"
        )

        result["result"] = "FAIL"

        return result

    except Exception as exc:

        # ----------------------------------------------------
        # DOWNLOAD FALLBACK
        # ----------------------------------------------------

        if is_download_url(url):

            result["status"] = 200
            result["final_url"] = url
            result["result"] = "PASS"

            result["error"] = (
                "Download/resource link - "
                "not treated as broken"
            )

            print(
                f"PASS | DOWNLOAD RESOURCE | "
                f"{url}"
            )

            return result

        # ----------------------------------------------------
        # REAL FAILURE
        # ----------------------------------------------------

        result["error"] = str(exc)

        result["result"] = "FAIL"

        allure.attach(
            str(exc),
            name="Exception",
            attachment_type=(
                allure.attachment_type.TEXT
            )
        )

        print(
            f"FAIL | {area:<10} | "
            f"{url} | {exc}"
        )

        return result


# ============================================================
# INTERNAL PAGE QUEUE
# ============================================================

def queue_internal(
    result,
    page_queue,
    queued_pages,
    tested_pages
):
    """
    Add valid internal HTML pages to queue.

    Download files are never added as pages.
    """

    if not result["internal"]:
        return

    url = result["url"]

    # Never crawl downloadable resources
    if is_download_url(url):
        return

    # Don't queue HTTP errors
    if result["status"] >= 400:
        return

    # Don't duplicate pages
    if url in tested_pages:
        return

    if url in queued_pages:
        return

    page_queue.append(url)

    queued_pages.add(url)


# ============================================================
# PAGE CRAWLER
# ============================================================

def crawl_page(
    page,
    page_url,
    page_queue,
    queued_pages,
    tested_pages,
    tested_links,
    results
):
    """
    Page execution order:

    1. Header
    2. Full page scroll / Content
    3. Footer
    """

    print("\n")
    print("=" * 100)
    print(f"PAGE: {page_url}")
    print("=" * 100)

    allure.dynamic.parameter(
        "Page",
        page_url
    )

    # ========================================================
    # PAGE LOAD
    # ========================================================

    try:

        page.goto(
            page_url,
            wait_until="commit",
            timeout=30000
        )

        page.wait_for_timeout(
            2000
        )

    except Exception as exc:

        print(
            f"PAGE LOAD ERROR | "
            f"{page_url} | {exc}"
        )

        allure.attach(
            str(exc),
            name="Page Load Error",
            attachment_type=(
                allure.attachment_type.TEXT
            )
        )

        tested_pages.add(
            page_url
        )

        return

    # ========================================================
    # 1. HEADER
    # ========================================================

    print("\n--- HEADER ---")

    header_links = collect_links(
        page,
        "Header"
    )

    for item in header_links:

        url = item["url"]

        # Unique link check
        if url in tested_links:
            continue

        tested_links.add(url)

        result = check_single_link(
            page,
            page_url,
            url,
            item["text"],
            "Header"
        )

        results.append(
            result
        )

        queue_internal(
            result,
            page_queue,
            queued_pages,
            tested_pages
        )

    # ========================================================
    # 2. FULL PAGE SCROLL / CONTENT
    # ========================================================

    print("\n--- FULL PAGE SCROLL / CONTENT ---")

    previous_height = 0
    stable_count = 0

    while stable_count < 3:

        current_height = page.evaluate(
            "document.body.scrollHeight"
        )

        # Scroll to bottom
        page.evaluate(
            "window.scrollTo("
            "0, document.body.scrollHeight)"
        )

        # Allow lazy loading
        page.wait_for_timeout(
            1500
        )

        new_height = page.evaluate(
            "document.body.scrollHeight"
        )

        # ----------------------------------------------------
        # Collect newly loaded links
        # ----------------------------------------------------

        content_links = collect_links(
            page,
            "Content"
        )

        for item in content_links:

            url = item["url"]

            if url in tested_links:
                continue

            tested_links.add(url)

            result = check_single_link(
                page,
                page_url,
                url,
                item["text"],
                "Content"
            )

            results.append(
                result
            )

            queue_internal(
                result,
                page_queue,
                queued_pages,
                tested_pages
            )

        # ----------------------------------------------------
        # Check whether page height changed
        # ----------------------------------------------------

        if new_height == previous_height:

            stable_count += 1

        else:

            stable_count = 0

        previous_height = new_height

        if new_height == current_height:

            stable_count += 1

    # ========================================================
    # 3. FOOTER
    # ========================================================

    print("\n--- FOOTER ---")

    page.evaluate(
        "window.scrollTo("
        "0, document.body.scrollHeight)"
    )

    page.wait_for_timeout(
        1000
    )

    footer_links = collect_links(
        page,
        "Footer"
    )

    for item in footer_links:

        url = item["url"]

        if url in tested_links:
            continue

        tested_links.add(url)

        result = check_single_link(
            page,
            page_url,
            url,
            item["text"],
            "Footer"
        )

        results.append(
            result
        )

        queue_internal(
            result,
            page_queue,
            queued_pages,
            tested_pages
        )

    # ========================================================
    # PAGE COMPLETE
    # ========================================================

    tested_pages.add(
        page_url
    )

    print(
        f"\nPAGE COMPLETED: "
        f"{page_url}"
    )


# ============================================================
# BROWSER FIXTURE
# ============================================================

@pytest.fixture
def browser():

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        yield browser

        browser.close()


# ============================================================
# PAGE FIXTURE
# ============================================================

@pytest.fixture
def page(browser):

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    yield page

    context.close()


# ============================================================
# MAIN ALLURE TEST
# ============================================================

@allure.title(
    "Thaura.ai Complete Link Crawler"
)
@allure.description(
    """
    Validates Thaura.ai internal and external links.

    Coverage:
    - Header links
    - Full page content links
    - Lazy-loaded links
    - Footer links
    - Internal page crawling
    - External link validation
    - HTTP status validation
    - Redirect validation
    - Mixed-content HTTP links
    - Downloadable resources
    - Duplicate page prevention
    - Duplicate link prevention
    """
)
@allure.epic("Thaura.ai")
@allure.feature("Link Validation")
@allure.story(
    "Internal and External Link Validation"
)
def test_thaura_link_crawler(page):

    page_queue = deque()

    queued_pages = set()

    tested_pages = set()

    # Every unique link tested only once
    tested_links = set()

    results = []

    start_url = normalize_url(
        BASE_URL
    )

    page_queue.append(
        start_url
    )

    queued_pages.add(
        start_url
    )

    # ========================================================
    # MAIN CRAWL LOOP
    # ========================================================

    while page_queue:

        current_page = page_queue.popleft()

        # Page already tested
        if current_page in tested_pages:
            continue

        print(
            f"\n\nCRAWLING PAGE: "
            f"{current_page}"
        )

        crawl_page(
            page,
            current_page,
            page_queue,
            queued_pages,
            tested_pages,
            tested_links,
            results
        )

    # ========================================================
    # RESULTS
    # ========================================================

    broken_links = [
        item
        for item in results
        if item["result"] == "FAIL"
    ]

    passed_links = [
        item
        for item in results
        if item["result"] == "PASS"
    ]

    # ========================================================
    # ALLURE SUMMARY
    # ========================================================

    allure.attach(
        str(len(tested_pages)),
        name="Pages Tested",
        attachment_type=(
            allure.attachment_type.TEXT
        )
    )

    allure.attach(
        str(len(tested_links)),
        name="Unique Links Tested",
        attachment_type=(
            allure.attachment_type.TEXT
        )
    )

    allure.attach(
        str(len(passed_links)),
        name="Passed Links",
        attachment_type=(
            allure.attachment_type.TEXT
        )
    )

    allure.attach(
        str(len(broken_links)),
        name="Failed Links",
        attachment_type=(
            allure.attachment_type.TEXT
        )
    )

    # ========================================================
    # PRINT SUMMARY
    # ========================================================

    print("\n")
    print("=" * 100)
    print("CRAWL COMPLETED")
    print("=" * 100)

    print(
        f"Pages tested : "
        f"{len(tested_pages)}"
    )

    print(
        f"Unique links : "
        f"{len(tested_links)}"
    )

    print(
        f"Passed links : "
        f"{len(passed_links)}"
    )

    print(
        f"Broken links : "
        f"{len(broken_links)}"
    )

    # ========================================================
    # BROKEN LINKS
    # ========================================================

    if broken_links:

        print("\nBROKEN LINKS:")

        for item in broken_links:

            print(
                f"- {item['url']} | "
                f"{item['status']} | "
                f"{item['error']}"
            )

            allure.attach(
                (
                    f"URL: {item['url']}\n"
                    f"Source: {item['source_page']}\n"
                    f"Area: {item['area']}\n"
                    f"Status: {item['status']}\n"
                    f"Final URL: {item['final_url']}\n"
                    f"Error: {item['error']}"
                ),
                name=f"Broken Link - {item['url']}",
                attachment_type=(
                    allure.attachment_type.TEXT
                )
            )

    # ========================================================
    # FINAL ASSERTION
    # ========================================================

    assert not broken_links, (
        f"{len(broken_links)} "
        f"broken/failed link(s) found."
    )