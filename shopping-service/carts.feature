Feature: Post
  A service that allows you to post entries.

  Scenario: Get a cart
    Given I have cart ID 1
    When I fetch this cart
    Then I get back the cart with ID 1
    And A non-empty title
