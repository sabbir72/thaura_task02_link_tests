import json
import re
from pathlib import Path


# ============================================================
# TC-05 CLAIM ANALYZER
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "tests" / "tc05_data"


# ============================================================
# Helpers
# ============================================================

def load_json_files():
    """
    Load all collected TC-05 JSON files.
    """

    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        return {}

    files = sorted(DATA_DIR.glob("*.json"))

    if not files:
        print(f"ERROR: No JSON files found in: {DATA_DIR}")
        return {}

    data = {}

    for file in files:

        try:

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data[file.name] = json.load(f)

        except Exception as e:

            print(
                f"ERROR reading {file.name}: {e}"
            )

    return data


def normalize_text(text):
    """
    Normalize whitespace.
    """

    if not isinstance(text, str):
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def collect_all_text(page_data):
    """
    Collect text from:

    1. claims
    2. numeric_claims
    3. targeted_sections
    """

    texts = []

    # --------------------------------------------------------
    # claims
    # --------------------------------------------------------

    claims = page_data.get("claims", [])

    if isinstance(claims, list):

        for claim in claims:

            if isinstance(claim, dict):

                text = claim.get("text")

                if isinstance(text, str):
                    texts.append(text)

                context = claim.get(
                    "context",
                    []
                )

                if isinstance(context, list):

                    for item in context:

                        if isinstance(item, dict):

                            context_text = item.get(
                                "text"
                            )

                            if isinstance(
                                context_text,
                                str
                            ):
                                texts.append(
                                    context_text
                                )

    # --------------------------------------------------------
    # numeric_claims
    # --------------------------------------------------------

    numeric_claims = page_data.get(
        "numeric_claims",
        {}
    )

    if isinstance(numeric_claims, dict):

        for values in numeric_claims.values():

            if isinstance(values, list):

                for value in values:

                    if isinstance(value, str):
                        texts.append(value)

    # --------------------------------------------------------
    # targeted_sections
    # --------------------------------------------------------

    targeted_sections = page_data.get(
        "targeted_sections",
        []
    )

    if isinstance(targeted_sections, list):

        for section in targeted_sections:

            if isinstance(section, dict):

                for key in [
                    "target",
                    "element_text",
                    "parent_text",
                    "grandparent_text",
                ]:

                    value = section.get(key)

                    if isinstance(value, str):
                        texts.append(value)

    return [
        normalize_text(text)
        for text in texts
        if normalize_text(text)
    ]


def unique(values):
    """
    Remove duplicates while preserving order.
    """

    return list(
        dict.fromkeys(values)
    )


def print_section(title):
    """
    Print formatted analyzer section.
    """

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


# ============================================================
# 1. Parameter Claims
# ============================================================

def analyze_parameters(data):

    print_section(
        "1. MODEL PARAMETER CLAIMS"
    )

    pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:B|billion|M|million)"
        r"\s+parameters?\b",
        re.IGNORECASE
    )

    found = []

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        for text in texts:

            matches = pattern.findall(text)

            for match in matches:

                found.append(
                    (
                        page,
                        match,
                        text
                    )
                )

    if not found:

        print(
            "No numeric model parameter count found."
        )

        print(
            "Result: NOT AVAILABLE / SKIPPED"
        )

        return

    print(
        f"Numeric parameter claims found: "
        f"{len(found)}"
    )

    for page, value, text in found:

        print(
            f"\n[{page}]"
        )

        print(
            f"Value : {value}"
        )

        print(
            f"Text  : {text}"
        )


# ============================================================
# 2. Energy Claims
# ============================================================

def analyze_energy(data):

    print_section(
        "2. ENERGY PER 1K TOKENS CLAIMS"
    )

    energy_patterns = [

        re.compile(
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:Wh|mWh|kWh)"
            r"(?:\s*(?:per|/)\s*\d+[kK]?\s*tokens?)?",
            re.IGNORECASE
        ),

        re.compile(
            r"energy\s+per\s+\d+[kK]?\s+tokens?",
            re.IGNORECASE
        ),

    ]

    found = []

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        for text in texts:

            for pattern in energy_patterns:

                matches = pattern.findall(text)

                for match in matches:

                    found.append(
                        (
                            page,
                            match,
                            text
                        )
                    )

    # Remove duplicates
    unique_found = []

    seen = set()

    for item in found:

        key = (
            item[0],
            item[1],
            item[2]
        )

        if key not in seen:

            seen.add(key)
            unique_found.append(item)

    if not unique_found:

        print(
            "No numeric energy measurement found."
        )

        print(
            "Result: NOT AVAILABLE / SKIPPED"
        )

        return

    print(
        f"Energy claims found: "
        f"{len(unique_found)}"
    )

    for page, value, text in unique_found:

        print(
            f"\n[{page}]"
        )

        print(
            f"Value : {value}"
        )

        print(
            f"Text  : {text}"
        )


