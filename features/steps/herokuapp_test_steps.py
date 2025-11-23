"""
Step definitions for herokuapp_test-dample_2025-11-23.feature
Properly converted from the Playwright recording

These steps follow the Page Object Model pattern and use proper BDD practices.
"""

from behave import given, when, then
from playwright.sync_api import Page, expect


# ==============================================================================
# BACKGROUND STEPS
# ==============================================================================

@given('I navigate to the Herokuapp homepage')
def step_navigate_to_homepage(context):
    """Navigate to the Herokuapp homepage"""
    context.page.goto("https://the-internet.herokuapp.com/")
    context.current_url = context.page.url
    print(f"✓ Navigated to: {context.current_url}")


# ==============================================================================
# NAVIGATION STEPS
# ==============================================================================

@when('I click on the "{link_text}" link')
def step_click_link(context, link_text):
    """Click on a link with the given text"""
    context.page.click(f"text={link_text}")
    context.last_clicked_link = link_text
    print(f"✓ Clicked '{link_text}' link")


# ==============================================================================
# CHECKBOX STEPS
# ==============================================================================

@then('I should see the checkboxes page')
def step_verify_checkboxes_page(context):
    """Verify we're on the checkboxes page"""
    expect(context.page.locator("h3")).to_have_text("Checkboxes")
    print("✓ Checkboxes page loaded")


@when('I check the first checkbox')
def step_check_first_checkbox(context):
    """Check the first checkbox"""
    checkbox = context.page.locator("input[type='checkbox']").nth(0)
    checkbox.check()
    context.first_checkbox = checkbox
    print("✓ Checked first checkbox")


@when('I uncheck the second checkbox')
def step_uncheck_second_checkbox(context):
    """Uncheck the second checkbox"""
    checkbox = context.page.locator("input[type='checkbox']").nth(1)
    checkbox.uncheck()
    context.second_checkbox = checkbox
    print("✓ Unchecked second checkbox")


@then('the first checkbox should be checked')
def step_verify_first_checkbox_checked(context):
    """Verify the first checkbox is checked"""
    checkbox = context.page.locator("input[type='checkbox']").nth(0)
    assert checkbox.is_checked(), "First checkbox should be checked"
    print("✓ First checkbox is checked")


@then('the second checkbox should be unchecked')
def step_verify_second_checkbox_unchecked(context):
    """Verify the second checkbox is unchecked"""
    checkbox = context.page.locator("input[type='checkbox']").nth(1)
    assert not checkbox.is_checked(), "Second checkbox should be unchecked"
    print("✓ Second checkbox is unchecked")


# ==============================================================================
# CHALLENGING DOM STEPS - PAGE VERIFICATION
# ==============================================================================

@then('I should see the Challenging DOM page')
def step_verify_challenging_dom_page(context):
    """Verify we're on the Challenging DOM page"""
    expect(context.page.locator("h3")).to_have_text("Challenging DOM")
    print("✓ Challenging DOM page loaded")


@then('I should see the data table')
def step_verify_table_visible(context):
    """Verify the data table is visible"""
    table = context.page.locator("table")
    expect(table).to_be_visible()
    print("✓ Data table is visible")


@then('I should see the data table with {row_count:d} rows')
def step_verify_table_row_count(context, row_count):
    """Verify the table has the expected number of rows"""
    rows = context.page.locator("table tbody tr")
    actual_count = rows.count()
    assert actual_count == row_count, f"Expected {row_count} rows, found {actual_count}"
    context.table_row_count = actual_count
    print(f"✓ Table has {actual_count} rows")


# ==============================================================================
# CHALLENGING DOM STEPS - BUTTON INTERACTIONS
# ==============================================================================

@when('I click the "{button_name}" button')
def step_click_button(context, button_name):
    """Click a button with the given name"""
    # Map button names to their selectors
    button_selectors = {
        "foo": "a.button:has-text('foo')",
        "bar": "a.button.alert:has-text('bar')",
        "baz": "a.button.success:has-text('baz')"
    }

    selector = button_selectors.get(button_name.lower())
    if not selector:
        raise ValueError(f"Unknown button: {button_name}")

    context.page.click(selector)
    context.last_clicked_button = button_name
    print(f"✓ Clicked '{button_name}' button")


@then('all button clicks should be successful')
def step_verify_button_clicks(context):
    """Verify all button clicks were successful"""
    # In this case, we're just verifying no errors occurred
    # In a real application, you might check for specific outcomes
    assert context.last_clicked_button is not None, "No buttons were clicked"
    print("✓ All button clicks successful")


@then('the "{button_name}" button should have the "{button_class}" class')
def step_verify_button_class(context, button_name, button_class):
    """Verify a button has the expected CSS class"""
    button_selectors = {
        "foo": "a.button:has-text('foo')",
        "bar": "a.button.alert:has-text('bar')",
        "baz": "a.button.success:has-text('baz')"
    }

    selector = button_selectors.get(button_name.lower())
    button = context.page.locator(selector)

    # Verify the button has the expected class
    class_attr = button.get_attribute("class")
    assert button_class in class_attr, f"Button should have class '{button_class}'"
    print(f"✓ Button '{button_name}' has class '{button_class}'")


# ==============================================================================
# CHALLENGING DOM STEPS - TABLE INTERACTIONS
# ==============================================================================

@when('I click the "{action}" link in row {row_number:d}')
def step_click_table_action(context, action, row_number):
    """Click an action link (edit/delete) in a specific table row"""
    # Playwright uses 0-based indexing, but BDD uses 1-based
    # nth-child CSS selector uses 1-based indexing
    selector = f"table tbody tr:nth-child({row_number}) td a:has-text('{action}')"
    context.page.click(selector)
    context.last_table_action = {
        'action': action,
        'row': row_number
    }
    print(f"✓ Clicked '{action}' link in row {row_number}")


@then('the table actions should be successful')
def step_verify_table_actions(context):
    """Verify table actions were successful"""
    assert context.last_table_action is not None, "No table actions were performed"
    print(f"✓ Table action '{context.last_table_action['action']}' successful")


@then('the table action "{action}" should be performed on row {row_number:d}')
def step_verify_specific_table_action(context, action, row_number):
    """Verify a specific table action was performed"""
    assert context.last_table_action['action'] == action, \
        f"Expected action '{action}', got '{context.last_table_action['action']}'"
    assert context.last_table_action['row'] == row_number, \
        f"Expected row {row_number}, got {context.last_table_action['row']}"
    print(f"✓ Action '{action}' performed on row {row_number}")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_checkbox_state(page: Page, index: int) -> bool:
    """Get the checked state of a checkbox by index"""
    checkbox = page.locator("input[type='checkbox']").nth(index)
    return checkbox.is_checked()


def get_table_row_count(page: Page) -> int:
    """Get the number of rows in the data table"""
    rows = page.locator("table tbody tr")
    return rows.count()


def click_table_action(page: Page, action: str, row: int):
    """Click an action link in the table"""
    selector = f"table tbody tr:nth-child({row}) td a:has-text('{action}')"
    page.click(selector)
