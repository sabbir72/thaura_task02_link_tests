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
def test_metadata_consistency(page: Page, url):
    page.goto(url, wait_until="domcontentloaded")

    expected_url = url.rstrip("/")

    # -------------------------------------------------
    # 1. Page Title
    # -------------------------------------------------
    title = page.title()

    assert title.strip() != "", (
        f"{url}: Page title is empty"
    )

    # -------------------------------------------------
    # 2. Meta Description
    # -------------------------------------------------
    description = page.locator('meta[name="description"]')

    assert description.count() == 1, (
        f"{url}: Expected 1 meta description, "
        f"found {description.count()}"
    )

    description_content = description.get_attribute("content")

    assert description_content and description_content.strip(), (
        f"{url}: Meta description is empty"
    )

    # -------------------------------------------------
    # 3. Open Graph Title
    # -------------------------------------------------
    og_title = page.locator('meta[property="og:title"]')

    assert og_title.count() == 1, (
        f"{url}: Expected 1 og:title, "
        f"found {og_title.count()}"
    )

    og_title_content = og_title.get_attribute("content")

    assert og_title_content and og_title_content.strip(), (
        f"{url}: og:title is empty"
    )

    # -------------------------------------------------
    # 4. Open Graph Description
    # -------------------------------------------------
    og_description = page.locator(
        'meta[property="og:description"]'
    )

    assert og_description.count() == 1, (
        f"{url}: Expected 1 og:description, "
        f"found {og_description.count()}"
    )

    og_description_content = og_description.get_attribute("content")

    assert og_description_content and og_description_content.strip(), (
        f"{url}: og:description is empty"
    )

    # -------------------------------------------------
    # 5. Open Graph URL
    # -------------------------------------------------
    og_url = page.locator('meta[property="og:url"]')

    assert og_url.count() == 1, (
        f"{url}: Expected 1 og:url, "
        f"found {og_url.count()}"
    )

    og_url_content = og_url.get_attribute("content")

    assert og_url_content and og_url_content.strip(), (
        f"{url}: og:url is empty"
    )

    actual_og_url = og_url_content.rstrip("/")

    assert actual_og_url == expected_url, (
        f"{url}: og:url mismatch | "
        f"Expected: {expected_url} | "
        f"Actual: {og_url_content}"
    )

    # -------------------------------------------------
    # 6. Twitter Title
    # -------------------------------------------------
    twitter_title = page.locator(
        'meta[name="twitter:title"]'
    )

    assert twitter_title.count() == 1, (
        f"{url}: Expected 1 twitter:title, "
        f"found {twitter_title.count()}"
    )

    twitter_title_content = twitter_title.get_attribute("content")

    assert twitter_title_content and twitter_title_content.strip(), (
        f"{url}: twitter:title is empty"
    )

    # -------------------------------------------------
    # 7. Twitter Description
    # -------------------------------------------------
    twitter_description = page.locator(
        'meta[name="twitter:description"]'
    )

    assert twitter_description.count() == 1, (
        f"{url}: Expected 1 twitter:description, "
        f"found {twitter_description.count()}"
    )

    twitter_description_content = twitter_description.get_attribute(
        "content"
    )

    assert (
        twitter_description_content
        and twitter_description_content.strip()
    ), (
        f"{url}: twitter:description is empty"
    )

    # -------------------------------------------------
    # Page Result
    # -------------------------------------------------
    print(f"\nPASS: {url}")
    print(f"Title: {title}")
    print(f"Description: {description_content}")
    print(f"OG Title: {og_title_content}")
    print(f"OG URL: {og_url_content}")
    print(f"Twitter Title: {twitter_title_content}")


# =====================================================
# SUMMARY
# =====================================================

def test_metadata_consistency_summary():
    print("\n" + "=" * 70)
    print("TC-META-05 METADATA CONSISTENCY SUMMARY")
    print("=" * 70)
    print(f"Total Pages Tested : {len(PAGES)}")
    print("PASS / FAIL        : Shown in pytest results above")
    print("=" * 70)