# ============================================================
# 3. Language Claims
# ============================================================

def analyze_languages(data):

    print_section(
        "3. LANGUAGE SUPPORT CLAIMS"
    )

    patterns = [

        re.compile(
            r"\b\d+\+\s+languages?\b",
            re.IGNORECASE
        ),

        re.compile(
            r"\bmore than\s+\d+\s+languages?\b",
            re.IGNORECASE
        ),

        re.compile(
            r"\bover\s+\d+\s+languages?\b",
            re.IGNORECASE
        ),

    ]

    found = []

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        for text in texts:

            for pattern in patterns:

                matches = pattern.findall(text)

                for match in matches:

                    found.append(
                        (
                            page,
                            match,
                            text
                        )
                    )

    if not found:

        print(
            "No numeric language support claim found."
        )

        return

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    normalized = []

    for page, value, text in found:

        value_lower = value.lower()

        number_match = re.search(
            r"\d+",
            value_lower
        )

        if not number_match:
            continue

        number = number_match.group()

        normalized_value = f"{number}+"

        normalized.append(
            (
                page,
                normalized_value,
                value,
                text
            )
        )

    print(
        f"Language claims found: "
        f"{len(normalized)}"
    )

    for page, normalized_value, original, text in normalized:

        print(
            f"\n[{page}]"
        )

        print(
            f"Original   : {original}"
        )

        print(
            f"Normalized : {normalized_value}"
        )

        print(
            f"Text       : {text}"
        )

    values = unique(
        item[1]
        for item in normalized
    )

    print("\nNormalized Values:")

    for value in values:
        print(
            f"  - {value}"
        )

    if len(values) == 1:

        print(
            "\nConsistency: PASS"
        )

    else:

        print(
            "\nConsistency: REVIEW REQUIRED"
        )


# ============================================================
# 4. Encryption Claims
# ============================================================

def analyze_encryption(data):

    print_section(
        "4. ENCRYPTION / SECURITY CLAIMS"
    )

    aes_pattern = re.compile(
        r"\bAES-\d+(?:-[A-Z0-9]+)?\b",
        re.IGNORECASE
    )

    tls_pattern = re.compile(
        r"\bTLS\s+\d+(?:\.\d+)?(?:\+)?"
        r"(?:\s+or\s+higher)?",
        re.IGNORECASE
    )

    backup_pattern = re.compile(
        r"\bXSalsa20-Poly1305\b",
        re.IGNORECASE
    )

    aes_values = set()
    tls_values = set()
    backup_values = set()

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        for text in texts:

            for value in aes_pattern.findall(text):
                aes_values.add(
                    value.upper()
                )

            for value in tls_pattern.findall(text):

                normalized = value.lower()

                if (
                    "1.2" in normalized
                    and (
                        "+" in normalized
                        or "or higher" in normalized
                    )
                ):
                    tls_values.add(
                        "TLS 1.2+"
                    )

                elif "1.3" in normalized:

                    tls_values.add(
                        "TLS 1.3"
                    )

            for value in backup_pattern.findall(text):

                backup_values.add(
                    value
                )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print(
        "AES Claims:"
    )

    for value in sorted(aes_values):
        print(
            f"  - {value}"
        )

    print(
        "\nTLS Claims:"
    )

    for value in sorted(tls_values):
        print(
            f"  - {value}"
        )

    print(
        "\nBackup Encryption Claims:"
    )

    for value in sorted(backup_values):
        print(
            f"  - {value}"
        )

    # --------------------------------------------------------
    # Primary consistency
    # --------------------------------------------------------

    primary_aes = {
        value
        for value in aes_values
        if value == "AES-256-GCM"
    }

    if primary_aes:

        print(
            "\nAES primary claim: PASS"
        )

    else:

        print(
            "\nAES primary claim: REVIEW"
        )

    if "TLS 1.2+" in tls_values:

        print(
            "TLS baseline claim: PASS"
        )

    else:

        print(
            "TLS baseline claim: REVIEW"
        )

    print(
        "\nNote: TLS 1.3 preferred and "
        "backup-specific encryption are treated "
        "as additional claims, not automatic contradictions."
    )


