"""
Environment configuration for Behave tests
This file MUST be located at: features/environment.py

CRITICAL: This file must be in the features/ directory, NOT in steps/
Behave looks for environment.py specifically in features/ to load hooks.
"""

from playwright.sync_api import sync_playwright


def before_all(context):
    """
    Runs once before all tests
    Initialize the browser and create the Playwright instance
    """
    print("\n🚀 Initializing test framework...")
    print("=" * 70)

    # Start Playwright
    context.playwright = sync_playwright().start()

    # Launch browser
    context.browser = context.playwright.chromium.launch(
        headless=True,   # Headless mode for CI/CD and server environments
        slow_mo=100      # Minimal slow down for stability
    )

    print(f"✅ Browser: chromium (headless: True)")
    print(f"✅ Base URL: https://the-internet.herokuapp.com/")
    print("=" * 70 + "\n")


def before_scenario(context, scenario):
    """
    Runs before each scenario
    Create a new page for each scenario to ensure isolation

    THIS IS WHERE context.page GETS CREATED!
    If this hook doesn't run, you'll get: AttributeError: 'Context' object has no attribute 'page'
    """
    print(f"\n📝 Scenario: {scenario.name}")
    print("-" * 70)

    # Create a new browser context for isolation
    context.context = context.browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (BDD Test) AppleWebKit/537.36',
        ignore_https_errors=True  # Ignore SSL certificate errors in test environments
    )

    # Create a new page
    context.page = context.context.new_page()

    # Initialize context variables for tracking
    context.current_url = None
    context.last_clicked_link = None
    context.last_clicked_button = None
    context.last_table_action = None
    context.first_checkbox = None
    context.second_checkbox = None
    context.table_row_count = None

    print("✅ New page created for scenario")


def after_step(context, step):
    """
    Runs after each step
    Useful for screenshots and logging
    """
    if step.status == "passed":
        print(f"  ✓ {step.name}")
    elif step.status == "failed":
        print(f"  ✗ {step.name}")
        # Capture screenshot on failure
        screenshot_name = f"failure_{step.name.replace(' ', '_')}.png"
        context.page.screenshot(path=f"screenshots/{screenshot_name}")
        print(f"  📸 Screenshot saved: {screenshot_name}")


def after_scenario(context, scenario):
    """
    Runs after each scenario
    Clean up the page and context
    """
    if scenario.status == "passed":
        print(f"\n✅ Scenario passed: {scenario.name}")
    elif scenario.status == "failed":
        print(f"\n❌ Scenario failed: {scenario.name}")

    # Close the page and context
    context.page.close()
    context.context.close()

    print("-" * 70)


def after_all(context):
    """
    Runs once after all tests
    Clean up the browser and Playwright instance
    """
    print("\n" + "=" * 70)
    print("🏁 Test execution complete")

    # Close browser
    context.browser.close()

    # Stop Playwright
    context.playwright.stop()

    print("✅ Browser closed")
    print("✅ Playwright stopped")
    print("=" * 70 + "\n")
