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

    # ==========================================
    # STEP 1: Open Pricing page
    # ==========================================

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
    expect(
        page.get_by_text("$15", exact=True)
    ).to_be_visible()

    print("[STEP 4] Pricing page Monthly price verified: $15/month")

    # ==========================================
    # STEP 2: Open FAQ page
    # ==========================================

    page.goto("https://thaura.ai/faq")
    page.wait_for_timeout(2000)

    print("[STEP 5] FAQ page opened")

    # ==========================================
    # STEP 3: Open pricing FAQ
    # ==========================================

    pricing_question = page.get_by_text(
        "Why is your pricing set at $15?",
        exact=True
    )

    expect(pricing_question).to_be_visible()

    print("[STEP 6] Pricing FAQ question found")

    # Click FAQ question
    pricing_question.click()
    page.wait_for_timeout(1000)

    print("[STEP 7] Pricing FAQ question expanded")

    # ==========================================
    # STEP 4: Verify FAQ answer
    # ==========================================

    faq_answer = page.get_by_text(
        "We deliberately set our pricing at $15 when competitors charge $20 to provide an ethical, affordable alternative. These rates represent the minimum we need to operate effectively while maintaining our independence.",
        exact=True
    )

    expect(faq_answer).to_be_visible()

    print("[STEP 8] FAQ pricing answer verified")

    # ==========================================
    # STEP 5: Verify FAQ mentions $15
    # ==========================================

    faq_text = faq_answer.inner_text()

    assert "$15" in faq_text, (
        "FAQ answer does not contain expected $15 pricing"
    )

    print("[STEP 9] FAQ answer contains $15 pricing")

    # ==========================================
    # STEP 6: Final consistency check
    # ==========================================

    pricing_monthly_price = 15
    faq_price = 15

    print(
        f"[STEP 10] Pricing page Monthly price: "
        f"${pricing_monthly_price}/month"
    )

    print(
        f"[STEP 11] FAQ stated price: "
        f"${faq_price}"
    )

    assert pricing_monthly_price == faq_price, (
        f"Pricing mismatch: Pricing page=${pricing_monthly_price}, "
        f"FAQ=${faq_price}"
    )

    print("[STEP 12] Pricing page and FAQ pricing are consistent")

    print("[RESULT] TC-PR-06 PASSED")

def test_pr_07_no_outdated_pricing(page: Page) -> None:

    print("\n[TC-PR-07] Starting No Outdated Pricing Test")

    # ==========================================
    # STEP 1: Open Pricing page
    # ==========================================

    page.goto("https://thaura.ai/pricing")
    page.wait_for_timeout(2000)

    print("[STEP 1] Pricing page opened")

    # ==========================================
    # STEP 2: Verify Monthly pricing
    # ==========================================

    page.get_by_role("button", name="View Plans").click()
    page.wait_for_timeout(1500)

    print("[STEP 2] View Plans clicked")

    page.get_by_role("tab", name="Monthly").click()
    page.wait_for_timeout(1000)

    print("[STEP 3] Monthly plan selected")

    expect(
        page.get_by_text("$15", exact=True)
    ).to_be_visible()

    print("[STEP 4] Current Monthly price verified: $15/month")

    # ==========================================
    # STEP 3: Verify Annual pricing
    # ==========================================

    page.get_by_role("tab", name="Annual Save 20%").click()
    page.wait_for_timeout(1000)

    print("[STEP 5] Annual plan selected")

    expect(
        page.get_by_text("$12", exact=True)
    ).to_be_visible()

    expect(
        page.get_by_text("Billed $144/year", exact=True)
    ).to_be_visible()

    print("[STEP 6] Current Annual price verified: $12/month")
    print("[STEP 7] Current Annual billing verified: $144/year")

    # ==========================================
    # STEP 4: Check FAQ pricing references
    # ==========================================

    page.goto("https://thaura.ai/faq")
    page.wait_for_timeout(2000)

    print("[STEP 8] FAQ page opened")

    faq_text = page.locator("body").inner_text()

    print("[STEP 9] FAQ page content collected")

    # FAQ legitimately references $15 pricing
    expect(
        page.get_by_text(
            "Why is your pricing set at $15?",
            exact=True
        )
    ).to_be_visible()

    print("[STEP 10] FAQ contains legitimate $15 pricing reference")

    # ==========================================
    # STEP 5: Check for outdated pricing values
    # ==========================================

    outdated_prices = [
        "$10/month",
        "$20/month",
        "$18/month",
        "$144/month",
        "$180/month"
    ]

    found_outdated_prices = []

    for price in outdated_prices:
        if price in faq_text:
            found_outdated_prices.append(price)
            print(
                f"[STEP 11] Potential outdated pricing found: {price}"
            )

    # ==========================================
    # STEP 6: Final validation
    # ==========================================

    assert not found_outdated_prices, (
        "Potential outdated pricing found in FAQ: "
        + ", ".join(found_outdated_prices)
    )

    print("[STEP 12] No outdated pricing references found in FAQ")

    print("[RESULT] TC-PR-07 PASSED")