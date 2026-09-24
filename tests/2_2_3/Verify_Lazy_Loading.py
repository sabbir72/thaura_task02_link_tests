import csv
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


PAGES = [
    ("Home", "https://thaura.ai/home"),
    ("Pricing", "https://thaura.ai/pricing"),
    ("API Platform", "https://thaura.ai/api-platform"),
    ("FAQ", "https://thaura.ai/faq"),
]

OUTPUT_CSV = Path("thaura_lazy_loading_report.csv")
OUTPUT_JSON = Path("thaura_lazy_loading_report.json")


def safe_getattr(locator, name):
    try:
        return locator.get_attribute(name)
    except Exception:
        return None


def collect_dom_images(page):
    """Collect img attributes/state from the current DOM."""
    return page.locator("img").evaluate_all(
        """
        imgs => imgs.map((img, index) => ({
            index: index,
            src: img.currentSrc || img.src || "",
            loading: img.getAttribute("loading"),
            widthAttr: img.getAttribute("width"),
            heightAttr: img.getAttribute("height"),
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            renderedWidth: Math.round(img.getBoundingClientRect().width),
            renderedHeight: Math.round(img.getBoundingClientRect().height),
            top: Math.round(img.getBoundingClientRect().top + window.scrollY),
            viewportVisible: (() => {
                const r = img.getBoundingClientRect();
                return r.bottom > 0 &&
                       r.top < window.innerHeight &&
                       r.right > 0 &&
                       r.left < window.innerWidth;
            })(),
            complete: img.complete,
        }))
        """
    )


