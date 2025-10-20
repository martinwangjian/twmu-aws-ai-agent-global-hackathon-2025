# Architecture Diagrams (Mermaid)

Diagrams in Mermaid format for easy rendering in GitHub/GitLab.

## 1. System Overview

```mermaid
graph LR
    A[WhatsApp User] -->|Message| B[AWS End User Messaging]
    B -->|Webhook| C[SNS Topic]
    C -->|Event| D[Lambda Orchestrator]
    D -->|Invoke| E[AgentCore Runtime]
    E -->|LLM Call| F[Bedrock Nova Pro]
    F -->|Response| E
    E -->|Response| D
    D -->|Reply| B
    B -->|Deliver| A

    style A fill:#25D366
    style B fill:#FF9900
    style C fill:#FF9900
    style D fill:#FF9900
    style E fill:#FF9900
    style F fill:#FF9900
```

## 2. WhatsApp Message Flow

```mermaid
sequenceDiagram
    participant User as WhatsApp User
    participant EUM as AWS End User Messaging
    participant SNS as SNS Topic
    participant Lambda as Lambda Orchestrator
    participant AC as AgentCore Runtime
    participant Bedrock as Bedrock LLM

    User->>EUM: 1. Send WhatsApp Message
    EUM->>SNS: 2. Publish Webhook Event
    SNS->>Lambda: 3. Trigger Lambda
    Lambda->>Lambda: 4. Parse Webhook
    Lambda->>EUM: 5. Mark Message as Read
    Lambda->>AC: 6. Invoke AgentCore
    AC->>Bedrock: 7. Call LLM
    Bedrock-->>AC: 8. LLM Response
    AC-->>Lambda: 9. Agent Response
    Lambda->>EUM: 10. Send Reply
    EUM->>User: 11. Deliver Reply
```

## 3. AgentCore Runtime Architecture

```mermaid
graph TB
    subgraph AgentCore["AgentCore Runtime"]
        subgraph Strands["Strands Agent Framework"]
            Agent[Agent Logic]
        end

        subgraph MCP["MCP Client"]
            MCPClient[MCP Client]
            MCPAWS[AWS Docs MCP]
            MCPOther[Other MCP Servers]
        end

        subgraph Bedrock["Bedrock Integration"]
            Nova[Nova Pro]
            Claude[Claude Optional]
        end

        Agent --> MCPClient
        MCPClient --> MCPAWS
        MCPClient --> MCPOther
        Agent --> Nova
        Agent -.-> Claude
    end

    style Agent fill:#FF9900
    style MCPClient fill:#FF9900
    style Nova fill:#FF9900
```

## 4. Deployment Pipeline

```mermaid
graph LR
    Dev[Developer] -->|Run| Deploy[./scripts/deploy.sh]

    subgraph Step1["Step 1: AgentCore"]
        Configure[agentcore configure]
        Launch[agentcore launch]
        SaveARN[Save ARN to file]
    end

    subgraph Step2["Step 2: CDK"]
        CDKDeploy[cdk deploy]
    end

    subgraph AWS["AWS Resources"]
        AC[AgentCore Runtime]

        subgraph Stack["WhatsAppStack"]
            SNS[SNS Topic]
            Lambda[Lambda Orchestrator]
            Secrets[Secrets Manager]
        end
    end

    Deploy --> Configure
    Configure --> Launch
    Launch --> SaveARN
    SaveARN --> AC

    Deploy --> CDKDeploy
    CDKDeploy --> SNS
    CDKDeploy --> Lambda
    CDKDeploy --> Secrets

    style Dev fill:#4CAF50
    style Deploy fill:#2196F3
    style AC fill:#FF9900
    style SNS fill:#FF9900
    style Lambda fill:#FF9900
    style Secrets fill:#FF9900
```

## 5. Data Flow

```mermaid
graph TD
    A[WhatsApp Message] -->|JSON| B{Parse Webhook}
    B -->|Extract| C[Phone Number]
    B -->|Extract| D[Message Text]
    B -->|Extract| E[Message ID]

    C --> F[Session ID]
    D --> F
    E --> G[Mark as Read]

    F -->|Invoke| H[AgentCore]
    H -->|Prompt| I[Bedrock LLM]
    I -->|Response| J[AI Reply]

    J -->|Format| K[WhatsApp Message]
    K -->|Send| L[AWS End User Messaging]
    L -->|Deliver| M[WhatsApp User]

    style A fill:#25D366
    style H fill:#FF9900
    style I fill:#FF9900
    style M fill:#25D366
```

---

## Rendering

These diagrams render automatically on:

- GitHub
- GitLab
- VS Code (with Mermaid extension)
- Documentation sites (MkDocs, Docusaurus, etc.)

## Exporting to PNG

### Option 1: Mermaid CLI

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams.md -o system-overview.png
```

### Option 2: Online

Visit: https://mermaid.live/

### Option 3: VS Code

1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Right-click diagram → Export to PNG

---

**Last Updated**: 2025-10-08
