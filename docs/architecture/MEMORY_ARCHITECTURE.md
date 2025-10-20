# Agentic Memory Architecture

## Overview

Implementing short-term and long-term memory for the WhatsApp booking agent to provide personalized, context-aware interactions.

## Memory Types

### 1. Short-Term Memory (Session Context)

**Purpose**: Maintain conversation context within a session
**Retention**: Minutes to hours
**Use Cases**:

- Current conversation flow
- Temporary booking details
- User's current intent

### 2. Long-Term Memory (User Profile)

**Purpose**: Persistent user preferences and history
**Retention**: Indefinite
**Use Cases**:

- User preferences (language, timezone)
- Booking history
- Frequently requested services

## Architecture Options

### Option 1: AgentCore Native Memory (Recommended)

**Components**:

```
WhatsApp User
    ↓
Lambda Orchestrator
    ↓
AgentCore Runtime
    ├── Session Memory (built-in)
    └── Memory ARN (persistent)
```

**Pros**:

- ✅ Built into AgentCore
- ✅ Automatic session management
- ✅ No additional infrastructure
- ✅ Integrated with agent lifecycle

**Cons**:

- ⚠️ Limited to AgentCore features
- ⚠️ Less control over memory structure

**Implementation**:

```python
# AgentCore automatically manages session memory
response = agentcore.invoke_agent_runtime(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_id,  # Maintains session context
    memoryArn=memory_arn,          # Persistent memory
    payload=json.dumps({"prompt": prompt})
)
```

**Cost**: Included in AgentCore pricing

---

### Option 2: DynamoDB + ElastiCache

**Components**:

```
WhatsApp User
    ↓
Lambda Orchestrator
    ├── ElastiCache Redis (short-term)
    │   └── Session data, conversation context
    └── DynamoDB (long-term)
        └── User profiles, booking history
    ↓
AgentCore Runtime
```

**Pros**:

- ✅ Full control over memory structure
- ✅ Fast access (Redis)
- ✅ Scalable (DynamoDB)
- ✅ Rich querying capabilities

**Cons**:

- ❌ Additional infrastructure cost
- ❌ More complex to manage
- ❌ Requires custom implementation

**Data Models**:

**Short-Term (Redis)**:

```json
{
  "session_id": "whatsapp:+1234567890:20251008",
  "conversation": [
    { "role": "user", "content": "Book appointment" },
    { "role": "assistant", "content": "What date?" }
  ],
  "context": {
    "intent": "booking",
    "current_step": "date_selection"
  },
  "ttl": 3600
}
```

**Long-Term (DynamoDB)**:

```json
{
  "user_id": "whatsapp:+1234567890",
  "preferences": {
    "language": "en",
    "timezone": "America/New_York",
    "notification_preference": "whatsapp"
  },
  "booking_history": [
    {
      "date": "2025-10-15",
      "service": "haircut",
      "status": "completed"
    }
  ],
  "created_at": "2025-10-01T00:00:00Z",
  "updated_at": "2025-10-08T08:00:00Z"
}
```

**Cost**: ~$5-20/month (low traffic)

---

### Option 3: Hybrid (AgentCore + DynamoDB)

**Components**:

```
WhatsApp User
    ↓
Lambda Orchestrator
    ├── DynamoDB (user profiles)
    └── AgentCore Runtime
        └── Session Memory (built-in)
```

**Pros**:

- ✅ Best of both worlds
- ✅ AgentCore handles conversation context
- ✅ DynamoDB for structured user data
- ✅ Moderate complexity

**Cons**:

- ⚠️ Requires synchronization
- ⚠️ Additional DynamoDB cost

**Implementation Flow**:

1. User sends message
2. Lambda retrieves user profile from DynamoDB
3. Inject profile into AgentCore prompt
4. AgentCore maintains session context
5. Update DynamoDB after booking completion

**Cost**: ~$2-10/month

---

### Option 4: S3 + Bedrock Knowledge Base (Semantic Memory)

**Components**:

```
WhatsApp User
    ↓
Lambda Orchestrator
    ↓
AgentCore Runtime
    ├── Session Memory (built-in)
    └── Bedrock Knowledge Base
        └── S3 (user interactions, FAQs)
```

**Pros**:

- ✅ Semantic search capabilities
- ✅ Natural language queries
- ✅ Scales to large knowledge bases
- ✅ Integrated with Bedrock

