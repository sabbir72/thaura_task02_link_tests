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

    description = page.locator('meta[name="description"]')

    # Exactly one meta description
    assert description.count() == 1, (
        f"{url}: Expected exactly 1 meta description, "
        f"found {description.count()}"
    )

    # Get content
    content = description.get_attribute("content")

    # Content must exist
    assert content is not None, (
        f"{url}: Meta description content attribute is missing"
    )

    # Content must not be empty
    assert content.strip() != "", (
        f"{url}: Meta description content is empty"
    )

    print(f"\nPASS: {url}")
    print(f"Meta Description: {content}")