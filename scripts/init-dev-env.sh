#!/usr/bin/env bash
#
# Development Environment Initialization Script
# Sets up pre-commit hooks and dependencies using uv
#

set -e

echo "🚀 Initializing development environment with uv..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ uv $(uv --version) found"
echo ""

# Sync dependencies (creates .venv automatically)
echo "📦 Installing dependencies..."
uv sync --all-extras

echo ""
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg

echo ""
echo "✅ Development environment initialized!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure AWS credentials"
echo "  2. Run tests: uv run pytest"
echo "  3. Test agent: uv run python -m src.agents.agentcore_mcp_agent"
echo ""
echo "Useful commands:"
echo "  • Run pre-commit: uv run pre-commit run --all-files"
echo "  • Update deps: uv lock --upgrade"
echo "  • Add package: uv add <package>"
echo "  • Deploy CDK: cd cdk_infra && uv run cdk deploy"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
