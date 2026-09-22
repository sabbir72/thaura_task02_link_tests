import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# ============================================================
# TC-05 CLAIM COLLECTOR
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "tc05_data"

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


# ============================================================
# Keywords
# ============================================================

KEYWORDS = [
    "parameter",
    "parameters",
    "billion",
    "million",
    "language",
    "languages",
    "energy",
    "token",
    "tokens",
    "wh",
    "mwh",
    "kwh",
    "encryption",
    "encrypted",
    "aes",
    "tls",
    "gdpr",
    "data residency",
    "data residence",
    "data stored",
    "stored in",
    "stored",
    "processed",
    "processing",
    "europe",
    "eu",
    "eea",
    "european union",
    "european economic area",
    "qwen",
    "pricing",
    "per million",
]


# ============================================================
# Helpers
# ============================================================

def safe_filename(url: str) -> str:
    """
    Convert URL into a safe JSON filename.
    """

    path = url.rstrip("/").split("/")[-1]

    if not path:
        path = "home"

    path = re.sub(r"[^a-zA-Z0-9_-]", "_", path)

    return f"{path}.json"


def normalize_text(text: str) -> str:
    """
    Normalize whitespace while preserving readable text.
    """

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def keyword_match(text: str) -> bool:
    """
    Check whether text contains any TC-05 keyword.
    """

    lower_text = text.lower()

    return any(
        keyword.lower() in lower_text
        for keyword in KEYWORDS
    )


def extract_numeric_claims(text: str):
    """
    Extract potentially important numeric technical claims.
    """

    patterns = {
        "parameter_count": [
            r"\b\d+(?:\.\d+)?\s*(?:B|billion|M|million)\s+parameters?\b",
            r"\b\d+(?:\.\d+)?\s*(?:billion|million)\s+model\s+parameters?\b",
        ],

        "language_count": [
            r"\b\d+\+\s+languages?\b",
            r"\bmore than\s+\d+\s+languages?\b",
            r"\bover\s+\d+\s+languages?\b",
        ],

        "energy": [
            r"\b\d+(?:\.\d+)?\s*(?:Wh|mWh|kWh)\b",
            r"\b\d+(?:\.\d+)?\s*(?:Wh|mWh|kWh)\s*(?:per|/)\s*\d+\s*tokens?\b",
            r"\benergy\s+per\s+\d+[kK]\s+tokens?\b",
        ],

        "encryption": [
            r"\bAES-\d+(?:-[A-Z0-9]+)?\b",
            r"\bTLS\s+\d+(?:\.\d+)?(?:\+)?\b",
            r"\bXSalsa20-Poly1305\b",
        ],

        "token_pricing": [
            r"\$\d+(?:\.\d+)?\s+per\s+million\s+input\s+tokens?",
            r"\$\d+(?:\.\d+)?\s+per\s+million\s+output\s+tokens?",
        ],

        "token_limit": [
            r"\bmax_completion_tokens\b",
            r"\bmax_tokens\b",
            r"\b\d+\s*token\s+limit\b",
            r"\bcapped\s+at\s+\d+\b",
        ],
    }

    results = {}

    for claim_type, regex_list in patterns.items():

        matches = []

        for pattern in regex_list:

            found = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            matches.extend(found)

        if matches:
            # Remove duplicates while preserving order
            unique_matches = list(dict.fromkeys(matches))
            results[claim_type] = unique_matches

    return results


def collect_claim_context(lines, index, radius=2):
    """
    Collect surrounding lines around a matched claim.

    Example:
        line -2
        line -1
        MATCHED LINE
        line +1
        line +2
    """

    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)

    context = []

    for i in range(start, end):
        context.append({
            "offset": i - index,
            "text": lines[i]
        })

    return context


# ============================================================
# Main Collector
# ============================================================

