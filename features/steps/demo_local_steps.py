"""
Step definitions for local demo tests
These tests verify the E2E framework is working without external dependencies
"""

from behave import given, when, then


@given('the test framework is initialized')
def step_framework_initialized(context):
    """Verify the framework is initialized"""
    assert hasattr(context, 'page'), "context.page should exist"
    assert hasattr(context, 'browser'), "context.browser should exist"
    assert hasattr(context, 'playwright'), "context.playwright should exist"
    print("✓ Framework properly initialized")


@then('the browser should be running')
def step_browser_running(context):
    """Verify browser is running"""
    assert context.browser is not None, "Browser should be running"
    print("✓ Browser is running")


@then('the page context should exist')
def step_page_context_exists(context):
    """Verify page context exists"""
    assert context.page is not None, "Page should exist"
    assert context.context is not None, "Browser context should exist"
    print("✓ Page context exists")


@when('I navigate to a local data URL')
def step_navigate_data_url(context):
    """Navigate to a simple data URL (no external dependencies)"""
    html_content = """
    <!DOCTYPE html>
    <html>
        <head><title>E2E Test Demo</title></head>
        <body>
            <h1>E2E Framework Working!</h1>
            <button id="testButton">Click Me</button>
            <input type="checkbox" id="testCheckbox">
            <p id="message">Framework is operational</p>
        </body>
    </html>
    """
    data_url = f"data:text/html;charset=utf-8,{html_content}"
    context.page.goto(data_url)
    context.current_url = data_url
    print("✓ Navigated to local data URL")


@then('the page should load successfully')
def step_page_loaded(context):
    """Verify page loaded"""
    title = context.page.title()
    assert "E2E Test Demo" in title, f"Expected title to contain 'E2E Test Demo', got '{title}'"
    print(f"✓ Page loaded with title: {title}")


@then('I should be able to interact with the page')
def step_can_interact(context):
    """Verify we can interact with page elements"""
    # Check button exists
    button = context.page.locator("#testButton")
    assert button.is_visible(), "Button should be visible"

    # Check checkbox exists
    checkbox = context.page.locator("#testCheckbox")
    assert checkbox.is_visible(), "Checkbox should be visible"

    # Interact with checkbox
    checkbox.check()
    assert checkbox.is_checked(), "Checkbox should be checked"

    # Check message exists
    message = context.page.locator("#message")
    assert "operational" in message.text_content(), "Message should be visible"

    print("✓ Successfully interacted with all page elements")
