import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


PAGES = [
    ("Home", "https://thaura.ai/home"),
    ("Pricing", "https://thaura.ai/pricing"),
    ("API Platform", "https://thaura.ai/api-platform"),
    ("FAQ", "https://thaura.ai/faq"),
]

OUTPUT_CSV = Path("thaura_video_optimization_report.csv")
OUTPUT_JSON = Path("thaura_video_optimization_report.json")

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".ogg",
    ".mov",
    ".m4v",
)


def is_video_url(url: str) -> bool:
    path = urlsplit(url).path.lower()
    return path.endswith(VIDEO_EXTENSIONS)


def bytes_to_kb(value):
    if isinstance(value, int):
        return round(value / 1024, 2)
    return "N/A"


def collect_video_dom(page):
    return page.locator("video").evaluate_all(
        """
        videos => videos.map((video, index) => ({
            index: index,

            src: video.getAttribute("src") || "",

            currentSrc: video.currentSrc || "",

            poster: video.getAttribute("poster") || "",

            preload: video.getAttribute("preload") || "auto",

            autoplay: video.hasAttribute("autoplay"),

            muted: video.muted,

            controls: video.hasAttribute("controls"),

            loop: video.hasAttribute("loop"),

            playsInline: video.hasAttribute("playsinline"),

            widthAttr: video.getAttribute("width") || "",

            heightAttr: video.getAttribute("height") || "",

            renderedWidth: Math.round(
                video.getBoundingClientRect().width
            ),

            renderedHeight: Math.round(
                video.getBoundingClientRect().height
            ),

            readyState: video.readyState,

            networkState: video.networkState,

            duration:
                Number.isFinite(video.duration)
                ? Number(video.duration.toFixed(3))
                : null
        }))
        """
    )


