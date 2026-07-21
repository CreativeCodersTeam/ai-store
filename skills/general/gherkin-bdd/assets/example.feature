# language: en
@checkout
Feature: Checkout
  As a shopper
  I want to pay for the items in my cart
  So that I receive my order

  Background:
    Given the store sells "book" for 10

  Scenario: Pay for a single item
    Given the cart contains a "book"
    When the user checks out
    Then the order total is 10

  @discount
  Scenario Outline: Order total scales with quantity
    Given the cart contains <count> copies of "book"
    When the user checks out
    Then the order total is <total>

    Examples:
      | count | total |
      | 1     | 10    |
      | 5     | 45    |
      | 10    | 80    |
