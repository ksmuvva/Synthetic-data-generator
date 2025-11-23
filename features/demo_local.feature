# Demo Feature - Tests Local Data URLs (No External Dependencies)
# This demonstrates the E2E framework works without requiring external sites

Feature: E2E Framework Verification
  As a developer
  I want to verify the E2E testing framework is properly set up
  So that I can run tests successfully

  @demo @local
  Scenario: Framework initialization works correctly
    Given the test framework is initialized
    Then the browser should be running
    And the page context should exist

  @demo @local
  Scenario: Page navigation works with data URLs
    Given the test framework is initialized
    When I navigate to a local data URL
    Then the page should load successfully
    And I should be able to interact with the page
