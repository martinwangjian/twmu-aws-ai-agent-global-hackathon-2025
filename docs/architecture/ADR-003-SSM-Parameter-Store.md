# ADR-003: Use SSM Parameter Store for Runtime Configuration

**Date**: 2025-10-12
**Status**: Accepted
**Deciders**: Development Team

## Context

AgentCore Runtime does not support environment variable injection at deployment time. Currently, configuration values (like `GOOGLE_CALENDAR_ID`) are hardcoded in agent code, requiring redeployment for any configuration change.

### Current Issues

1. **Hardcoded values** in `agentcore_a2a_server.py`
2. **No environment variable support** in AgentCore Runtime
3. **Secrets mixed with config** in `.env` file
4. **Redeployment required** for config changes
5. **No audit trail** for configuration changes

## Decision

We will use **AWS Systems Manager (SSM) Parameter Store** for all runtime configuration and secrets.

### Configuration Strategy

**Runtime Configuration** → SSM Parameter Store (String)
**Secrets** → SSM Parameter Store (SecureString)
**Local Development** → `.env` file (fallback)
**Deployment Config** → `.env` file (AWS credentials only)

## Rationale

### Why SSM Parameter Store?

1. **AgentCore Compatible**: Works without environment variable support
2. **Centralized**: Single source of truth for configuration
3. **Updateable**: Change config without redeployment
4. **Secure**: SecureString encryption for secrets
5. **IAM-Controlled**: Fine-grained access control
6. **Auditable**: CloudTrail logs all access
7. **Free**: Standard parameters are free
8. **Versioned**: Automatic version history

### Why Not Alternatives?

**Environment Variables**:

- ❌ Not supported by AgentCore Runtime
- ❌ Requires container rebuild

**Secrets Manager**:

- ❌ More expensive ($0.40/secret/month)
- ❌ Overkill for non-rotating secrets
- ✅ Consider for future if rotation needed

**S3 Configuration File**:

- ❌ More complex (S3 permissions, parsing)
- ❌ No built-in encryption
- ❌ No version history

**DynamoDB**:

- ❌ Overkill for simple key-value config
- ❌ More expensive
- ❌ More complex

## Implementation

### Parameter Hierarchy

```
/restaurant-booking/
├── google-calendar-id          (String)
├── bedrock-model-id            (String)
├── restaurant-kb-id            (String)
├── agentcore-memory-arn        (String)
├── google-client-id            (SecureString)
├── google-client-secret        (SecureString)
├── gateway-client-id           (SecureString)
└── gateway-client-secret       (SecureString)
```

### Code Pattern

```python
from config.runtime_config import get_runtime_config

config = get_runtime_config()  # Cached, fetches from SSM
calendar_id = config['google_calendar_id']
```

### Local Development

```bash
export LOCAL_DEV=true  # Uses .env instead of SSM
python src/agents/agentcore_a2a_server.py
```

### Production

```bash
# Automatically fetches from SSM
uv run agentcore launch
```

## Consequences

### Positive

✅ **No hardcoded values** - Clean, maintainable code
✅ **Update without redeployment** - Faster iteration
✅ **Encrypted secrets** - Better security
✅ **IAM-controlled** - Principle of least privilege
✅ **Audit trail** - Compliance-ready
✅ **Works locally and in cloud** - Consistent experience
✅ **Free** - No additional cost

### Negative

⚠️ **Extra API call** - ~50ms latency at startup (cached)
⚠️ **IAM permissions required** - Must grant SSM access
⚠️ **Regional** - Parameters are region-specific
⚠️ **Migration effort** - One-time setup cost

### Neutral

- Parameters must be created before agent deployment
- Requires SSM permissions in execution role
- Local dev still uses `.env` (fallback)

## Alternatives Considered

### 1. Keep Hardcoded Values

- ❌ Not maintainable
- ❌ Requires redeployment for changes
- ❌ Secrets in code

### 2. Configuration File in Code

- ❌ Still requires redeployment
- ❌ Secrets in repository

### 3. S3 Configuration

- ⚠️ More complex
- ⚠️ No built-in encryption
- ✅ Could work but SSM is simpler

### 4. AWS Secrets Manager

- ✅ Better for rotating secrets
- ❌ More expensive
- ❌ Overkill for current needs

## Migration Path

1. Create SSMParametersStack (CDK)
2. Deploy stack to create parameters
3. Populate parameters from `.env`
4. Create `runtime_config.py` module
5. Update agent code to use config
6. Test locally with `LOCAL_DEV=true`
7. Deploy to AgentCore
8. Verify SSM parameters are used
9. Update documentation

## Success Metrics

- ✅ Agent starts successfully with SSM config
- ✅ Config changes work without redeployment
- ✅ Local development still works with `.env`
- ✅ No secrets in code or logs
- ✅ CloudTrail shows parameter access

## References

- [SSM Parameter Store Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [AgentCore Runtime Limitations](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [SSM_PARAMETER_STORE_PLAN.md](../SSM_PARAMETER_STORE_PLAN.md)

## Related Decisions

- ADR-001: Use AgentCore Runtime for A2A deployment
- ADR-002: Use Cognito OAuth for A2A authentication
