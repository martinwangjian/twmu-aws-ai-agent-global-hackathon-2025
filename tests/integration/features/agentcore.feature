Feature: AgentCore Deployment and Invocation
  As a developer
  I want to deploy and test AgentCore runtime
  So that I can ensure the agent works correctly

  Background:
    Given AWS credentials are configured
    And the region is set to "us-east-1"

  Scenario: Deploy AgentCore runtime
    When I deploy AgentCore with entrypoint "src/agents/agentcore_mcp_agent.py"
    Then the deployment should succeed
    And the AgentCore runtime ARN should be saved
    And the runtime status should be "ACTIVE"

  Scenario: Invoke AgentCore with simple prompt
    Given AgentCore runtime is deployed
    When I invoke the agent with prompt "What is 2+2?"
    Then the response should contain "4"
    And the response status should be "success"

  Scenario: Invoke AgentCore with AWS question
    Given AgentCore runtime is deployed
    When I invoke the agent with prompt "What is AWS Lambda in one sentence?"
    Then the response should contain "Lambda"
    And the response status should be "success"
    And the response time should be less than 30 seconds
