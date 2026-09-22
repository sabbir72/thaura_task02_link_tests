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
def test_canonical_url(page: Page, url):
    page.goto(url, wait_until="domcontentloaded")

    canonical = page.locator('link[rel="canonical"]')

    # Exactly one canonical tag
    assert canonical.count() == 1, (
        f"{url}: Expected exactly 1 canonical tag, "
        f"but found {canonical.count()}"
    )

    canonical_url = canonical.get_attribute("href")

    # Canonical must exist
    assert canonical_url, f"{url}: Canonical href is empty"

    # Canonical must use HTTPS
    assert canonical_url.startswith("https://"), (
        f"{url}: Canonical URL is not HTTPS: {canonical_url}"
    )

    # Normalize trailing slash for comparison
    expected_url = url.rstrip("/")
    actual_url = canonical_url.rstrip("/")

    assert actual_url == expected_url, (
        f"{url}: Canonical mismatch. "
        f"Expected: {expected_url}, Actual: {canonical_url}"
    )

    print(f"\nPASS: {url}")
    print(f"Canonical: {canonical_url}")