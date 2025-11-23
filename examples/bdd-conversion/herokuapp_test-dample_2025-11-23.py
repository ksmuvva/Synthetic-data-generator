"""
Playwright Recording: herokuapp_test-dample_2025-11-23.py
Generated: 2025-11-23
URL: https://the-internet.herokuapp.com/

This is a RAW Playwright recording that needs to be converted to BDD format.
"""

from playwright.sync_api import sync_playwright


def run():
    """
    Raw Playwright recording showing:
    1. Navigation to Herokuapp
    2. Clicking checkboxes
    3. Navigating to "Challenging DOM"
    4. Clicking various buttons (foo, bar, baz)
    """
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the homepage
        page.goto("https://the-internet.herokuapp.com/")
        print("✓ Navigated to Herokuapp homepage")

        # Click on Checkboxes link
        page.click("text=Checkboxes")
        print("✓ Clicked 'Checkboxes' link")

        # Interact with checkboxes
        # First checkbox (unchecked by default)
        checkbox1 = page.locator("input[type='checkbox']").nth(0)
        checkbox1.check()
        print("✓ Checked first checkbox")

        # Second checkbox (checked by default)
        checkbox2 = page.locator("input[type='checkbox']").nth(1)
        checkbox2.uncheck()
        print("✓ Unchecked second checkbox")

        # Verify checkbox states
        assert checkbox1.is_checked(), "First checkbox should be checked"
        assert not checkbox2.is_checked(), "Second checkbox should be unchecked"
        print("✓ Verified checkbox states")

        # Navigate back to homepage
        page.goto("https://the-internet.herokuapp.com/")
        print("✓ Navigated back to homepage")

        # Click on Challenging DOM link
        page.click("text=Challenging DOM")
        print("✓ Clicked 'Challenging DOM' link")

        # Click the "foo" button (blue button)
        page.click("a.button:has-text('foo')")
        print("✓ Clicked 'foo' button")

        # Click the "bar" button (red button)
        page.click("a.button.alert:has-text('bar')")
        print("✓ Clicked 'bar' button")

        # Click the "baz" button (green button)
        page.click("a.button.success:has-text('baz')")
        print("✓ Clicked 'baz' button")

        # Verify table exists
        table = page.locator("table")
        assert table.is_visible(), "Table should be visible"
        print("✓ Verified table is visible")

        # Get row count
        rows = page.locator("table tbody tr")
        row_count = rows.count()
        print(f"✓ Table has {row_count} rows")

        # Click edit and delete links in first row
        page.click("table tbody tr:nth-child(1) td a:has-text('edit')")
        print("✓ Clicked 'edit' link in first row")

        # Wait a moment to see the action
        page.wait_for_timeout(1000)

        page.click("table tbody tr:nth-child(1) td a:has-text('delete')")
        print("✓ Clicked 'delete' link in first row")

        # Wait a moment before closing
        page.wait_for_timeout(2000)

        print("\n✅ Recording complete!")

        # Cleanup
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
