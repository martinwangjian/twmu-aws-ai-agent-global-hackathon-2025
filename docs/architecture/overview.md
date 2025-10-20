# Architecture Documentation

## Overview

This document describes the architecture of the AWS AI Agent WhatsApp Booking Bot for the AWS AI Agent Global Hackathon 2025.

## System Architecture

![System Architecture](diagrams/system-architecture.png)

### Components

#### Messaging Layer

- **WhatsApp Channel**: AWS End User Messaging (Social) integration
- **SNS Topic**: Message routing and event distribution

#### Processing Layer

- **WhatsApp Orchestrator**: Lambda function handling message processing
- **Secrets Manager**: Secure storage for WhatsApp credentials

#### AI Layer

- **AgentCore Runtime**: Amazon Bedrock AgentCore for agent execution
- **Nova Pro v1**: LLM model for natural language understanding

#### Observability

- **CloudWatch Logs**: Centralized logging
- **X-Ray Tracing**: Distributed tracing for performance monitoring

## WhatsApp Message Flow

![WhatsApp Flow](diagrams/whatsapp-flow.png)

### Flow Steps

1. **Customer sends message** via WhatsApp
2. **WhatsApp publishes event** to SNS Topic
3. **SNS triggers** Lambda Orchestrator
4. **Orchestrator invokes** AgentCore Runtime
5. **AgentCore returns** AI-generated response
6. **Orchestrator sends reply** to WhatsApp
7. **WhatsApp delivers** message to customer

## AgentCore Integration

![AgentCore Integration](diagrams/agentcore-integration.png)

### Integration Details

- **Lambda Orchestrator**: Entry point for WhatsApp messages
- **AgentCore Runtime**: Manages agent lifecycle and execution
- **Strands Agent**: Custom agent implementation with MCP tools
- **MCP Tools**: Extensible tool integration (future: calendar, payments)
- **Nova Pro v1**: Foundation model for reasoning and responses

## Technology Stack

### AWS Services

- **Amazon Bedrock AgentCore**: Agent runtime and orchestration
- **Amazon Bedrock (Nova Pro v1)**: LLM inference
- **AWS Lambda**: Serverless compute
- **AWS End User Messaging**: WhatsApp integration
- **Amazon SNS**: Event-driven messaging
- **AWS Secrets Manager**: Credential management
- **Amazon CloudWatch**: Logging and monitoring
- **AWS X-Ray**: Distributed tracing

### Frameworks & Libraries

- **Strands Agents**: AI agent framework
- **AWS CDK**: Infrastructure as Code
- **Python 3.11+**: Primary language
- **uv**: Fast dependency management

## Deployment Architecture

### Region

- **Primary**: us-east-1 (only supported region for AgentCore)

### Infrastructure as Code

- **AWS CDK**: Python-based infrastructure definitions
- **Custom Resources**: AgentCore runtime deployment

### CI/CD

- **GitHub Actions**: Automated testing
- **Pre-commit Hooks**: Code quality checks

## Security Architecture

### Authentication & Authorization

- **IAM Roles**: Least-privilege access
- **Secrets Manager**: Credential storage
- **GitHub Secrets**: CI/CD credentials

### Monitoring & Compliance

- **CloudWatch Logs**: Audit trail
- **X-Ray Tracing**: Request tracking
- **Pre-commit Hooks**: Secret detection

## Scalability

### Current Capacity

- **Lambda**: Auto-scaling up to account limits
- **SNS**: Unlimited message throughput
- **AgentCore**: Managed by AWS

### Future Enhancements

- **Multi-region**: Expand beyond us-east-1
- **Caching**: Redis for session management
- **Queue**: SQS for message buffering

## Cost Optimization

### Pay-per-use Services

- Lambda invocations
- Bedrock model inference
- SNS messages
- CloudWatch logs

### Cost Monitoring

- AWS Cost Explorer
- CloudWatch billing alarms
- Resource tagging

## Disaster Recovery

### Backup Strategy

- **Code**: Git repository
- **Infrastructure**: CDK definitions
- **Secrets**: Secrets Manager replication

### Recovery Time Objective (RTO)

- **Infrastructure**: < 30 minutes (CDK redeploy)
- **Data**: N/A (stateless architecture)

## Performance

### Latency Targets

- **WhatsApp → Lambda**: < 1 second
- **Lambda → AgentCore**: < 3 seconds
- **Total response time**: < 5 seconds

### Monitoring

- X-Ray service map
- CloudWatch metrics
- Lambda insights

## Compliance

### Data Privacy

- **AGPL-3.0 License**: Open source with copyleft
- **No PII storage**: Stateless processing
- **Encryption**: In-transit and at-rest

### AWS Best Practices

- Well-Architected Framework
- Security best practices
- Cost optimization

---

**Last Updated**: 2025-10-08
**Version**: 1.0
**Team**: Teamwork Mauritius
