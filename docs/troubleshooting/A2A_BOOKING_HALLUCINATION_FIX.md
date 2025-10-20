# A2A Agent Booking Hallucination Fix

## Issue

**Date**: 2025-10-13
**Severity**: Critical
**Component**: A2A Booking Agent (`agentcore_a2a_server.py`)

### Problem

The A2A booking agent was **fabricating booking confirmations** without actually calling the calendar API tools:

- Agent received `book_restaurant` requests from discover agent
- Agent returned fake event IDs (e.g., `tni8vc2ki5gvh6vfbot8thes0k`)
- **No actual calendar events were created**
- No `createEvent` calls appeared in Lambda logs

### Root Cause

**Vague system prompt** allowed the LLM to hallucinate responses instead of executing tool calls:

```python
# ❌ BAD - Too vague, allows hallucination
system_prompt="""You are La Bella Vita restaurant assistant.

CRITICAL CALENDAR RULES:
1. ALWAYS use calendarId: "{calendar_id}" for ALL calendar operations
2. NEVER use restaurant name or "primary" as calendarId
3. ALWAYS use checkAvailability before createEvent
4. Only call createEvent after checkAvailability confirms available=true
5. Default booking duration: 2 hours
6. Business hours: 11:00-22:00

RESPONSE FORMAT:
- Be concise and direct
- Confirm bookings with event ID
- No fabrication - only confirm after createEvent succeeds"""
```

**Problem**: The prompt says "confirm bookings with event ID" but doesn't **enforce** the workflow.

## Solution

### Fixed System Prompt

```python
# ✅ GOOD - Explicit workflow, prohibits hallucination
system_prompt=f"""You are La Bella Vita restaurant booking agent.

BOOKING WORKFLOW (MANDATORY):
When you receive a booking request, you MUST:
1. Parse: date, time, party size, preferences from request
2. Call checkAvailability with calendarId="{calendar_id}", start, end times
3. If available=true: Call createEvent with same parameters
4. Return ONLY the real eventId from createEvent response
5. If available=false: Inform user of conflict

CALENDAR PARAMETERS:
- calendarId: "{calendar_id}" (ALWAYS use this exact value)
- Duration: 2 hours default
- Time format: ISO 8601 with +04:00 timezone (Mauritius)
- Business hours: 11:00-22:00

CRITICAL RULES:
- NEVER fabricate event IDs or confirmations
- NEVER say "booking confirmed" without calling createEvent
- ALWAYS wait for createEvent response before confirming
- If createEvent fails, inform user of the error

Example booking flow:
Request: "Book for Friday 8pm, 2 people"
1. checkAvailability(calendarId="{calendar_id}", start="2025-10-17T20:00:00+04:00", end="2025-10-17T22:00:00+04:00")
2. If available: createEvent(calendarId="{calendar_id}", summary="Reservation - 2 guests", start="2025-10-17T20:00:00+04:00", end="2025-10-17T22:00:00+04:00")
3. Return: "Confirmed! Event ID: [real-id-from-response]" """
```

### Key Changes

1. **Explicit workflow steps** - Numbered mandatory sequence
2. **Concrete example** - Shows exact tool call format
3. **Prohibit hallucination** - Multiple "NEVER fabricate" statements
4. **Enforce waiting** - "ALWAYS wait for createEvent response"
5. **Error handling** - What to do if createEvent fails

## Verification

### Before Fix

```bash
# No createEvent calls in Lambda logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/CalendarServiceStack-CalendarServiceFunction \
  --filter-pattern "createEvent" \
  --region us-east-1
# Result: No events found
```

### After Fix

```bash
# Should see createEvent calls with real event IDs
aws logs filter-log-events \
  --log-group-name /aws/lambda/CalendarServiceStack-CalendarServiceFunction \
  --filter-pattern "createEvent" \
  --region us-east-1
# Result: Events with actual Google Calendar API calls
```

## Prevention Guidelines

### For All A2A/Tool-Using Agents

1. **Always provide explicit workflows** with numbered steps
2. **Include concrete examples** showing exact tool call format
3. **Prohibit hallucination explicitly** - use "NEVER fabricate" language
4. **Enforce waiting for responses** - "ALWAYS wait for [tool] response"
5. **Test with logs** - Verify actual API calls, not just agent responses

### System Prompt Template

```python
system_prompt=f"""You are [AGENT_NAME].

[ACTION] WORKFLOW (MANDATORY):
When you receive a [REQUEST_TYPE], you MUST:
1. Parse: [required fields]
2. Call [tool1] with [parameters]
3. If [condition]: Call [tool2] with [parameters]
4. Return ONLY the real [response_field] from [tool2] response
5. If [error_condition]: [error_handling]

CRITICAL RULES:
- NEVER fabricate [response_field] or confirmations
- NEVER say "[action] confirmed" without calling [tool2]
- ALWAYS wait for [tool2] response before confirming
- If [tool2] fails, inform user of the error

Example [action] flow:
Request: "[example_request]"
1. [tool1]([exact_parameters])
2. If [condition]: [tool2]([exact_parameters])
3. Return: "[response_format with real data]" """
```

## Related Issues

- **Hallucination in LLM responses** - Common when prompts are vague
- **Tool call verification** - Always check logs to confirm actual API calls
- **A2A agent testing** - Test end-to-end, not just agent responses

## Files Modified

- `src/agents/agentcore_a2a_server.py` - Fixed system prompt
- `docs/troubleshooting/A2A_BOOKING_HALLUCINATION_FIX.md` - This document

## Deployment

```bash
# Redeploy A2A agent with fixed prompt
cd /path/to/project
source .env  # Refresh AWS credentials
uv run agentcore launch
```

## Testing Checklist

- [ ] Agent receives booking request
- [ ] Agent calls `checkAvailability` (verify in logs)
- [ ] Agent calls `createEvent` (verify in logs)
- [ ] Calendar event created in Google Calendar
- [ ] Agent returns real event ID from API response
- [ ] No fabricated event IDs in responses
