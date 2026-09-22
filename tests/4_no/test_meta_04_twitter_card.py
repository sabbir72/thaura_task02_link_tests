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


TWITTER_TAGS = [
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
]


@pytest.mark.parametrize("url", PAGES)
def test_twitter_card_tags(page: Page, url):
    page.goto(url, wait_until="domcontentloaded")

    for tag in TWITTER_TAGS:
        locator = page.locator(f'meta[name="{tag}"]')

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

        print(f"{tag}: {content}")

    print(f"\nPASS: {url}")


def test_twitter_card_summary():
    """
    Final Summary
    """
    total = len(PAGES)

    # This test is only a summary marker.
    # Actual PASS/FAIL comes from the parametrized test above.
    print("\n" + "=" * 60)
    print("TC-META-04 TWITTER CARD SUMMARY")
    print("=" * 60)
    print(f"Total Pages Tested : {total}")
    print(f"Expected PASS      : {total}")
    print("FAIL               : 0  (if all parametrized tests pass)")
    print("=" * 60)