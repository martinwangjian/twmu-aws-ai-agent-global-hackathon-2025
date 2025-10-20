Feature: CDK Stack Deployment
  As a developer
  I want to deploy infrastructure to AWS
  So that I can verify it works in real environment

  Background:
    Given AWS credentials are configured
    And the region is set to "us-east-1"
    And AgentCore runtime is deployed

  @integration
  Scenario: Deploy stack successfully
    When I deploy the CDK stack
    Then the stack should be in "CREATE_COMPLETE" or "UPDATE_COMPLETE" status
    And the stack should have outputs

  @integration
  Scenario: Lambda function exists in AWS
    Given the CDK stack is deployed
    Then Lambda function should exist in AWS
    And Lambda should have tag "aws:cloudformation:stack-name"

  @integration
  Scenario: Lambda has correct configuration
    Given the CDK stack is deployed
    Then Lambda runtime should be "python3.12"
    And Lambda architecture should be "arm64"
    And Lambda timeout should be 30 seconds
    And Lambda memory should be 512 MB

  @integration
  Scenario: Lambda has correct environment variables
    Given the CDK stack is deployed
    Then Lambda should have environment variable "AGENTCORE_RUNTIME_ARN"
    And the ARN should start with "arn:aws:bedrock-agentcore:us-east-1"

  @integration
  Scenario: Function URL is accessible
    Given the CDK stack is deployed
    Then Function URL should be in stack outputs
    And Function URL should be accessible via HTTPS
