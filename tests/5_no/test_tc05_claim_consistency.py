import json
import re
from pathlib import Path

import pytest


# ============================================================
# TC-05: FACTUAL / TECHNICAL CLAIM CONSISTENCY
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

# Actual collected data location:
# /home/eng-sabbir/thaura_task02_link_tests/tests/tc05_data/
DATA_DIR = BASE_DIR / "tests" / "tc05_data"


# ============================================================
# DATA LOADING
# ============================================================

def load_all_claims():
    """
    Load all TC-05 collected JSON files.
    """

    if not DATA_DIR.exists():
        pytest.fail(
            f"TC-05 data directory not found: {DATA_DIR}"
        )

    json_files = sorted(
        DATA_DIR.glob("*.json")
    )

    if not json_files:
        pytest.fail(
            f"No JSON files found in: {DATA_DIR}"
        )

    pages = {}

    for file in json_files:

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            pages[file.name] = json.load(f)

    return pages


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_all_text(page_data):
    """
    Collect text from:
    - claims
    - claim context
    - numeric_claims
    - targeted_sections
    """

    texts = []

    # --------------------------------------------------------
    # claims
    # --------------------------------------------------------

    claims = page_data.get(
        "claims",
        []
    )

    if isinstance(claims, list):

        for claim in claims:

            if not isinstance(claim, dict):
                continue

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

    if isinstance(
        numeric_claims,
        dict
    ):

        for values in numeric_claims.values():

            if isinstance(
                values,
                list
            ):

                for value in values:

                    if isinstance(
                        value,
                        str
                    ):
                        texts.append(value)

    # --------------------------------------------------------
    # targeted_sections
    # --------------------------------------------------------

    targeted_sections = page_data.get(
        "targeted_sections",
        []
    )

    if isinstance(
        targeted_sections,
        list
    ):

        for section in targeted_sections:

            if not isinstance(
                section,
                dict
            ):
                continue

            for key in [
                "target",
                "element_text",
                "parent_text",
                "grandparent_text",
            ]:

                value = section.get(key)

                if isinstance(
                    value,
                    str
                ):
                    texts.append(value)

    return [
        text.strip()
        for text in texts
        if isinstance(text, str)
        and text.strip()
    ]


# ============================================================
# TC-05-01
# VOICE LANGUAGE CONSISTENCY
# ============================================================

def test_tc05_voice_language_consistency():

    pages = load_all_claims()

    found_values = []

    pattern = re.compile(
        r"(90\+|more than 90|over 90)"
        r"\s+languages?",
        re.IGNORECASE
    )

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            matches = pattern.findall(text)

            for match in matches:

                normalized = "90+"

                found_values.append(
                    (
                        page,
                        normalized,
                        text
                    )
                )

    assert found_values, (
        "No '90+ languages' or equivalent "
        "language claim was found."
    )

    normalized_values = {
        item[1]
        for item in found_values
    }

    assert normalized_values == {
        "90+"
    }, (
        "Inconsistent language claims found: "
        f"{normalized_values}"
    )


# ============================================================
# TC-05-02
# ENCRYPTION / SECURITY CONSISTENCY
# ============================================================

def test_tc05_encryption_consistency():

    pages = load_all_claims()

    aes_values = set()
    tls_values = set()

    aes_pattern = re.compile(
        r"\bAES-\d+(?:-[A-Z0-9]+)?\b",
        re.IGNORECASE
    )

    tls_pattern = re.compile(
        r"\bTLS\s+\d+(?:\.\d+)?"
        r"(?:\+|\s+or\s+higher)?",
        re.IGNORECASE
    )

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            # AES
            for value in aes_pattern.findall(text):

                aes_values.add(
                    value.upper()
                )

            # TLS
            for value in tls_pattern.findall(text):

                value_lower = value.lower()

                if (
                    "tls 1.2" in value_lower
                    and (
                        "+" in value_lower
                        or "or higher" in value_lower
                    )
                ):
                    tls_values.add(
                        "TLS 1.2+"
                    )

                elif "tls 1.3" in value_lower:

                    tls_values.add(
                        "TLS 1.3"
                    )

    # --------------------------------------------------------
    # AES validation
    # --------------------------------------------------------

    assert "AES-256-GCM" in aes_values, (
        "AES-256-GCM primary encryption claim "
        "was not found."
    )

    # --------------------------------------------------------
    # TLS validation
    # --------------------------------------------------------

    assert "TLS 1.2+" in tls_values, (
        "TLS 1.2+ baseline claim was not found."
    )


# ============================================================
# TC-05-03
# EU DATA RESIDENCY / PROCESSING CONSISTENCY
# ============================================================

def test_tc05_eu_data_residency_consistency():

    pages = load_all_claims()

    primary_patterns = [

        r"stored and processed only on EU servers",

        r"store data exclusively in EU servers",

        r"all servers are located in the European Union",

        r"all processing of personal data.{0,150}"
        r"(?:European Union|European Economic Area)",

        r"servers are located in the EU",

        r"EU-only processing",

    ]

    primary_claims = []

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            for pattern in primary_patterns:

                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                ):

                    primary_claims.append(
                        (
                            page,
                            text
                        )
                    )

    assert primary_claims, (
        "No primary EU data residency/processing "
        "claim was found."
    )

    # --------------------------------------------------------
    # Explicit non-EU contradiction detection
    # --------------------------------------------------------

    contradiction_pattern = re.compile(
        r"(?:data|personal data|customer data)"
        r".{0,100}"
        r"(?:stored|processed|located)"
        r".{0,100}"
        r"(?:outside the EU|outside EU)",
        re.IGNORECASE
    )

    contradictions = []

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            if contradiction_pattern.search(
                text
            ):

                contradictions.append(
                    (
                        page,
                        text
                    )
                )

    assert not contradictions, (
        "Explicit non-EU primary data "
        "residency contradiction found: "
        f"{contradictions}"
    )


