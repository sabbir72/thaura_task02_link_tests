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

OUTPUT_FILE = Path("thaura_image_payload_report.csv")


def get_extension(url: str) -> str:
    clean_url = url.split("?")[0].split("#")[0]

    match = re.search(r"\.([a-zA-Z0-9]+)$", clean_url)

    return match.group(1).lower() if match else "N/A"


def run_test():

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        for page_name, page_url in PAGES:

            print("\n" + "=" * 100)
            print(f"PAGE: {page_name}")
            print(f"URL : {page_url}")
            print("=" * 100)

            page = context.new_page()

            image_responses = []

            def handle_response(response):

                try:

                    request = response.request

                    if request.resource_type != "image":
                        return

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

                    # Get actual response body size
                    actual_size = "N/A"

                    try:
                        body = response.body()
                        actual_size = len(body)
                    except Exception:
                        pass

                    image_responses.append({
                        "Page": page_name,
                        "Page URL": page_url,
                        "Status": response.status,
                        "Resource Type": request.resource_type,
                        "Image URL": image_url,
                        "Extension": get_extension(image_url),
                        "Content-Type": content_type,
                        "Content-Length": content_length,
                        "Actual Response Size": actual_size,
                    })

                except Exception as e:

                    print(
                        f"[WARNING] Response processing error: {e}"
                    )

            page.on(
                "response",
                handle_response
            )

            print("[INFO] Loading page...")

            try:

                page.goto(
                    page_url,
                    wait_until="networkidle",
                    timeout=60000
                )

                page.wait_for_timeout(2000)

                # Scroll to trigger lazy-loaded images
                page.evaluate("""
                    async () => {

                        const delay = ms =>
                            new Promise(
                                resolve => setTimeout(resolve, ms)
                            );

                        const step = 500;

                        const height =
                            document.body.scrollHeight;

                        for (
                            let y = 0;
                            y < height;
                            y += step
                        ) {
                            window.scrollTo(0, y);
                            await delay(250);
                        }

                        window.scrollTo(0, 0);

                        await delay(1000);
                    }
                """)

                page.wait_for_timeout(2000)

            except Exception as e:

                print(
                    f"[ERROR] Page load failed: {e}"
                )

            # Collect image DOM dimensions
            dom_images = page.locator("img")

            try:

                count = dom_images.count()

            except Exception:

                count = 0

            dom_data = []

            for i in range(count):

                try:

                    img = dom_images.nth(i)

                    data = img.evaluate("""
                        img => ({
                            src: img.currentSrc || img.src,
                            naturalWidth: img.naturalWidth,
                            naturalHeight: img.naturalHeight,
                            renderedWidth: img.getBoundingClientRect().width,
                            renderedHeight: img.getBoundingClientRect().height
                        })
                    """)

                    dom_data.append(data)

                except Exception:

                    pass

            # Match DOM image data with network responses
            for item in image_responses:

                item["Natural Width"] = "N/A"
                item["Natural Height"] = "N/A"
                item["Rendered Width"] = "N/A"
                item["Rendered Height"] = "N/A"

                for dom in dom_data:

                    if dom["src"] == item["Image URL"]:

                        item["Natural Width"] = dom[
                            "naturalWidth"
                        ]

                        item["Natural Height"] = dom[
                            "naturalHeight"
                        ]

                        item["Rendered Width"] = round(
                            dom["renderedWidth"]
                        )

                        item["Rendered Height"] = round(
                            dom["renderedHeight"]
                        )

                        break

                # Optimization observation
                size = item["Actual Response Size"]

                if isinstance(size, int):

                    if size > 100 * 1024:
                        item["Large Image Candidate"] = "Yes"
                    else:
                        item["Large Image Candidate"] = "No"

                else:

                    item["Large Image Candidate"] = "Unknown"

            print(
                f"[INFO] Images detected: "
                f"{len(image_responses)}"
            )

            # Console output
            for item in image_responses:

                size = item["Actual Response Size"]

                if isinstance(size, int):

                    size_kb = round(
                        size / 1024,
                        2
                    )

                else:

                    size_kb = "N/A"

                print(
                    f"{item['Extension']:6} | "
                    f"{item['Status']:3} | "
                    f"{size_kb} KB | "
                    f"{item['Image URL']}"
                )

            results.extend(
                image_responses
            )

            page.close()

        browser.close()

    # Remove duplicates
    unique_results = []

    seen = set()

    for item in results:

        key = (
            item["Page"],
            item["Image URL"]
        )

        if key not in seen:

            seen.add(key)
            unique_results.append(item)

    # CSV
    fieldnames = [
        "Page",
        "Page URL",
        "Status",
        "Resource Type",
        "Image URL",
        "Extension",
        "Content-Type",
        "Content-Length",
        "Actual Response Size",
        "Natural Width",
        "Natural Height",
        "Rendered Width",
        "Rendered Height",
        "Large Image Candidate",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            unique_results
        )

    print("\n" + "=" * 100)
    print("TEST COMPLETED")
    print("=" * 100)

    print(
        f"Total unique images: "
        f"{len(unique_results)}"
    )

    print(
        f"CSV report: "
        f"{OUTPUT_FILE.resolve()}"
    )

    # Summary
    print("\nIMAGE SIZE SUMMARY")
    print("-" * 100)

    large_count = 0

    for item in unique_results:

        size = item["Actual Response Size"]

        if isinstance(size, int):

            size_kb = size / 1024

            if size > 100 * 1024:

                large_count += 1

                print(
                    f"[LARGE CANDIDATE] "
                    f"{item['Page']} | "
                    f"{round(size_kb, 2)} KB | "
                    f"{item['Image URL']}"
                )

    print(
        f"\nLarge image candidates: "
        f"{large_count}"
    )


if __name__ == "__main__":
    run_test()