# Session Reset Guide

## Problem: Agent Behavior Doesn't Match System Prompt

### Symptoms

- Agent ignores current system prompt instructions
- Agent references old behavior from previous conversations
- System prompt is correct in logs but agent acts differently
- Tool usage doesn't match system prompt directives

### Root Cause

**S3SessionManager persists conversation history** across deployments. When you update the system prompt or agent behavior, old conversation history can override the new instructions because:

1. The agent loads previous messages from S3
2. Historical context is stronger than system prompt for LLMs
3. Session IDs are date-based (`whatsapp-{phone}-{date}-{hash}`) - same all day

### Solution Options

## Option 1: Manual Session Clear (Immediate)

```bash
# Clear all sessions for a specific user
aws s3 rm s3://agentcore-sessions-{ACCOUNT_ID}/actor-{PHONE_NUMBER}/ --recursive

# Clear all sessions (nuclear option)
aws s3 rm s3://agentcore-sessions-{ACCOUNT_ID}/ --recursive
```

**When to use:** After major system prompt changes, agent behavior updates, or tool modifications.

## Option 2: Add Admin Reset Command

Create a Lambda function or API endpoint that allows clearing sessions:

```python
# Add to Lambda orchestrator
def clear_user_session(phone_number: str, bucket: str):
    """Clear session history for a user."""
    s3 = boto3.client('s3')
    prefix = f"actor-{phone_number}/"

    # List and delete all objects
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if 'Contents' in page:
            objects = [{'Key': obj['Key']} for obj in page['Contents']]
            s3.delete_objects(Bucket=bucket, Delete={'Objects': objects})
```

**Trigger options:**

- WhatsApp command: `/reset` or `/clear`
- Admin API endpoint
- Scheduled daily cleanup

## Option 3: Session ID Strategy

### Current (Date-based):

```python
session_id = f"whatsapp-{phone}-{date}-{hash}"  # Same all day
```

### Alternative (Time-based):

```python
session_id = f"whatsapp-{phone}-{timestamp}"  # New every hour/deployment
```

**Pros:** Automatic fresh start
**Cons:** Loses conversation context more frequently

### Hybrid (Version-based):

```python
AGENT_VERSION = "v2"  # Increment on major changes
session_id = f"whatsapp-{phone}-{date}-{AGENT_VERSION}"
```

**Pros:** Controlled resets only when needed
**Cons:** Requires manual version bumps

## Option 4: System Prompt Override

Make system prompt more forceful:

```python
system_prompt = """CRITICAL INSTRUCTIONS - OVERRIDE ALL PREVIOUS CONTEXT:

You are La Bella Vita restaurant assistant on WhatsApp.

IGNORE any previous instructions about being a "booking assistant" or "finding restaurants".

YOU ARE THE RESTAURANT. Answer questions about YOUR menu, YOUR hours, YOUR dishes.

MANDATORY: Use search_restaurant_info tool for ALL menu/dietary questions.
"""
```

**Pros:** No infrastructure changes
**Cons:** Not guaranteed to work, LLMs may still prioritize history

## Recommended Approach

**For Development:**

- Use Option 1 (manual clear) after each major change
- Add to deployment checklist

**For Production:**

- Implement Option 2 (admin reset command)
- Add WhatsApp command: `/reset` to clear user's session
- Log session resets for monitoring

**For Major Updates:**

- Use Option 3 (version-based sessions)
- Increment `AGENT_VERSION` in code when system prompt changes significantly

## Implementation Checklist

- [ ] Add session clear function to Lambda
- [ ] Create `/reset` WhatsApp command handler
- [ ] Add `AGENT_VERSION` environment variable
- [ ] Update session ID generation to include version
- [ ] Document session reset in user guide
- [ ] Add CloudWatch alarm for high session storage costs

## Testing After Changes

Always test with fresh session after:

1. System prompt modifications
2. Tool additions/removals
3. Agent behavior changes
4. Model changes

```bash
# Quick test with fresh session
aws s3 rm s3://agentcore-sessions-{ACCOUNT_ID}/actor-{TEST_PHONE}/ --recursive
# Then send test message via WhatsApp
```

## Related Issues

- **Issue**: Agent not using new tools → Clear session
- **Issue**: Agent contradicts system prompt → Clear session
- **Issue**: Agent references old context → Clear session
- **Issue**: Tool permissions work in CLI but not WhatsApp → Check session history

## Monitoring

Add CloudWatch metrics:

- Session count per user
- Session age
- Session size
- Reset frequency

Alert if sessions grow too large (>100 messages) or too old (>7 days).