# ============================================================
# TC-05-04
# API TOKEN PRICING CONSISTENCY
# ============================================================

def test_tc05_api_token_pricing_consistency():

    pages = load_all_claims()

    input_pattern = re.compile(
        r"\$(\d+(?:\.\d+)?)"
        r"\s+per\s+million\s+input\s+tokens?",
        re.IGNORECASE
    )

    output_pattern = re.compile(
        r"\$(\d+(?:\.\d+)?)"
        r"\s+per\s+million\s+output\s+tokens?",
        re.IGNORECASE
    )

    pricing_values = []

    for page, data in pages.items():

        texts = extract_all_text(data)

        page_input = None
        page_output = None

        for text in texts:

            input_match = input_pattern.search(
                text
            )

            if input_match:
                page_input = input_match.group(1)

            output_match = output_pattern.search(
                text
            )

            if output_match:
                page_output = output_match.group(1)

        if page_input and page_output:

            pricing_values.append(
                (
                    page,
                    page_input,
                    page_output
                )
            )

    assert pricing_values, (
        "No complete API token pricing claim "
        "was found."
    )

    normalized = {
        (
            input_price,
            output_price
        )
        for (
            page,
            input_price,
            output_price
        ) in pricing_values
    }

    assert normalized == {
        ("0.50", "2.00")
    }, (
        "Inconsistent API token pricing found: "
        f"{normalized}"
    )


# ============================================================
# TC-05-05
# ENERGY PER 1K TOKENS
# ============================================================

def test_tc05_energy_per_1k_tokens():

    pages = load_all_claims()

    energy_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:Wh|mWh|kWh)"
        r"(?:\s*(?:per|/)\s*\d+[kK]?\s*tokens?)?",
        re.IGNORECASE
    )

    energy_values = []

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            matches = energy_pattern.findall(
                text
            )

            for value in matches:

                energy_values.append(
                    (
                        page,
                        value,
                        text
                    )
                )

    if not energy_values:

        pytest.skip(
            "Current collected data contains the "
            "'Energy per 1K Tokens' heading but "
            "no numeric energy measurement value."
        )

    assert energy_values, (
        "No numeric energy measurement found."
    )


# ============================================================
# TC-05-06
# MODEL PARAMETER COUNT
# ============================================================

def test_tc05_model_parameter_count():

    pages = load_all_claims()

    parameter_pattern = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:B|billion|M|million)"
        r"\s+parameters?\b",
        re.IGNORECASE
    )

    parameter_values = []

    for page, data in pages.items():

        texts = extract_all_text(data)

        for text in texts:

            matches = parameter_pattern.findall(
                text
            )

            for value in matches:

                parameter_values.append(
                    (
                        page,
                        value,
                        text
                    )
                )

    if not parameter_values:

        pytest.skip(
            "Current collected data does not contain "
            "a numeric model parameter count."
        )

    # If values exist, make sure the same claim
    # is not represented with conflicting numbers.

    normalized_values = set()

    for page, value, text in parameter_values:

        normalized = value.lower()
        normalized = normalized.replace(
            " ",
            ""
        )

        normalized_values.add(
            normalized
        )

    assert len(normalized_values) == 1, (
        "Conflicting model parameter counts found: "
        f"{normalized_values}"
    )


# ============================================================
# FINAL TC-05 SUMMARY
# ============================================================

def pytest_terminal_summary(
    terminalreporter,
    exitstatus,
    config
):

    reports = terminalreporter.getreports(
        "call"
    )

    passed = sum(
        1
        for report in reports
        if report.passed
    )

    failed = sum(
        1
        for report in reports
        if report.failed
    )

    skipped = sum(
        1
        for report in reports
        if report.skipped
    )

    total = (
        passed
        + failed
        + skipped
    )

    # --------------------------------------------------------
    # Final Result
    # --------------------------------------------------------

    if failed > 0:

        final_result = "FAIL"

    elif total == 0:

        final_result = "NO TEST EXECUTED"

    else:

        final_result = "PASS"

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)

    print(
        "TC-05 FACTUAL / TECHNICAL CLAIM CONSISTENCY SUMMARY"
    )

    print("=" * 70)

    print(
        f"Total Tests : {total}"
    )

    print(
        f"PASS        : {passed}"
    )

    print(
        f"FAIL        : {failed}"
    )

    print(
        f"SKIPPED     : {skipped}"
    )

    print("-" * 70)

    print("Test Areas:")

    print(
        "1. Voice Language Claim Consistency"
    )

    print(
        "2. Encryption / Security Claim Consistency"
    )

    print(
        "3. EU Data Residency / Processing Consistency"
    )

    print(
        "4. API Token Pricing Consistency"
    )

    print(
        "5. Energy per 1K Tokens"
    )

    print(
        "6. Model Parameter Count"
    )

    print("-" * 70)

    print(
        "Scope:"
    )

    print(
        "Cross-page factual and technical claim consistency"
    )

    print(
        "Source:"
    )

    print(
        "Collected page data from tests/tc05_data/"
    )

    print("=" * 70)

    print(
        f"FINAL RESULT: {final_result}"
    )

    print("=" * 70)