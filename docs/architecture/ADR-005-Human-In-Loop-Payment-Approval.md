# ADR-005: Human-in-the-Loop Payment Approval via Claude Desktop MCP

**Status**: Accepted
**Date**: 2025-10-18
**Context**: AP2 payment integration for hackathon - responsible AI demonstration
**Related**: ADR-004 (AP2 Payment A2A Only)

---

## Decision

**AP2 payments MUST require explicit human approval via Claude Desktop MCP tool, NOT auto-confirmation.**

## Context

After implementing AP2 payment tools with 30-second auto-confirmation (mock), we realized this misses a critical opportunity to demonstrate:

1. **Responsible AI** - Human oversight for financial transactions
2. **Interactive Demo** - Judges can approve payments live
3. **Real-world Workflow** - Actual payment approval process
4. **Unique Differentiator** - Most teams won't have this

## Architecture

### Current MCP A2A Orchestrator Setup

**File**: `mcp_server/a2a_orchestrator_mcp.py`

**Claude Desktop Config**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "/path/to/scripts/mcp-a2a-wrapper.sh"
    }
  }
}
```

**Flow**:

```
Claude Desktop (Human)
    ↓
MCP A2A Orchestrator (stdio protocol)
    ↓ Bearer Token Authentication
AgentCore A2A Server (A2A protocol)
    ↓
Strands Agent with Payment Tools
```

### ❌ BEFORE (Auto-Confirm)

```python
# In check_payment_status()
if age_seconds > 30:
    payment_data["status"] = "confirmed"  # Auto-confirm
```

**Problems**:

- No human oversight
- Not realistic
- Misses demo opportunity
- Less impressive for judges

### ✅ AFTER (Human Approval)

```python
# New tool: approve_payment(booking_id)
@tool
def approve_payment(booking_id: str) -> dict[str, Any]:
    """Approve pending payment (human-in-the-loop)"""
    # Update S3 payment status to "confirmed"
    # Return confirmation
```

**Benefits**:

- Explicit human approval
- Realistic workflow
- Interactive demo
- Shows responsible AI

## Implementation

### 1. Add `approve_payment` Tool

**File**: `src/agents/tools/payment_tool.py`

```python
@tool
def approve_payment(booking_id: str) -> dict[str, Any]:
    """
    Approve a pending payment (human-in-the-loop).

    Args:
        booking_id: Booking ID to approve payment for

    Returns:
        Approval confirmation
    """
    try:
        # Get payment from S3
        response = s3_client.get_object(
            Bucket=PAYMENT_BUCKET,
            Key=f"payments/{booking_id}.json"
        )
        payment_data = json.loads(response["Body"].read())

        # Update status
        payment_data["status"] = "confirmed"
        payment_data["approved_at"] = datetime.now(UTC).isoformat()

        # Save back to S3
        s3_client.put_object(
            Bucket=PAYMENT_BUCKET,
            Key=f"payments/{booking_id}.json",
            Body=json.dumps(payment_data),
            ContentType="application/json"
        )

        return {
            "success": True,
            "message": f"✅ Payment approved for booking {booking_id}",
            "amount": payment_data["amount"],
            "currency": payment_data["currency"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 2. Add to A2A Agent

**File**: `src/agents/agentcore_a2a_server.py`

```python
from tools.payment_tool import (
    request_payment,
    check_payment_status,
    approve_payment  # NEW
)

strands_agent = Agent(
    tools=[
        *gateway_tools,
        request_payment,
        check_payment_status,
        approve_payment  # NEW
    ]
)
```

**System Prompt Update**:

```
PAYMENT APPROVAL (Human-in-the-Loop):
When payment is requested:
1. Return payment details to human
2. Wait for human to call approve_payment(booking_id)
3. Confirm booking only after payment approved
4. Do NOT auto-confirm payments
```

### 3. Add MCP Tool to Orchestrator

**File**: `mcp_server/a2a_orchestrator_mcp.py`

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="discover_restaurants",
            description="Search for restaurants...",
            inputSchema={...}
        ),
        Tool(
            name="book_restaurant",
            description="Book a table...",
            inputSchema={...}
        ),
        Tool(
            name="approve_payment",  # NEW
            description="Approve a pending payment for a booking",
            inputSchema={
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "string",
                        "description": "Booking ID from payment request"
                    }
                },
                "required": ["booking_id"]
            }
        )
    ]

