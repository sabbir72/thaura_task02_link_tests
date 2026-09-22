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


OG_TAGS = [
    "og:title",
    "og:description",
    "og:url",
    "og:image",
]


@pytest.mark.parametrize("url", PAGES)
def test_open_graph_tags(page: Page, url):
    page.goto(url, wait_until="domcontentloaded")

    expected_url = url.rstrip("/")

    for tag in OG_TAGS:
        locator = page.locator(f'meta[property="{tag}"]')

        # Exactly one tag
        assert locator.count() == 1, (
            f"{url}: Expected exactly 1 {tag}, "
            f"found {locator.count()}"
        )

        # Get content
        content = locator.get_attribute("content")

        # Content must exist
        assert content is not None, (
            f"{url}: {tag} content attribute is missing"
        )

        # Content must not be empty
        assert content.strip() != "", (
            f"{url}: {tag} content is empty"
        )

        # og:url must match current page
        if tag == "og:url":
            actual_url = content.rstrip("/")

            assert actual_url == expected_url, (
                f"{url}: og:url mismatch | "
                f"Expected: {expected_url} | "
                f"Actual: {content}"
            )

        print(f"{tag}: {content}")

    print(f"\nPASS: {url}")