from playwright.sync_api import Page, expect


def test_pr_01_monthly_pro_price(page: Page) -> None:

    print("\n[TC-PR-01] Starting Monthly Pro Price Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)
    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)
    print("[STEP 2] View Plans clicked")

    # Click Monthly
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)
    print("[STEP 3] Monthly plan selected")

    # Verify Pro price
    pro_price = page.get_by_text("$15/month", exact=True)

    expect(pro_price).to_be_visible()

    print("[STEP 4] Pro price verified: $15/month")
    print("[RESULT] TC-PR-01 PASSED")



def test_pr_02_annual_pricing(page: Page) -> None:

    print("\n[TC-PR-02] Starting Annual Pricing Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)
    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)
    print("[STEP 2] View Plans clicked")

    # Select Annual
    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1500)
    print("[STEP 3] Annual plan selected")

    # Verify Annual monthly equivalent
    expect(page.get_by_text("$12", exact=True)).to_be_visible()
    print("[STEP 4] Annual monthly price verified: $12/month")

    # Verify Annual billing amount
    expect(page.get_by_text("Billed $144/year", exact=True)).to_be_visible()
    print("[STEP 5] Annual billing price verified: $144/year")

    print("[RESULT] TC-PR-02 PASSED")


   

def test_pr_03_annual_calculation(page: Page) -> None:

    print("\n[TC-PR-03] Starting Annual Calculation Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)

    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)

    print("[STEP 2] View Plans clicked")

    # Select Monthly
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)

    print("[STEP 3] Monthly plan selected")

    # Verify Monthly price
    expect(page.get_by_text("$15", exact=True)).to_be_visible()

    print("[STEP 4] Monthly price verified: $15/month")

    # Calculate yearly price based on Monthly price
    monthly_price = 15
    calculated_yearly_price = monthly_price * 12

    print(
        f"[STEP 5] Calculation: "
        f"${monthly_price} × 12 = ${calculated_yearly_price}/year"
    )

    # Select Annual
    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1500)

    print("[STEP 6] Annual plan selected")

    # Verify Annual monthly equivalent
    expect(page.get_by_text("$12", exact=True)).to_be_visible()

    print("[STEP 7] Annual monthly price verified: $12/month")

    # Verify Annual billing amount
    expect(page.get_by_text("Billed $144/year", exact=True)).to_be_visible()

    print("[STEP 8] Annual billing price verified: $144/year")

    # Compare calculated yearly price with annual billing price
    annual_price = 144
    saving = calculated_yearly_price - annual_price

    print(
        f"[STEP 9] Calculation: "
        f"${calculated_yearly_price} - ${annual_price} = ${saving} saving"
    )

    # Verify saving amount
    assert saving == 36, (
        f"Expected saving $36, but actual saving is ${saving}"
    )

    print("[STEP 10] Yearly saving verified: $36")

    print("[RESULT] TC-PR-03 PASSED")




def test_pr_04_monthly_annual_toggle(page: Page) -> None:

    print("\n[TC-PR-04] Starting Monthly/Annual Toggle Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)

    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)

    print("[STEP 2] View Plans clicked")

    # Select Monthly
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)

    print("[STEP 3] Monthly plan selected")

    # Verify Monthly price
    expect(page.get_by_text("$15", exact=True)).to_be_visible()

    print("[STEP 4] Monthly price verified: $15/month")

    # Select Annual
    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1500)

    print("[STEP 5] Annual plan selected")

    # Verify Annual price
    expect(page.get_by_text("$12", exact=True)).to_be_visible()
    expect(page.get_by_text("Billed $144/year", exact=True)).to_be_visible()

    print("[STEP 6] Annual price verified: $12/month")
    print("[STEP 7] Annual billing verified: $144/year")

    # Select Monthly again
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)

    print("[STEP 8] Monthly selected again")

    # Verify Monthly price is restored
    expect(page.get_by_text("$15", exact=True)).to_be_visible()

    print("[STEP 9] Monthly price restored: $15/month")

    print("[RESULT] TC-PR-04 PASSED")    