def collect_page(page, url):

    print("\n" + "=" * 80)
    print(f"Collecting: {url}")
    print("=" * 80)

    try:

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Give client-side rendered content time to appear.
        page.wait_for_timeout(3000)

        # ----------------------------------------------------
        # Page metadata
        # ----------------------------------------------------

        title = page.title()

        canonical = page.locator(
            'link[rel="canonical"]'
        ).get_attribute("href")

        meta_description = page.locator(
            'meta[name="description"]'
        ).get_attribute("content")

        og_title = page.locator(
            'meta[property="og:title"]'
        ).get_attribute("content")

        og_description = page.locator(
            'meta[property="og:description"]'
        ).get_attribute("content")

        og_url = page.locator(
            'meta[property="og:url"]'
        ).get_attribute("content")

        twitter_card = page.locator(
            'meta[name="twitter:card"]'
        ).get_attribute("content")

        # ----------------------------------------------------
        # Full visible body text
        # ----------------------------------------------------

        body_text = page.locator("body").inner_text(
            timeout=30000
        )

        body_text = normalize_text(body_text)

        # Split into useful lines.
        lines = [
            normalize_text(line)
            for line in body_text.splitlines()
        ]

        lines = [
            line for line in lines
            if line
        ]

        # ----------------------------------------------------
        # Keyword claim collection
        # ----------------------------------------------------

        claims = []

        for index, line in enumerate(lines):

            if keyword_match(line):

                claims.append({
                    "line_number": index + 1,
                    "text": line,
                    "context": collect_claim_context(
                        lines,
                        index,
                        radius=2
                    ),
                })

        # ----------------------------------------------------
        # Numeric / technical claim extraction
        # ----------------------------------------------------

        numeric_claims = extract_numeric_claims(
            body_text
        )

        # ----------------------------------------------------
        # Targeted DOM inspection
        #
        # Useful when a heading such as
        # "Energy per 1K Tokens" exists but the value is
        # rendered in a nearby DOM element.
        # ----------------------------------------------------

        targeted_sections = []

        target_patterns = [
            "Energy per 1K Tokens",
            "Energy Usage",
            "Parameters",
            "parameter",
            "languages",
            "90+ languages",
            "encryption",
            "AES-256-GCM",
            "TLS 1.2",
            "data residency",
        ]

        for target in target_patterns:

            try:

                locator = page.get_by_text(
                    re.compile(
                        re.escape(target),
                        re.IGNORECASE
                    )
                )

                count = locator.count()

                if count == 0:
                    continue

                # Inspect first few matches only.
                for i in range(min(count, 3)):

                    element = locator.nth(i)

                    try:

                        element_text = normalize_text(
                            element.inner_text(
                                timeout=5000
                            )
                        )

                    except Exception:
                        element_text = ""

                    if not element_text:
                        continue

                    # Try parent text.
                    parent_text = ""

                    try:

                        parent_text = normalize_text(
                            element.locator(
                                ".."
                            ).inner_text(
                                timeout=5000
                            )
                        )

                    except Exception:
                        pass

                    # Try grandparent text.
                    grandparent_text = ""

                    try:

                        grandparent_text = normalize_text(
                            element.locator(
                                "../.."
                            ).inner_text(
                                timeout=5000
                            )
                        )

                    except Exception:
                        pass

                    targeted_sections.append({
                        "target": target,
                        "element_text": element_text,
                        "parent_text": parent_text,
                        "grandparent_text": grandparent_text,
                    })

            except Exception:
                continue

        # ----------------------------------------------------
        # Page result
        # ----------------------------------------------------

        result = {
            "url": url,
            "title": title,
            "metadata": {
                "canonical": canonical,
                "description": meta_description,
                "og_title": og_title,
                "og_description": og_description,
                "og_url": og_url,
                "twitter_card": twitter_card,
            },
            "claim_count": len(claims),
            "claims": claims,
            "numeric_claims": numeric_claims,
            "targeted_sections": targeted_sections,
        }

        # ----------------------------------------------------
        # Save JSON
        # ----------------------------------------------------

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = OUTPUT_DIR / safe_filename(url)

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                indent=2,
                ensure_ascii=False
            )

        # ----------------------------------------------------
        # Console summary
        # ----------------------------------------------------

        print(f"Title       : {title}")
        print(f"Canonical   : {canonical}")
        print(f"Claims      : {len(claims)}")

        print("\nNumeric Claims:")

        if numeric_claims:

            for claim_type, values in numeric_claims.items():

                print(
                    f"  {claim_type}: {values}"
                )

        else:

            print("  None")

        print(
            f"\nTargeted sections collected: "
            f"{len(targeted_sections)}"
        )

        print(
            f"Saved       : {output_file}"
        )

        return True

    except PlaywrightTimeoutError:

        print(
            f"TIMEOUT: {url}"
        )

        return False

    except Exception as e:

        print(
            f"ERROR: {url}"
        )

        print(
            f"Reason: {e}"
        )

        return False


# ============================================================
# Entry Point
# ============================================================

def main():

    print("=" * 80)
    print("TC-05 CLAIM COLLECTION STARTED")
    print("=" * 80)

    print(
        f"Pages to scan: {len(PAGES)}"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    passed = 0
    failed = 0

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

        page = context.new_page()

        for url in PAGES:

            success = collect_page(
                page,
                url
            )

            if success:
                passed += 1
            else:
                failed += 1

        browser.close()

    # ========================================================
    # Final Collection Summary
    # ========================================================

    print("\n")
    print("=" * 80)
    print("TC-05 CLAIM COLLECTION SUMMARY")
    print("=" * 80)

    print(f"Total Pages : {len(PAGES)}")
    print(f"Collected   : {passed}")
    print(f"Failed      : {failed}")

    print("-" * 80)

    if failed == 0:
        print("COLLECTION RESULT: PASS")
    else:
        print("COLLECTION RESULT: PARTIAL / FAIL")

    print("=" * 80)


if __name__ == "__main__":
    main()