@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "approve_payment":
        booking_id = arguments.get("booking_id")
        request_text = f"Approve payment for booking {booking_id}"
        # ... existing A2A call logic
```

### 4. Remove Auto-Confirm Logic

**File**: `src/agents/tools/payment_tool.py`

```python
# In check_payment_status()
# REMOVE THIS:
# if age_seconds > 30:
#     payment_data["status"] = "confirmed"
```

## User Flow

### In Claude Desktop

**Step 1: Book table**

```
Human: "Book La Bella Vita for 6 people tomorrow at 7pm"

Agent: "Booking created! Event ID: evt_abc123

        💳 Payment Required: $120 USDC
        Booking ID: evt_abc123

        To complete booking, approve payment using:
        approve_payment(booking_id='evt_abc123')"
```

**Step 2: Approve payment**

```
Human: "Approve payment for evt_abc123"

Agent: "✅ Payment approved!
        Amount: $120 USDC
        Booking confirmed for 6 guests
        Date: Tomorrow at 7pm"
```

**Step 3: Verify (optional)**

```
Human: "Check payment status for evt_abc123"

Agent: "Payment Status: confirmed
        Amount: $120 USDC
        Approved at: 2025-10-18T15:05:00Z"
```

## Benefits

### For Hackathon

1. **Responsible AI** ⭐⭐⭐⭐⭐
   - Shows human oversight for financial decisions
   - Demonstrates ethical AI practices
   - Aligns with AWS responsible AI principles

2. **Interactive Demo** ⭐⭐⭐⭐⭐
   - Judges can approve payments live
   - More engaging than auto-confirm
   - Shows real-world workflow

3. **Technical Sophistication** ⭐⭐⭐⭐
   - MCP tool integration
   - A2A protocol usage
   - State management (S3)

4. **Unique Differentiator** ⭐⭐⭐⭐⭐
   - Most teams won't have payment approval
   - Shows understanding of agent-human collaboration
   - Demonstrates production-ready thinking

### For Real-World Use

- Prevents unauthorized payments
- Audit trail for approvals
- Compliance with financial regulations
- User control over transactions

## Consequences

### Positive

- ✅ More realistic payment flow
- ✅ Better demo story
- ✅ Shows responsible AI
- ✅ Unique differentiator
- ✅ Production-ready pattern

### Negative

- ⚠️ Requires human interaction (can't be fully automated)
- ⚠️ Slightly more complex testing
- ⚠️ Depends on MCP orchestrator availability

### Mitigation

- Keep auto-confirm as fallback (commented out)
- Document testing procedure clearly
- Ensure MCP orchestrator is stable

## Testing

### Manual Test in Claude Desktop

1. Start A2A server: `uv run python src/agents/agentcore_a2a_server.py`
2. Restart Claude Desktop (reload MCP servers)
3. Test booking: "Book for 6 people tomorrow at 7pm"
4. Verify payment request returned
5. Test approval: "Approve payment for [booking_id]"
6. Verify confirmation

### Automated Test

```python
def test_human_in_loop_payment():
    # Request payment
    result = request_payment(120.0, "test_booking", "Test deposit")
    assert result["success"]

    # Check status (should be pending)
    status = check_payment_status("test_booking")
    assert status["payment_data"]["status"] == "pending"

    # Approve payment
    approval = approve_payment("test_booking")
    assert approval["success"]

    # Check status (should be confirmed)
    status = check_payment_status("test_booking")
    assert status["payment_data"]["status"] == "confirmed"
```

## Related Documents

- `docs/architecture/ADR-004-AP2-Payment-A2A-Only.md` - AP2 placement decision
- `docs/planning/AP2_HUMAN_IN_LOOP_PLAN.md` - Implementation plan
- `docs/PROJECT_CONTEXT.md` - Project context and decisions

## Status

- ✅ Decision documented
- ⏳ Implementation in progress
- ⏳ Testing pending
- ⏳ Demo preparation pending

---

**Last Updated**: 2025-10-18
