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

OUTPUT_CSV = Path("thaura_video_poster_optimization_report.csv")
OUTPUT_JSON = Path("thaura_video_poster_optimization_report.json")


def bytes_to_kb(value):
    if isinstance(value, int):
        return round(value / 1024, 2)
    return "N/A"


def is_same_resource(url1: str, url2: str) -> bool:
    if not url1 or not url2:
        return False

    path1 = urlsplit(url1).path
    path2 = urlsplit(url2).path

    return (
        url1 == url2
        or path1 == path2
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

            poster_requests = {}

            def handle_request_finished(request):

                try:

                    url = request.url

                    # We only need image resources here.
                    if request.resource_type != "image":
                        return

                    response = request.response()

                    if response is None:
                        return

                    # Capture only once per URL.
                    if url in poster_requests:
                        return

                    sizes = request.sizes()

                    poster_requests[url] = {
                        "status": response.status,

                        "content_type":
                            response.header_value(
                                "content-type"
                            ) or "N/A",

                        "content_length":
                            response.header_value(
                                "content-length"
                            ) or "N/A",

                        "response_body_size":
                            sizes.get(
                                "responseBodySize",
                                "N/A"
                            ),

                        "request_headers_size":
                            sizes.get(
                                "requestHeadersSize",
                                "N/A"
                            ),

                        "response_headers_size":
                            sizes.get(
                                "responseHeadersSize",
                                "N/A"
                            ),
                    }

                except Exception as exc:

                    print(
                        f"[WARNING] "
                        f"Image response error: {exc}"
                    )

            page.on(
                "requestfinished",
                handle_request_finished
            )

            try:

                print("[INFO] Loading page...")

                page.goto(
                    page_url,
                    wait_until="load",
                    timeout=60000
                )

                # Give poster/resource requests time to complete.
                page.wait_for_timeout(4000)

                # ---------------------------------------------
                # Collect video DOM information
                # ---------------------------------------------

                videos = page.locator("video").evaluate_all(
                    """
                    videos => videos.map((video, index) => {

                        const poster =
                            video.getAttribute("poster") || "";

                        const rect =
                            video.getBoundingClientRect();

                        return {
                            videoIndex: index,

                            poster: poster,

                            preload:
                                video.getAttribute("preload")
                                || "auto",

                            autoplay:
                                video.hasAttribute("autoplay"),

                            muted:
                                video.muted,

                            controls:
                                video.hasAttribute("controls"),

                            loop:
                                video.hasAttribute("loop"),

                            playsInline:
                                video.hasAttribute(
                                    "playsinline"
                                ),

                            renderedVideoWidth:
                                Math.round(rect.width),

                            renderedVideoHeight:
                                Math.round(rect.height),

                            readyState:
                                video.readyState,

                            networkState:
                                video.networkState,

                            duration:
                                Number.isFinite(video.duration)
                                ? Number(
                                    video.duration.toFixed(3)
                                  )
                                : null
                        };
                    })
                    """
                )

                print(
                    f"[INFO] Video elements: "
                    f"{len(videos)}"
                )

                print(
                    f"[INFO] Image responses: "
                    f"{len(poster_requests)}"
                )

                poster_count = 0

                for video in videos:

                    poster_url = video["poster"]

                    if not poster_url:
                        print(
                            f"[VIDEO {video['videoIndex']}] "
                            f"No poster attribute"
                        )
                        continue

                    poster_count += 1

                    matched = None

                    for request_url, request_data in (
                        poster_requests.items()
                    ):

                        if is_same_resource(
                            poster_url,
                            request_url
                        ):
                            matched = request_data
                            break

                    # -----------------------------------------
                    # Read poster intrinsic dimensions
                    # -----------------------------------------

                    poster_dom = page.evaluate(
                        """
                        posterUrl => {

                            const img =
                                Array.from(
                                    document.images
                                ).find(
                                    image =>
                                        image.currentSrc === posterUrl
                                        || image.src === posterUrl
                                );

                            if (!img) {
                                return null;
                            }

                            return {
                                naturalWidth:
                                    img.naturalWidth,

                                naturalHeight:
                                    img.naturalHeight,

                                renderedWidth:
                                    Math.round(
                                        img.getBoundingClientRect()
                                          .width
                                    ),

                                renderedHeight:
                                    Math.round(
                                        img.getBoundingClientRect()
                                          .height
                                    )
                            };
                        }
                        """,
                        poster_url
                    )

                    natural_width = "N/A"
                    natural_height = "N/A"

                    if poster_dom:

                        natural_width = poster_dom[
                            "naturalWidth"
                        ]

                        natural_height = poster_dom[
                            "naturalHeight"
                        ]

                    response_size = "N/A"

                    if matched:

                        response_size = matched[
                            "response_body_size"
                        ]

                    observations = []

                    # -----------------------------------------
                    # Format observation
                    # -----------------------------------------

                    content_type = (
                        matched["content_type"]
                        if matched
                        else "N/A"
                    )

                    if (
                        "webp"
                        in content_type.lower()
                    ):

                        observations.append(
                            "WebP poster"
                        )

                    elif (
                        "avif"
                        in content_type.lower()
                    ):

                        observations.append(
                            "AVIF poster"
                        )

                    elif (
                        "jpeg"
                        in content_type.lower()
                        or "jpg"
                        in poster_url.lower()
                    ):

                        observations.append(
                            "JPEG poster"
                        )

                    elif (
                        "png"
                        in content_type.lower()
                    ):

                        observations.append(
                            "PNG poster"
                        )

                    # -----------------------------------------
                    # Size observation
                    # -----------------------------------------

                    if isinstance(
                        response_size,
                        int
                    ):

                        if response_size > 100 * 1024:

                            observations.append(
                                "Large payload candidate (>100 KB)"
                            )

                        elif response_size > 50 * 1024:

                            observations.append(
                                "Moderate payload candidate (>50 KB)"
                            )

                        else:

                            observations.append(
                                "Small payload"
                            )

                    # -----------------------------------------
                    # Dimension observation
                    # -----------------------------------------

                    rendered_width = video[
                        "renderedVideoWidth"
                    ]

                    rendered_height = video[
                        "renderedVideoHeight"
                    ]

                    if (
                        isinstance(natural_width, int)
                        and isinstance(natural_height, int)
                        and rendered_width > 0
                        and rendered_height > 0
                    ):

                        width_ratio = (
                            natural_width
                            / rendered_width
                        )

                        height_ratio = (
                            natural_height
                            / rendered_height
                        )

                        if (
                            width_ratio >= 2
                            and height_ratio >= 2
                        ):

                            observations.append(
                                "Poster intrinsic dimensions are "
                                "at least 2x rendered video dimensions"
                            )

                    row = {

                        "Page":
                            page_name,

                        "Page URL":
                            page_url,

                        "Video Index":
                            video["videoIndex"],

                        "Poster URL":
                            poster_url,

                        "Poster HTTP Status":
                            (
                                matched["status"]
                                if matched
                                else "N/A"
                            ),

                        "Poster Content-Type":
                            content_type,

                        "Content-Length":
                            (
                                matched["content_length"]
                                if matched
                                else "N/A"
                            ),

                        "Response Body Size (bytes)":
                            response_size,

                        "Response Body Size (KB)":
                            bytes_to_kb(
                                response_size
                            ),

                        "Poster Natural Width":
                            natural_width,

                        "Poster Natural Height":
                            natural_height,

                        "Rendered Video Width":
                            rendered_width,

                        "Rendered Video Height":
                            rendered_height,

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

                        "Video Ready State":
                            video["readyState"],

                        "Video Network State":
                            video["networkState"],

                        "Video Duration (sec)":
                            video["duration"],

                        "Optimization Observation":
                            "; ".join(observations)
                            if observations
                            else "No immediate observation",
                    }

                    all_rows.append(row)

                    print(
                        f"[VIDEO {video['videoIndex']}] "
                        f"poster={poster_url} | "
                        f"status={row['Poster HTTP Status']} | "
                        f"type={content_type} | "
                        f"size={row['Response Body Size (KB)']} KB | "
                        f"preload={video['preload']}"
                    )

                summary_rows.append({

                    "Page":
                        page_name,

                    "Page URL":
                        page_url,

                    "Video Elements":
                        len(videos),

                    "Videos With Poster":
                        poster_count,

                    "Poster Image Responses":
                        sum(
                            1
                            for video in videos
                            if video["poster"]
                            and any(
                                is_same_resource(
                                    video["poster"],
                                    url
                                )
                                for url in poster_requests
                            )
                        ),

                })

            except Exception as exc:

                print(
                    f"[ERROR] "
                    f"Page execution failed: {exc}"
                )

                summary_rows.append({

                    "Page":
                        page_name,

                    "Page URL":
                        page_url,

                    "Video Elements":
                        "ERROR",

                    "Videos With Poster":
                        "ERROR",

                    "Poster Image Responses":
                        "ERROR",
                })

            finally:

                page.close()

        browser.close()

    # ---------------------------------------------------------
    # CSV
    # ---------------------------------------------------------

    fieldnames = [

        "Page",

        "Page URL",

        "Video Index",

        "Poster URL",

        "Poster HTTP Status",

        "Poster Content-Type",

        "Content-Length",

        "Response Body Size (bytes)",

        "Response Body Size (KB)",

        "Poster Natural Width",

        "Poster Natural Height",

        "Rendered Video Width",

        "Rendered Video Height",

        "Preload",

        "Autoplay",

        "Muted",

        "Controls",

        "Loop",

        "Playsinline",

        "Video Ready State",

        "Video Network State",

        "Video Duration (sec)",

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

    # ---------------------------------------------------------
    # JSON
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Final console output
    # ---------------------------------------------------------

    print("\n" + "=" * 110)

    print("TC-PERF-11 TEST COMPLETED")

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
            f"poster_response="
            f"{str(item['Poster Image Responses']):3}"
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