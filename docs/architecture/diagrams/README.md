# Architecture Diagrams

This directory contains architecture diagrams for the AWS AI Agent Booking Bot.

## Diagrams

### 1. System Overview (`system-overview.png`)

**Description**: High-level end-to-end architecture

**Components**:

- User (WhatsApp client)
- AWS End User Messaging (Social)
- Amazon SNS (WhatsAppMessages topic)
- AWS Lambda (Orchestrator)
- Amazon Bedrock AgentCore (Runtime)
- Amazon Bedrock (Nova Pro LLM)

**Flow**: User → WhatsApp → AWS End User Messaging → SNS → Lambda → AgentCore → Bedrock

---

### 2. WhatsApp Flow (`whatsapp-flow.png`)

**Description**: Detailed WhatsApp message processing pipeline

**Components**:

- WhatsApp Message (inbound)
- AWS End User Messaging (Social)
- SNS Topic (WhatsAppMessages)
- Lambda Orchestrator
  - Parse webhook
  - Mark as read
  - Invoke AgentCore
  - Send reply
- AgentCore Runtime
  - Strands Agent
  - MCP Tools
  - Bedrock LLM
- WhatsApp Message (outbound)

**Flow**: Bidirectional message flow with processing steps

---

### 3. AgentCore Runtime (`agentcore-runtime.png`)

**Description**: Internal AgentCore architecture

**Components**:

- AgentCore Runtime Container
  - Strands Agent Framework
  - MCP Client
    - AWS Documentation MCP Server
    - Other MCP Servers
  - Bedrock Integration
    - Nova Pro Model
    - Claude Models (optional)

**Flow**: Agent → MCP Tools → Bedrock → Response

---

### 4. Deployment Pipeline (`deployment-pipeline.png`)

**Description**: Deployment process flow

**Components**:

- Developer
- `./scripts/deploy.sh`
  - Step 1: Deploy AgentCore
    - `agentcore configure`
    - `agentcore launch`
    - Save ARN to file
  - Step 2: Deploy CDK
    - WhatsAppStack
      - SNS Topic
      - Lambda Orchestrator
      - Secrets Manager
      - Event Destination Config
    - Outputs (ARNs)

**Flow**: Developer → Script → AWS Resources

---

## Generating Diagrams

### Option 1: AWS Diagram MCP (Recommended)

If you have AWS Diagram MCP configured:

```bash
# Use Amazon Q to generate diagrams
q chat
```

Then ask:

1. "Generate AWS architecture diagram for system overview showing User → WhatsApp → AWS End User Messaging → SNS → Lambda → AgentCore → Bedrock"
2. "Generate detailed WhatsApp message flow diagram with Lambda orchestrator processing steps"
3. "Generate AgentCore runtime architecture diagram showing Strands Agent, MCP Client, and Bedrock integration"
4. "Generate deployment pipeline diagram showing deploy.sh steps"

### Option 2: Manual Creation

Use tools like:

- AWS Architecture Icons
- draw.io
- Lucidchart
- CloudCraft

### Option 3: Code-based (Python)

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import SNS
from diagrams.aws.ml import Bedrock
# ... etc
```

---

## Updating Diagrams

When architecture changes:

1. Update diagram specifications above
2. Regenerate diagrams
3. Update references in documentation
4. Commit changes

**Last Updated**: 2025-10-08