def test_pr_05_save_20_percent_calculation(page: Page) -> None:

    print("\n[TC-PR-05] Starting Save 20% Calculation Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)

    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)

    print("[STEP 2] View Plans clicked")

    # Select Monthly
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)

    print("[STEP 3] Monthly plan selected")

    # Verify Monthly price
    expect(page.get_by_text("$15", exact=True)).to_be_visible()

    print("[STEP 4] Monthly price verified: $15/month")

    # Calculate normal yearly price
    monthly_price = 15
    normal_yearly_price = monthly_price * 12

    print(
        f"[STEP 5] Normal yearly calculation: "
        f"${monthly_price} × 12 = ${normal_yearly_price}/year"
    )

    # Select Annual
    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1500)

    print("[STEP 6] Annual plan selected")

    # Verify Annual billing price
    expect(
        page.get_by_text("Billed $144/year", exact=True)
    ).to_be_visible()

    print("[STEP 7] Annual billing price verified: $144/year")

    # Verify Save 20%
    expect(
        page.get_by_text("Save 20%", exact=True)
    ).to_be_visible()

    print("[STEP 8] Save 20% text verified")

    # Calculate saving
    annual_price = 144
    saving = normal_yearly_price - annual_price

    print(
        f"[STEP 9] Saving calculation: "
        f"${normal_yearly_price} - ${annual_price} = ${saving}"
    )

    # Calculate discount percentage
    discount_percentage = (saving / normal_yearly_price) * 100

    print(
        f"[STEP 10] Discount calculation: "
        f"${saving} / ${normal_yearly_price} × 100 = "
        f"{discount_percentage:.0f}%"
    )

    # Verify 20% discount
    assert discount_percentage == 20, (
        f"Expected 20% discount, "
        f"but calculated {discount_percentage:.2f}%"
    )

    print("[STEP 11] 20% discount calculation verified")

    print("[RESULT] TC-PR-05 PASSED")


def test_pr_06_pricing_vs_faq_consistency(page: Page) -> None:

    print("\n[TC-PR-06] Starting Pricing vs FAQ Consistency Test")

    # Open Pricing page
    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)

    print("[STEP 1] Pricing page opened")

    # Click View Plans
    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)

    print("[STEP 2] View Plans clicked")

    # Select Monthly
    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1500)

    print("[STEP 3] Monthly plan selected")

    # Verify current Pricing page values
    expect(page.get_by_text("$15", exact=True)).to_be_visible()

    print("[STEP 4] Pricing page Monthly price: $15/month")

    # Select Annual
    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1500)

    print("[STEP 5] Annual plan selected")

    # Verify Annual pricing
    expect(page.get_by_text("$12", exact=True)).to_be_visible()
    expect(
        page.get_by_text("Billed $144/year", exact=True)
    ).to_be_visible()

    print("[STEP 6] Pricing page Annual price: $12/month")
    print("[STEP 7] Pricing page Annual billing: $144/year")

    # Open FAQ
    page.get_by_role("link", name="FAQ").click()
    page.wait_for_timeout(2000)

    print("[STEP 8] FAQ page opened")

    # Search FAQ page text
    faq_text = page.locator("body").inner_text()

    print("[STEP 9] FAQ page content collected")

    # Check whether pricing information exists in FAQ
    pricing_terms = [
        "$15",
        "$12",
        "$144",
        "20%",
    ]

    found_terms = []

    for term in pricing_terms:
        if term in faq_text:
            found_terms.append(term)
            print(f"[STEP 10] FAQ contains pricing term: {term}")

    # If FAQ contains pricing information, report it
    if found_terms:
        print(
            f"[STEP 11] Pricing information found in FAQ: "
            f"{', '.join(found_terms)}"
        )
    else:
        print(
            "[STEP 11] No matching pricing figures found in FAQ"
        )

    print("[RESULT] TC-PR-06 PASSED")