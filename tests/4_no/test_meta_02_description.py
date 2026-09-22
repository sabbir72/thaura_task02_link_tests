import pytest
from playwright.sync_api import Page


PAGES = [
    "https://thaura.ai/home",
    "https://thaura.ai/story",
    "https://thaura.ai/constitution",
    "https://thaura.ai/pricing",
    "https://thaura.ai/community",
    "https://thaura.ai/contact",
    "https://thaura.ai/careers",
    "https://thaura.ai/faq",
    "https://thaura.ai/api-platform",
    "https://thaura.ai/donate",
    "https://thaura.ai/download",
    "https://thaura.ai/terms-of-service",
    "https://thaura.ai/privacy-policy",
    "https://thaura.ai/data-processing-addendum",
    "https://thaura.ai/imprint",
]


@pytest.mark.parametrize("url", PAGES)
def test_meta_description(page: Page, url):

    page.goto(url, wait_until="domcontentloaded")

    description = page.locator(
        'meta[name="description"]'
    )

    assert description.count() == 1, (
        f"{url}: Expected exactly 1 meta description, "
        f"found {description.count()}"
    )

    content = description.get_attribute("content")

    assert content is not None, (
        f"{url}: Meta description content "
        f"attribute is missing"
    )

    assert content.strip() != "", (
        f"{url}: Meta description content is empty"
    )

    print(f"\nPASS: {url}")
    print(f"Meta Description: {content}")


# ==========================================================
# SUMMARY
# ==========================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):

    reports = terminalreporter.getreports("call")

    passed = sum(
        1 for report in reports
        if report.passed
    )

    failed = sum(
        1 for report in reports
        if report.failed
    )

    skipped = sum(
        1 for report in reports
        if report.skipped
    )

    total = passed + failed + skipped

    print("\n")
    print("=" * 70)
    print("TC-META-02 META DESCRIPTION SUMMARY")
    print("=" * 70)
    print(f"Total Pages Tested : {total}")
    print(f"PASS               : {passed}")
    print(f"FAIL               : {failed}")
    print(f"SKIPPED            : {skipped}")
    print("=" * 70)

    if failed == 0:
        print("FINAL RESULT       : PASS")
    else:
        print("FINAL RESULT       : FAIL")

    print("=" * 70)