**Cons**:

- ❌ Higher latency
- ❌ More expensive
- ❌ Overkill for simple memory

**Use Cases**:

- FAQ retrieval
- Similar booking patterns
- Personalized recommendations

**Cost**: ~$10-50/month

---

## Recommended Architecture

### Phase 1: AgentCore Native Memory (MVP)

**Why**: Fastest to implement, no additional infrastructure

```python
# .bedrock_agentcore.yaml
memory:
  memory_arn: arn:aws:bedrock-agentcore:us-east-1:123456789012:memory/booking-agent-mem-EXAMPLE
```

**Implementation**:

```python
# lambda/whatsapp_orchestrator.py
def invoke_agentcore(runtime_arn: str, session_id: str, prompt: str) -> str:
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,  # Auto-managed session memory
        payload=json.dumps({"prompt": prompt})
    )
    return response
```

### Phase 2: Add DynamoDB for User Profiles

**Why**: Structured data for bookings and preferences

**CDK Stack**:

```python
# cdk_infra/cdk_infra/memory_stack.py
user_table = dynamodb.Table(
    self, "UserProfiles",
    partition_key=dynamodb.Attribute(
        name="user_id",
        type=dynamodb.AttributeType.STRING
    ),
    billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
    point_in_time_recovery=True
)
```

**Lambda Integration**:

```python
def get_user_profile(user_id: str) -> dict:
    response = dynamodb.get_item(
        TableName="UserProfiles",
        Key={"user_id": {"S": user_id}}
    )
    return response.get("Item", {})

def invoke_with_context(runtime_arn: str, session_id: str, user_id: str, prompt: str) -> str:
    profile = get_user_profile(user_id)

    # Inject user context into prompt
    context_prompt = f"""
    User Profile:
    - Language: {profile.get('language', 'en')}
    - Timezone: {profile.get('timezone', 'UTC')}
    - Previous bookings: {len(profile.get('booking_history', []))}

    User Message: {prompt}
    """

    return invoke_agentcore(runtime_arn, session_id, context_prompt)
```

### Phase 3: Add Redis for High-Frequency Access (Optional)

**Why**: Sub-millisecond access for active sessions

**When**: If you have >1000 concurrent users

---

## Implementation Roadmap

### Week 1: AgentCore Memory

- [ ] Configure memory ARN in AgentCore
- [ ] Test session persistence
- [ ] Verify conversation context

### Week 2: DynamoDB Integration

- [ ] Create DynamoDB table (CDK)
- [ ] Implement user profile CRUD
- [ ] Integrate with Lambda orchestrator

### Week 3: Testing & Optimization

- [ ] Load testing
- [ ] Memory retention tuning
- [ ] Cost optimization

---

## Cost Comparison

| Option           | Setup   | Monthly Cost  | Complexity |
| ---------------- | ------- | ------------- | ---------- |
| AgentCore Only   | 1 hour  | $0 (included) | Low        |
| + DynamoDB       | 2 hours | $2-10         | Medium     |
| + Redis          | 4 hours | $15-50        | High       |
| + Knowledge Base | 6 hours | $20-100       | High       |

---

## Security Considerations

1. **Data Encryption**
   - DynamoDB: Encryption at rest (enabled by default)
   - Redis: In-transit encryption (TLS)
   - S3: Server-side encryption (SSE-S3)

2. **Access Control**
   - IAM roles with least privilege
   - VPC endpoints for private access
   - Secrets Manager for credentials

3. **Data Retention**
   - DynamoDB TTL for automatic cleanup
   - S3 lifecycle policies
   - GDPR compliance (right to be forgotten)

---

## Monitoring

**CloudWatch Metrics**:

- Memory hit/miss rate
- Session duration
- DynamoDB read/write capacity
- Lambda memory usage

**Alarms**:

- High memory usage
- DynamoDB throttling
- Session timeout rate

---

## Next Steps

1. **Decision**: Choose architecture option
2. **Prototype**: Implement Phase 1 (AgentCore memory)
3. **Test**: Verify session persistence
4. **Iterate**: Add DynamoDB if needed

---

**Recommendation**: Start with **Option 1 (AgentCore Native)** for MVP, then add **DynamoDB** (Option 3) when you need structured user data.

**Last Updated**: 2025-10-08
**Status**: Design Phase
