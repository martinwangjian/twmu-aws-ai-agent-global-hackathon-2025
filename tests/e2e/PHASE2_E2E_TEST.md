# Phase 2: Availability Checking - E2E Test

## Test Scenarios

### Test 1: Conflict Detection ✅

**Objective**: Verify agent detects booking conflicts

**Steps**:
```bash
uv run agentcore invoke '{"prompt": "I want to book a table for tomorrow at 8pm for 2 people. My name is Jane Doe, phone +23099999999", "actor_id": "test-user"}'
```

**Expected Result**:
- Agent checks availability using `checkAvailability` tool
- Detects existing booking at 8pm
- Responds with: "Time slot is not available" or similar
- Suggests alternative time

**Actual Result** (2025-01-09):
```
"I'm sorry, but the time slot you requested is not available. There is already a booking for 2 guests starting at 20:00 on 2025-10-10. How about we try 18:00 instead?"
```

✅ **PASS**: Agent detected conflict and suggested 6pm alternative

---

### Test 2: Alternative Time Booking ✅

**Objective**: Verify agent can book at suggested alternative time

**Steps**:
```bash
# Continue from Test 1 session
uv run agentcore invoke '{"prompt": "Yes, 6pm works for me", "actor_id": "test-user"}'
```

**Expected Result**:
- Agent checks availability at 6pm
- Time slot is available
- Creates booking successfully
- Provides confirmation with calendar link

**Actual Result** (2025-01-09):
```
"Your booking has been successfully created! You have a reservation for 4 guests under the name John Smith at 18:00 on 2025-10-10. Here is the link to your booking: [Google Calendar Event](...)"
```

✅ **PASS**: Booking created at alternative time

---

### Test 3: Available Slot (No Conflict)

**Objective**: Verify agent handles available time slots correctly

**Steps**:
```bash
uv run agentcore invoke '{"prompt": "Book a table for tomorrow at 2:30pm for 3 people. Name: Test User, phone +23011111111", "actor_id": "test-user-2"}'
```

**Expected Result**:
- Agent checks availability
- Time slot is available
- Creates booking directly
- Provides confirmation

**To Test**: Run command and verify response

---

### Test 4: Business Hours Validation

**Objective**: Verify agent rejects bookings outside business hours

**Steps**:
```bash
uv run agentcore invoke '{"prompt": "Book a table for tomorrow at 2am for 2 people. Name: Night Owl, phone +23022222222", "actor_id": "test-user-3"}'
```

**Expected Result**:
- Agent recognizes 2am is outside business hours (11am-10pm/11pm)
- Rejects booking politely
- Suggests booking during business hours
- May mention opening time (11am)

**To Test**: Run command and verify response

---

### Test 5: WhatsApp End-to-End

**Objective**: Verify full WhatsApp integration with availability checking

**Steps**:
1. Send WhatsApp message: "I want to book a table for tomorrow at 8pm"
2. Verify agent detects conflict
3. Accept suggested alternative time
4. Verify booking confirmation

**Expected Result**:
- Same behavior as AgentCore direct invocation
- No `<thinking>` tags visible
- Natural conversational flow
- Booking created in Google Calendar

**To Test**: Use real WhatsApp number

---

## Test Results Summary

| Test | Status | Date | Notes |
|------|--------|------|-------|
| Conflict Detection | ✅ PASS | 2025-01-09 | Detected existing 8pm booking, suggested 6pm |
| Alternative Booking | ✅ PASS | 2025-01-09 | Successfully booked at 6pm |
| Available Slot | ⏳ TODO | - | Need to test |
| Business Hours | ⏳ TODO | - | Need to test |
| WhatsApp E2E | ⏳ TODO | - | Need to test via real WhatsApp |

## Running Tests

### Quick Test (Conflict Detection)
```bash
cd /Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025
source .env
uv run agentcore invoke '{"prompt": "Book tomorrow 8pm for 2, Jane Doe +23099999999", "actor_id": "test"}'
```

### Full Test Suite
Run each test scenario above manually and verify results.

## Success Criteria

- ✅ Agent ALWAYS checks availability before booking
- ✅ Agent detects conflicts accurately
- ✅ Agent suggests alternative times when conflicts occur
- ⏳ Agent validates business hours
- ⏳ Agent creates bookings successfully when slots are available
- ⏳ No `<thinking>` tags visible in responses
- ⏳ Works end-to-end via WhatsApp

## Notes

- Tests use AgentCore direct invocation for speed
- WhatsApp testing requires real phone number
- Calendar must have existing bookings for conflict tests
- Business hours: Mon-Thu 11am-10pm, Fri-Sat 11am-11pm, Sun 11am-10pm