def run():
    all_rows = []
    summary_rows = []

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

            # Keep request/response information for images only.
            response_records = []
            seen_response_urls = set()

            def handle_response(response):
                try:
                    request = response.request

                    if request.resource_type != "image":
                        return

                    url = response.url

                    # Keep first observed response per URL for clean reporting.
                    key = (url, response.status)
                    if key in seen_response_urls:
                        return

                    seen_response_urls.add(key)

                    response_records.append({
                        "url": url,
                        "status": response.status,
                        "content_type": response.headers.get("content-type", "N/A"),
                        "phase": "unknown",
                    })
                except Exception as exc:
                    print(f"[WARNING] Response capture error: {exc}")

            page.on("response", handle_response)

            try:
                # Start from top.
                page.goto(
                    page_url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                # Allow initial requests to settle, but DO NOT scroll yet.
                page.wait_for_timeout(3000)

                # Snapshot 1: DOM attributes/state before scroll.
                initial_dom = collect_dom_images(page)

                # Mark all currently captured image responses as initial-load responses.
                for item in response_records:
                    item["phase"] = "initial_load"

                initial_response_urls = {
                    item["url"] for item in response_records
                }

                print(f"[INFO] Initial image responses: {len(initial_response_urls)}")
                print(f"[INFO] <img> elements before scroll: {len(initial_dom)}")

                # Now scroll gradually to trigger lazy-loaded resources.
                print("[INFO] Scrolling page to trigger lazy-loaded images...")

                page.evaluate(
                    """
                    async () => {
                        const delay = ms =>
                            new Promise(resolve => setTimeout(resolve, ms));

                        const step = 500;
                        const maxHeight = Math.max(
                            document.body.scrollHeight,
                            document.documentElement.scrollHeight
                        );

                        for (let y = 0; y <= maxHeight; y += step) {
                            window.scrollTo(0, y);
                            await delay(300);
                        }

                        window.scrollTo(0, 0);
                    }
                    """
                )

                # Give newly-triggered image requests time to finish.
                page.wait_for_timeout(3000)

                # Mark requests observed after initial phase.
                for item in response_records:
                    if item["url"] in initial_response_urls:
                        continue
                    if item["phase"] == "unknown":
                        item["phase"] = "after_scroll"

                after_scroll_dom = collect_dom_images(page)

                after_scroll_urls = {
                    item["url"]
                    for item in response_records
                }

                new_after_scroll_urls = after_scroll_urls - initial_response_urls

                # Build lookup of DOM information by normalized src/currentSrc.
                dom_lookup = {}

                for dom in after_scroll_dom:
                    src = dom.get("src", "")
                    if src:
                        dom_lookup[src] = dom

                # Add DOM-only image information to rows.
                page_rows = []

                for item in response_records:
                    url = item["url"]
                    dom = dom_lookup.get(url, {})

                    row = {
                        "Page": page_name,
                        "Page URL": page_url,
                        "Image URL": url,
                        "Status": item["status"],
                        "Content-Type": item["content_type"],
                        "Load Phase": item["phase"],
                        "Requested After Scroll": (
                            "Yes" if url in new_after_scroll_urls else "No"
                        ),
                        "DOM loading Attribute": dom.get("loading") or "Not set / not matched",
                        "Natural Width": dom.get("naturalWidth", "N/A"),
                        "Natural Height": dom.get("naturalHeight", "N/A"),
                        "Rendered Width": dom.get("renderedWidth", "N/A"),
                        "Rendered Height": dom.get("renderedHeight", "N/A"),
                        "Viewport Visible After Scroll": dom.get(
                            "viewportVisible", "N/A"
                        ),
                        "Image Complete After Scroll": dom.get(
                            "complete", "N/A"
                        ),
                    }

                    page_rows.append(row)
                    all_rows.append(row)

                # DOM-level lazy summary.
                lazy_attr_count = sum(
                    1
                    for d in initial_dom
                    if str(d.get("loading", "")).lower() == "lazy"
                )

                total_img_elements = len(initial_dom)

                initial_urls = {
                    item["src"]
                    for item in initial_dom
                    if item.get("src")
                }

                images_not_initially_requested = sum(
                    1
                    for d in after_scroll_dom
                    if d.get("src")
                    and d.get("src") not in initial_urls
                )

                print(f"[INFO] Image requests after scroll: {len(new_after_scroll_urls)}")
                print(f"[INFO] DOM images with loading='lazy': {lazy_attr_count}")
                print(
                    f"[INFO] DOM images before scroll: "
                    f"{total_img_elements}"
                )

                for row in page_rows:
                    print(
                        f"{row['Status']:3} | "
                        f"{row['Load Phase']:13} | "
                        f"lazy={row['DOM loading Attribute']} | "
                        f"{row['Image URL']}"
                    )

                summary_rows.append({
                    "Page": page_name,
                    "Page URL": page_url,
                    "DOM Images Before Scroll": total_img_elements,
                    "Images With loading='lazy'": lazy_attr_count,
                    "Initial Image Requests": len(initial_urls),
                    "Total Image Responses": len(after_scroll_urls),
                    "New Image Requests After Scroll": len(new_after_scroll_urls),
                    "Images Loaded Only After Scroll (DOM comparison)": images_not_initially_requested,
                })

            except Exception as exc:
                print(f"[ERROR] Page execution failed: {exc}")

                summary_rows.append({
                    "Page": page_name,
                    "Page URL": page_url,
                    "DOM Images Before Scroll": "ERROR",
                    "Images With loading='lazy'": "ERROR",
                    "Initial Image Requests": "ERROR",
                    "Total Image Responses": "ERROR",
                    "New Image Requests After Scroll": "ERROR",
                    "Images Loaded Only After Scroll (DOM comparison)": "ERROR",
                })

            finally:
                page.close()

        browser.close()

    # Remove duplicate rows based on page + URL + phase.
    unique_rows = []
    seen = set()

    for row in all_rows:
        key = (
            row["Page"],
            row["Image URL"],
            row["Load Phase"],
        )

        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    # CSV report.
    fieldnames = [
        "Page",
        "Page URL",
        "Image URL",
        "Status",
        "Content-Type",
        "Load Phase",
        "Requested After Scroll",
        "DOM loading Attribute",
        "Natural Width",
        "Natural Height",
        "Rendered Width",
        "Rendered Height",
        "Viewport Visible After Scroll",
        "Image Complete After Scroll",
    ]

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    # JSON report.
    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "summary": summary_rows,
                "details": unique_rows,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 100)
    print("TC-PERF-09 TEST COMPLETED")
    print("=" * 100)

    print("\nSUMMARY")
    print("-" * 100)

    for row in summary_rows:
        lazy_count = row["Images With loading='lazy'"]
        initial_count = row["Initial Image Requests"]
        after_scroll_count = row["New Image Requests After Scroll"]

        print(
            f"{row['Page']:15} | "
            f"lazy={str(lazy_count):3} | "
            f"initial={str(initial_count):3} | "
            f"after_scroll={str(after_scroll_count):3}"
        )

    print(f"\nCSV : {OUTPUT_CSV.resolve()}")
    print(f"JSON: {OUTPUT_JSON.resolve()}")


if __name__ == "__main__":
    run()
