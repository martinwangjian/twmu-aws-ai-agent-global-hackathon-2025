# Scripts Reference

All scripts in `scripts/` directory.

## Deployment Scripts

### `deploy.sh`

**Purpose**: Deploy everything (AgentCore + CDK)

**Usage**:

```bash
./scripts/deploy.sh
```

**What it does**:

1. Checks if AgentCore exists (`.agentcore-runtime-arn`)
2. If not, deploys AgentCore via Starter Toolkit
3. Deploys CDK stacks (WhatsAppStack)
4. Shows deployment outputs

**Environment**:

- `AWS_REGION` (default: `us-east-1`)

**Outputs**:

- `.agentcore-runtime-arn` file
- CDK stack outputs

---

### `test.sh`

**Purpose**: Test WhatsApp integration

**Usage**:

```bash
./scripts/test.sh
```

**What it does**:

1. Reads CDK outputs (SNS topic, Lambda name)
2. Sends 3 test messages via SNS
3. Shows Lambda logs with AI responses

**Requirements**:

- Stack must be deployed
- AWS credentials configured

---

### `cleanup.sh`

**Purpose**: Delete all resources

**Usage**:

```bash
./scripts/cleanup.sh
```

**What it does**:

1. Asks for confirmation
2. Deletes CDK stacks
3. Deletes AgentCore runtime
4. Removes `.agentcore-runtime-arn` file

**Warning**: Destructive operation!

---

## Development Scripts

### `init-dev-env.sh`

**Purpose**: Initialize development environment

**Usage**:

```bash
./scripts/init-dev-env.sh
```

**What it does**:

1. Checks if `uv` is installed
2. Runs `uv sync --all-extras`
3. Installs pre-commit hooks

**Requirements**:

- `uv` installed

---

### `generate-diagrams.sh`

**Purpose**: Generate architecture diagrams

**Usage**:

```bash
./scripts/generate-diagrams.sh
```

**What it does**:

- Shows instructions for generating diagrams with AWS Diagram MCP
- Lists diagram types to generate

**Output**: `docs/architecture/diagrams/*.png`

---

## Script Patterns

### Error Handling

All scripts use `set -e` to exit on error.

### Environment Variables

Scripts read from `.env` file if present:

```bash
if [ -f .env ]; then
    export $(cat .env | xargs)
fi
```

### Region Configuration

Default region is `us-east-1`:

```bash
REGION="${AWS_REGION:-us-east-1}"
```

### Idempotency

Scripts are safe to run multiple times:

- `deploy.sh` checks if AgentCore exists
- `cleanup.sh` handles missing resources gracefully

---

## Related Documentation

- [Deployment Guide](../guides/deployment.md)
- [Testing Guide](../guides/testing.md)
- [Environment Variables](environment-variables.md)