def run_test():

    all_rows = []
    summary_rows = []

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

            print("\n" + "=" * 110)

            print(f"PAGE: {page_name}")

            print(f"URL : {page_url}")

            print("=" * 110)

            page = context.new_page()

            video_requests = {}

            failed_requests = []

            # --------------------------------------------------
            # Capture completed video/media requests
            # --------------------------------------------------

            def handle_request_finished(request):

                try:

                    url = request.url

                    is_video = (
                        request.resource_type == "media"
                        or is_video_url(url)
                    )

                    if not is_video:
                        return

                    response = request.response()

                    if response is None:
                        return

                    # Playwright Chromium request.sizes()
                    # gives encoded response body size.
                    sizes = request.sizes()

                    timing = request.timing

                    video_requests[url] = {
                        "url": url,

                        "status": response.status,

                        "content_type": (
                            response.header_value(
                                "content-type"
                            )
                            or "N/A"
                        ),

                        "content_length": (
                            response.header_value(
                                "content-length"
                            )
                            or "N/A"
                        ),

                        "response_body_size": (
                            sizes.get(
                                "responseBodySize"
                            )
                            if sizes
                            else "N/A"
                        ),

                        "request_headers_size": (
                            sizes.get(
                                "requestHeadersSize"
                            )
                            if sizes
                            else "N/A"
                        ),

                        "response_headers_size": (
                            sizes.get(
                                "responseHeadersSize"
                            )
                            if sizes
                            else "N/A"
                        ),

                        "request_start": (
                            timing.get(
                                "requestStart"
                            )
                            if timing
                            else -1
                        ),

                        "response_start": (
                            timing.get(
                                "responseStart"
                            )
                            if timing
                            else -1
                        ),

                        "response_end": (
                            timing.get(
                                "responseEnd"
                            )
                            if timing
                            else -1
                        ),
                    }

                except Exception as exc:

                    print(
                        "[WARNING] "
                        f"requestfinished error: {exc}"
                    )

            page.on(
                "requestfinished",
                handle_request_finished
            )

            # --------------------------------------------------
            # Capture failed media requests
            # --------------------------------------------------

            def handle_request_failed(request):

                try:

                    url = request.url

                    is_video = (
                        request.resource_type == "media"
                        or is_video_url(url)
                    )

                    if is_video:

                        failed_requests.append({
                            "url": url,
                            "failure": request.failure,
                        })

                except Exception:
                    pass

            page.on(
                "requestfailed",
                handle_request_failed
            )

            try:

                print("[INFO] Loading page...")

                page.goto(
                    page_url,
                    wait_until="load",
                    timeout=60000
                )

                # Allow media metadata/network activity
                # to settle.
                page.wait_for_timeout(5000)

                # --------------------------------------------------
                # Collect video DOM information
                # --------------------------------------------------

                videos = collect_video_dom(page)

                print(
                    f"[INFO] Video elements found: "
                    f"{len(videos)}"
                )

                print(
                    f"[INFO] Video/media requests: "
                    f"{len(video_requests)}"
                )

                page_rows = []

                for video in videos:

                    source_url = (
                        video["currentSrc"]
                        or video["src"]
                    )

                    matched_request = None

                    # Match video DOM source with
                    # network request.
                    for request_url, request_data in (
                        video_requests.items()
                    ):

                        if not source_url:
                            continue

                        source_path = (
                            urlsplit(source_url).path
                        )

                        request_path = (
                            urlsplit(request_url).path
                        )

                        if (
                            source_url == request_url
                            or source_path == request_path
                        ):
                            matched_request = request_data
                            break

                    # --------------------------------------------------
                    # Optimization observations
                    # --------------------------------------------------

                    observations = []

                    preload = (
                        video["preload"]
                        or "auto"
                    ).lower()

                    if preload == "metadata":

                        observations.append(
                            "preload=metadata"
                        )

                    elif preload == "none":

                        observations.append(
                            "preload=none"
                        )

                    elif preload == "auto":

                        observations.append(
                            "preload=auto; "
                            "review whether early media loading is necessary"
                        )

                    if video["poster"]:

                        observations.append(
                            "poster configured"
                        )

                    else:

                        observations.append(
                            "poster not configured"
                        )

                    response_size = "N/A"

                    if matched_request:

                        response_size = (
                            matched_request[
                                "response_body_size"
                            ]
                        )

                    if isinstance(
                        response_size,
                        int
                    ):

                        if response_size > 5_000_000:

                            observations.append(
                                "response size > 5 MB"
                            )

                        elif response_size > 1_000_000:

                            observations.append(
                                "response size > 1 MB"
                            )

                    if video["autoplay"]:

                        observations.append(
                            "autoplay enabled"
                        )

                    # --------------------------------------------------
                    # Calculate loading time
                    # --------------------------------------------------

                    loading_time_ms = "N/A"

                    if matched_request:

                        start = matched_request[
                            "request_start"
                        ]

                        end = matched_request[
                            "response_end"
                        ]

                        if (
                            isinstance(start, (int, float))
                            and isinstance(end, (int, float))
                            and start >= 0
                            and end >= 0
                            and end >= start
                        ):

                            loading_time_ms = round(
                                end - start,
                                2
                            )

                    row = {

                        "Page": page_name,

                        "Page URL": page_url,

                        "Video Index": video["index"],

                        "Video Source":
                            source_url or "N/A",

                        "Poster":
                            video["poster"] or "N/A",

                        "Preload":
                            video["preload"],

                        "Autoplay":
                            video["autoplay"],

                        "Muted":
                            video["muted"],

                        "Controls":
                            video["controls"],

                        "Loop":
                            video["loop"],

                        "Playsinline":
                            video["playsInline"],

                        "Width Attribute":
                            video["widthAttr"],

                        "Height Attribute":
                            video["heightAttr"],

                        "Rendered Width":
                            video["renderedWidth"],

                        "Rendered Height":
                            video["renderedHeight"],

                        "Ready State":
                            video["readyState"],

                        "Network State":
                            video["networkState"],

                        "Duration (sec)":
                            video["duration"],

                        "HTTP Status":
                            (
                                matched_request["status"]
                                if matched_request
                                else "N/A"
                            ),

                        "Content-Type":
                            (
                                matched_request[
                                    "content_type"
                                ]
                                if matched_request
                                else "N/A"
                            ),

                        "Content-Length":
                            (
                                matched_request[
                                    "content_length"
                                ]
                                if matched_request
                                else "N/A"
                            ),

                        "Response Body Size (bytes)":
                            response_size,

                        "Response Body Size (KB)":
                            bytes_to_kb(
                                response_size
                            ),

                        "Loading Time (ms)":
                            loading_time_ms,

                        "Optimization Observation":
                            "; ".join(
                                observations
                            ),
                    }

                    page_rows.append(row)

                    all_rows.append(row)

                    print(
                        f"[VIDEO {video['index']}] "
                        f"src={source_url or 'N/A'} | "
                        f"preload={video['preload']} | "
                        f"poster="
                        f"{'Yes' if video['poster'] else 'No'} | "
                        f"status="
                        f"{row['HTTP Status']} | "
                        f"type="
                        f"{row['Content-Type']} | "
                        f"size="
                        f"{row['Response Body Size (KB)']} KB | "
                        f"load="
                        f"{row['Loading Time (ms)']} ms"
                    )

                # --------------------------------------------------
                # Summary
                # --------------------------------------------------

                summary_rows.append({

                    "Page": page_name,

                    "Page URL": page_url,

                    "Video Elements":
                        len(videos),

                    "Video Requests":
                        len(video_requests),

                    "Failed Video Requests":
                        len(failed_requests),

                    "Videos With Poster":
                        sum(
                            1
                            for v in videos
                            if v["poster"]
                        ),

                    "preload=metadata":
                        sum(
                            1
                            for v in videos
                            if (
                                v["preload"]
                                .lower()
                                == "metadata"
                            )
                        ),

                    "preload=auto":
                        sum(
                            1
                            for v in videos
                            if (
                                v["preload"]
                                .lower()
                                == "auto"
                            )
                        ),

                    "preload=none":
                        sum(
                            1
                            for v in videos
                            if (
                                v["preload"]
                                .lower()
                                == "none"
                            )
                        ),
                })

            except Exception as exc:

                print(
                    f"[ERROR] "
                    f"Page execution failed: {exc}"
                )

                summary_rows.append({

                    "Page": page_name,

                    "Page URL": page_url,

                    "Video Elements": "ERROR",

                    "Video Requests": "ERROR",

                    "Failed Video Requests": "ERROR",

                    "Videos With Poster": "ERROR",

                    "preload=metadata": "ERROR",

                    "preload=auto": "ERROR",

                    "preload=none": "ERROR",
                })

            finally:

                page.close()

        browser.close()

    # --------------------------------------------------
    # CSV output
    # --------------------------------------------------

    fieldnames = [

        "Page",

        "Page URL",

        "Video Index",

        "Video Source",

        "Poster",

        "Preload",

        "Autoplay",

        "Muted",

        "Controls",

        "Loop",

        "Playsinline",

        "Width Attribute",

        "Height Attribute",

        "Rendered Width",

        "Rendered Height",

        "Ready State",

        "Network State",

        "Duration (sec)",

        "HTTP Status",

        "Content-Type",

        "Content-Length",

        "Response Body Size (bytes)",

        "Response Body Size (KB)",

        "Loading Time (ms)",

        "Optimization Observation",
    ]

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            all_rows
        )

    # --------------------------------------------------
    # JSON output
    # --------------------------------------------------

    OUTPUT_JSON.write_text(
        json.dumps(
            {
                "summary": summary_rows,
                "details": all_rows,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------
    # Console summary
    # --------------------------------------------------

    print("\n" + "=" * 110)

    print("TC-PERF-10 TEST COMPLETED")

    print("=" * 110)

    print("\nSUMMARY")

    print("-" * 110)

    for item in summary_rows:

        print(
            f"{item['Page']:15} | "
            f"videos="
            f"{str(item['Video Elements']):3} | "
            f"poster="
            f"{str(item['Videos With Poster']):3} | "
            f"metadata="
            f"{str(item['preload=metadata']):3} | "
            f"auto="
            f"{str(item['preload=auto']):3} | "
            f"none="
            f"{str(item['preload=none']):3}"
        )

    print("\nFiles generated:")

    print(
        f"CSV : {OUTPUT_CSV.resolve()}"
    )

    print(
        f"JSON: {OUTPUT_JSON.resolve()}"
    )


if __name__ == "__main__":
    run_test()