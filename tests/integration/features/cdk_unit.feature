Feature: CDK Stack Synthesis
  As a developer
  I want to verify CDK stack structure
  So that infrastructure is correctly defined

  Background:
    Given a CDK app with BookingAgentStack

  @unit
  Scenario: Stack synthesizes without errors
    When I synthesize the stack
    Then synthesis should succeed
    And the template should be valid CloudFormation

  @unit
  Scenario: Lambda function is defined correctly
    When I synthesize the stack
    Then the stack should contain 1 Lambda function
    And the Lambda should have runtime "python3.12"
    And the Lambda should have architecture "arm64"
    And the Lambda should have timeout 30 seconds
    And the Lambda should have memory 512 MB

  @unit
  Scenario: Lambda has correct IAM permissions
    When I synthesize the stack
    Then Lambda should have permission "bedrock-agentcore:InvokeAgentRuntime"
    And the permission should include runtime endpoint wildcard

  @unit
  Scenario: Lambda has Function URL
    When I synthesize the stack
    Then the stack should contain 1 Lambda Function URL
    And the Function URL should have auth type "NONE"

  @unit
  Scenario: Lambda has correct environment variables
    When I synthesize the stack
    Then Lambda should have environment variable "AGENTCORE_RUNTIME_ARN"
