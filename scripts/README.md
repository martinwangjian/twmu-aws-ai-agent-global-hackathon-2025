# Deployment Scripts

This directory contains automation scripts for the AWS AI Agent project.

## Scripts

### `deploy-agentcore.sh`

Automated deployment script for the entire AgentCore + CDK infrastructure.

**What it does:**

- Checks prerequisites (Python, Node, Docker, AWS CLI)
- Initializes CDK Python project
- Creates CDK stack files (Lambda invoker, ECR integration)
- Builds ARM64 Docker image for AgentCore
- Pushes image to Amazon ECR
- Deploys CDK stack (Lambda + Function URL)
- Creates AgentCore runtime with container
- Updates Lambda environment variables
- Tests the deployment

**Prerequisites:**

- AWS CLI configured with credentials
- Docker with buildx support
- Node.js and npm (for CDK)
- Python 3.12+
- IAM role named `AgentCoreRuntimeRole` with permissions:
  - `bedrock:InvokeModel`
  - `logs:CreateLogGroup`
  - `logs:CreateLogStream`
  - `logs:PutLogEvents`

**Usage:**

```bash
# Basic usage (uses defaults)
./scripts/deploy-agentcore.sh

# With custom configuration
export AWS_REGION=us-east-1
export AGENT_NAME=my-booking-agent
./scripts/deploy-agentcore.sh
```

**Estimated Time:** ~10-15 minutes
