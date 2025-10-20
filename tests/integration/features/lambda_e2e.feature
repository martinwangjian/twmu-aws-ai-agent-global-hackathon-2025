Feature: Lambda to AgentCore Integration
  As a user
  I want to invoke the agent via Lambda
  So that I can get AI responses

  Background:
    Given the infrastructure is deployed
    And the Function URL is available

  @e2e
  Scenario: Invoke Lambda with math question
    When I POST to Function URL with prompt "What is 15+25?"
    Then the HTTP status should be 200
    And the response should be valid JSON
    And the response should contain "40"
    And the response status should be "success"

  @e2e
  Scenario: Invoke Lambda with AWS question
    When I POST to Function URL with prompt "What is AWS Lambda?"
    Then the HTTP status should be 200
    And the response should contain "Lambda"
    And the response status should be "success"
    And the response time should be less than 10 seconds

  @e2e
  Scenario: Lambda handles empty prompt
    When I POST to Function URL with prompt ""
    Then the HTTP status should be 200
    And the response should be valid JSON

  @e2e
  Scenario: Lambda handles malformed request
    When I POST to Function URL with invalid JSON
    Then the HTTP status should be 500
