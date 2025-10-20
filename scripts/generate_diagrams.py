#!/usr/bin/env python3
"""Generate AWS architecture diagrams."""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import SNS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Bedrock
from diagrams.aws.network import APIGateway
from diagrams.aws.security import SecretsManager
from diagrams.onprem.client import Users

# System Architecture
with Diagram(
    "System Architecture", filename="docs/diagrams/system-architecture", show=False, direction="LR"
):
    user = Users("WhatsApp User")

    with Cluster("AWS Cloud"):
        with Cluster("Messaging Layer"):
            whatsapp = APIGateway("WhatsApp\nChannel")
            sns = SNS("Message\nTopic")

        with Cluster("Processing Layer"):
            orchestrator = Lambda("WhatsApp\nOrchestrator")
            secrets = SecretsManager("Credentials")

        with Cluster("AI Layer"):
            agentcore = Bedrock("AgentCore\nRuntime")
            model = Bedrock("Nova Pro\nv1")

        with Cluster("Observability"):
            logs = Cloudwatch("CloudWatch\nLogs")
            xray = Cloudwatch("X-Ray\nTracing")

    user >> Edge(label="message") >> whatsapp
    whatsapp >> Edge(label="event") >> sns
    sns >> Edge(label="trigger") >> orchestrator
    orchestrator >> Edge(label="invoke") >> agentcore
    agentcore >> Edge(label="inference") >> model
    orchestrator >> Edge(label="get") >> secrets
    orchestrator >> Edge(label="reply") >> whatsapp
    orchestrator >> logs
    orchestrator >> xray

# WhatsApp Flow
with Diagram(
    "WhatsApp Message Flow", filename="docs/diagrams/whatsapp-flow", show=False, direction="TB"
):
    user = Users("Customer")

    with Cluster("AWS"):
        whatsapp = APIGateway("WhatsApp")
        sns = SNS("SNS Topic")
        lambda_fn = Lambda("Orchestrator")
        agentcore = Bedrock("AgentCore")

    user >> Edge(label="1. Send message") >> whatsapp
    whatsapp >> Edge(label="2. Publish") >> sns
    sns >> Edge(label="3. Trigger") >> lambda_fn
    lambda_fn >> Edge(label="4. Invoke") >> agentcore
    agentcore >> Edge(label="5. Response") >> lambda_fn
    lambda_fn >> Edge(label="6. Reply") >> whatsapp
    whatsapp >> Edge(label="7. Deliver") >> user

# AgentCore Integration
with Diagram(
    "AgentCore Integration",
    filename="docs/diagrams/agentcore-integration",
    show=False,
    direction="LR",
):
    with Cluster("Lambda Function"):
        orchestrator = Lambda("Orchestrator")

    with Cluster("Bedrock AgentCore"):
        runtime = Bedrock("Runtime")
        agent = Bedrock("Strands Agent")

        with Cluster("MCP Tools"):
            tool1 = Bedrock("Tool 1")
            tool2 = Bedrock("Tool 2")

    with Cluster("Bedrock Models"):
        nova = Bedrock("Nova Pro v1")

    orchestrator >> Edge(label="invoke") >> runtime
    runtime >> Edge(label="execute") >> agent
    agent >> Edge(label="use") >> tool1
    agent >> Edge(label="use") >> tool2
    agent >> Edge(label="inference") >> nova

import sys

sys.stdout.write("✅ Diagrams generated successfully!\n")
sys.stdout.write("   - docs/diagrams/system-architecture.png\n")
sys.stdout.write("   - docs/diagrams/whatsapp-flow.png\n")
sys.stdout.write("   - docs/diagrams/agentcore-integration.png\n")