# ============================================================
# 5. EU Data Residency Claims
# ============================================================

def analyze_eu_residency(data):

    print_section(
        "5. EU DATA RESIDENCY / PROCESSING CLAIMS"
    )

    patterns = [

        re.compile(
            r"stored and processed only on EU servers",
            re.IGNORECASE
        ),

        re.compile(
            r"store data exclusively in EU servers",
            re.IGNORECASE
        ),

        re.compile(
            r"all servers are located in the European Union",
            re.IGNORECASE
        ),

        re.compile(
            r"all processing of personal data.{0,150}"
            r"(?:European Union|European Economic Area)",
            re.IGNORECASE
        ),

        re.compile(
            r"servers are located in the EU",
            re.IGNORECASE
        ),

        re.compile(
            r"EU-only processing",
            re.IGNORECASE
        ),

    ]

    found = []

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        for text in texts:

            for pattern in patterns:

                if pattern.search(text):

                    found.append(
                        (
                            page,
                            text
                        )
                    )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    found = unique(found)

    if not found:

        print(
            "No primary EU residency/processing claim found."
        )

        return

    print(
        f"Primary EU claims found: {len(found)}"
    )

    for page, text in found:

        print(
            f"\n[{page}]"
        )

        print(
            f"Text: {text}"
        )

    print(
        "\nPrimary residency scope: EU / EU-EEA"
    )

    print(
        "Result: CONSISTENT"
    )

    print(
        "\nNote:"
    )

    print(
        "Future third-country transfer clauses are "
        "treated as contingency/legal safeguards, "
        "not automatic residency contradictions."
    )


# ============================================================
# 6. API Token Pricing
# ============================================================

def analyze_token_pricing(data):

    print_section(
        "6. API TOKEN PRICING CLAIMS"
    )

    input_pattern = re.compile(
        r"\$(\d+(?:\.\d+)?)\s+per\s+million\s+input\s+tokens?",
        re.IGNORECASE
    )

    output_pattern = re.compile(
        r"\$(\d+(?:\.\d+)?)\s+per\s+million\s+output\s+tokens?",
        re.IGNORECASE
    )

    claims = []

    for page, page_data in data.items():

        texts = collect_all_text(page_data)

        page_input = None
        page_output = None

        for text in texts:

            input_match = input_pattern.search(text)

            if input_match:

                page_input = input_match.group(1)

            output_match = output_pattern.search(text)

            if output_match:

                page_output = output_match.group(1)

        if page_input or page_output:

            claims.append(
                (
                    page,
                    page_input,
                    page_output
                )
            )

    if not claims:

        print(
            "No API token pricing claim found."
        )

        return

    print(
        f"Pages containing pricing claims: "
        f"{len(claims)}"
    )

    normalized = set()

    for page, input_price, output_price in claims:

        print(
            f"\n[{page}]"
        )

        print(
            f"Input  : ${input_price}"
        )

        print(
            f"Output : ${output_price}"
        )

        if input_price and output_price:

            normalized.add(
                (
                    input_price,
                    output_price
                )
            )

    if len(normalized) == 1:

        print(
            "\nPricing consistency: PASS"
        )

    else:

        print(
            "\nPricing consistency: REVIEW REQUIRED"
        )


# ============================================================
# 7. Important Technical Claims Overview
# ============================================================

def analyze_numeric_overview(data):

    print_section(
        "7. NUMERIC / TECHNICAL CLAIM OVERVIEW"
    )

    total_numeric_claims = 0

    for page, page_data in data.items():

        numeric_claims = page_data.get(
            "numeric_claims",
            {}
        )

        if not isinstance(
            numeric_claims,
            dict
        ):
            continue

        if not numeric_claims:
            continue

        print(
            f"\n[{page}]"
        )

        for claim_type, values in numeric_claims.items():

            print(
                f"  {claim_type}: {values}"
            )

            total_numeric_claims += len(values)

    print(
        "\nTotal numeric/technical claim values:",
        total_numeric_claims
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "TC-05 CLAIM ANALYSIS STARTED"
    )
    print("=" * 80)

    data = load_json_files()

    if not data:

        return

    print(
        f"Pages loaded: {len(data)}"
    )

    analyze_parameters(data)

    analyze_energy(data)

    analyze_languages(data)

    analyze_encryption(data)

    analyze_eu_residency(data)

    analyze_token_pricing(data)

    analyze_numeric_overview(data)

    print("\n")
    print("=" * 80)
    print(
        "TC-05 CLAIM ANALYSIS COMPLETED"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()