import csv
import re
from pathlib import Path
from playwright.sync_api import sync_playwright


PAGES = [
    ("Home", "https://thaura.ai/home"),
    ("Pricing", "https://thaura.ai/pricing"),
    ("API Platform", "https://thaura.ai/api-platform"),
    ("FAQ", "https://thaura.ai/faq"),
]

OUTPUT_FILE = Path("thaura_image_report.csv")


def get_extension(url: str) -> str:
    """
    Extract file extension from image URL.
    """
    clean_url = url.split("?")[0].split("#")[0]

    match = re.search(r"\.([a-zA-Z0-9]+)$", clean_url)

    if match:
        return match.group(1).lower()

    return "N/A"


def run_test():
    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": 1440, "height": 900}
        )

        for page_name, page_url in PAGES:

            print("\n" + "=" * 100)
            print(f"PAGE: {page_name}")
            print(f"URL : {page_url}")
            print("=" * 100)

            page = context.new_page()

            page_images = []

            def handle_response(response):
                try:
                    request = response.request

                    # Playwright identifies image network resources
                    if request.resource_type == "image":

                        headers = response.all_headers()

                        content_type = headers.get(
                            "content-type",
                            "N/A"
                        )

                        content_length = headers.get(
                            "content-length",
                            "N/A"
                        )

                        image_url = response.url

                        extension = get_extension(image_url)

                        data = {
                            "Page": page_name,
                            "Page URL": page_url,
                            "Status": response.status,
                            "Resource Type": request.resource_type,
                            "Image URL": image_url,
                            "Extension": extension,
                            "Content-Type": content_type,
                            "Content-Length": content_length,
                        }

                        page_images.append(data)

                except Exception as e:
                    print(f"[WARN] Could not process response: {e}")

            page.on("response", handle_response)

            print("[INFO] Opening page...")

            try:
                page.goto(
                    page_url,
                    wait_until="networkidle",
                    timeout=60000
                )

                # Extra wait for lazy-loaded resources
                page.wait_for_timeout(3000)

                # Scroll to trigger lazy-loaded images
                page.evaluate("""
                    async () => {
                        const delay = ms =>
                            new Promise(resolve => setTimeout(resolve, ms));

                        const step = 500;
                        const maxHeight = document.body.scrollHeight;

                        for (let y = 0; y < maxHeight; y += step) {
                            window.scrollTo(0, y);
                            await delay(300);
                        }

                        window.scrollTo(0, 0);
                    }
                """)

                page.wait_for_timeout(3000)

            except Exception as e:
                print(f"[ERROR] Page load failed: {e}")

            print(
                f"[INFO] Images detected: {len(page_images)}"
            )

            for image in page_images:

                print(
                    f"{image['Extension']:8} | "
                    f"{image['Content-Type']:25} | "
                    f"{image['Status']:3} | "
                    f"{image['Image URL']}"
                )

            results.extend(page_images)

            page.close()

        browser.close()

    # Remove duplicates
    unique_results = []

    seen = set()

    for item in results:

        key = (
            item["Page"],
            item["Image URL"],
        )

        if key not in seen:
            seen.add(key)
            unique_results.append(item)

    # Write CSV
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        fieldnames = [
            "Page",
            "Page URL",
            "Status",
            "Resource Type",
            "Image URL",
            "Extension",
            "Content-Type",
            "Content-Length",
        ]

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(unique_results)

    print("\n" + "=" * 100)
    print("TEST COMPLETED")
    print("=" * 100)

    print(f"Total unique images: {len(unique_results)}")
    print(f"Report generated   : {OUTPUT_FILE.resolve()}")

    # Format summary
    format_count = {}

    for item in unique_results:

        ext = item["Extension"]

        if ext not in format_count:
            format_count[ext] = 0

        format_count[ext] += 1

    print("\nFORMAT SUMMARY")
    print("-" * 50)

    for ext, count in sorted(format_count.items()):
        print(f"{ext:10} : {count}")


if __name__ == "__main__":
    run_test()