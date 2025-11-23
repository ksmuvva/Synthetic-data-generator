# Feature file converted from: herokuapp_test-dample_2025-11-23.py
# This is the PROPER BDD conversion of the Playwright recording

Feature: Herokuapp Interactive Elements Testing
  As a QA tester
  I want to test various interactive elements on Herokuapp
  So that I can ensure they work correctly

  Background:
    Given I navigate to the Herokuapp homepage

  @checkboxes @smoke
  Scenario: Successfully interact with checkboxes
    When I click on the "Checkboxes" link
    Then I should see the checkboxes page
    When I check the first checkbox
    And I uncheck the second checkbox
    Then the first checkbox should be checked
    And the second checkbox should be unchecked

  @challenging-dom @buttons
  Scenario: Successfully interact with Challenging DOM buttons
    When I click on the "Challenging DOM" link
    Then I should see the Challenging DOM page
    And I should see the data table
    When I click the "foo" button
    And I click the "bar" button
    And I click the "baz" button
    Then all button clicks should be successful

  @challenging-dom @table
  Scenario: Successfully interact with table actions
    When I click on the "Challenging DOM" link
    Then I should see the Challenging DOM page
    And I should see the data table with 10 rows
    When I click the "edit" link in row 1
    And I click the "delete" link in row 1
    Then the table actions should be successful

  @end-to-end @full-flow
  Scenario: Complete workflow - Checkboxes and Challenging DOM
    # Part 1: Checkbox interaction
    When I click on the "Checkboxes" link
    And I check the first checkbox
    And I uncheck the second checkbox
    Then the first checkbox should be checked
    And the second checkbox should be unchecked

    # Part 2: Navigate to Challenging DOM
    When I navigate to the Herokuapp homepage
    And I click on the "Challenging DOM" link
    Then I should see the Challenging DOM page

    # Part 3: Button interactions
    When I click the "foo" button
    And I click the "bar" button
    And I click the "baz" button
    Then all button clicks should be successful

    # Part 4: Table interactions
    When I click the "edit" link in row 1
    And I click the "delete" link in row 1
    Then the table actions should be successful

  @parametrized @data-driven
  Scenario Outline: Interact with different Challenging DOM buttons
    When I click on the "Challenging DOM" link
    Then I should see the Challenging DOM page
    When I click the "<button_name>" button
    Then the "<button_name>" button should have the "<button_class>" class

    Examples:
      | button_name | button_class |
      | foo         | button       |
      | bar         | button alert |
      | baz         | button success |

  @parametrized @data-driven
  Scenario Outline: Perform table actions on different rows
    When I click on the "Challenging DOM" link
    Then I should see the Challenging DOM page
    When I click the "<action>" link in row <row_number>
    Then the table action "<action>" should be performed on row <row_number>

    Examples:
      | action | row_number |
      | edit   | 1          |
      | edit   | 2          |
      | delete | 1          |
      | delete | 3          |
