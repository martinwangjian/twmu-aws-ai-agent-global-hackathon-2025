# Getting Started

**Time**: 5 minutes
**Prerequisites**: Python 3.11+, AWS account, uv installed

## Quick Setup

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv
```

### 2. Clone and Setup

```bash
git clone <repository-url>
cd aws-ai-agent-global-hackathon-2025

# Initialize environment (one command!)
./scripts/init-dev-env.sh
```

This will:

- Create `.venv/` virtual environment
- Install all dependencies
- Set up pre-commit hooks

### 3. Configure AWS

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:

```bash
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_SESSION_TOKEN=your-token  # For temporary credentials
AWS_REGION=us-east-1
```

### 4. Deploy

```bash
./scripts/deploy.sh
```

This deploys:

- AgentCore runtime
- WhatsApp integration stack

### 5. Test

```bash
./scripts/test.sh
```

### 6. A2A Setup (Optional - for Claude Desktop)

For agent-to-agent communication via Claude Desktop:

```bash
# Get 60-day refresh token
./scripts/get_refresh_token_direct.sh

# Update Claude Desktop config
./scripts/update-claude-config.sh

# Restart Claude Desktop
```

**Benefits:**

- 60-day token validity (no manual updates)
- No AWS credentials in Claude config
- Auto-refresh with 5-minute buffer

## What's Next?

- **[Architecture Overview](../architecture/overview.md)** - Understand the system
- **[Development Guide](development.md)** - Start developing
- **[Testing Guide](testing.md)** - Write tests

## Troubleshooting

### uv not found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell
exec $SHELL
```

### AWS credentials expired

```bash
# Update .env with new credentials
nano .env

# Reload
source .env
```

### Deployment fails

See **[Troubleshooting Guide](troubleshooting.md)** for common issues.

---

**Related**:

- [Deployment Guide](deployment.md)
- [Architecture Overview](../architecture/overview.md)
- [Troubleshooting](troubleshooting.md)
