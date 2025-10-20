# Google Calendar Features - Test Guide

Simple test cases to validate all calendar features are working.

## Prerequisites

```bash
cd /Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025
source .env
```

## Test 1: Check Availability ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Is tomorrow at 8pm available?", "actor_id": "test"}'
```

**Expected**: 
- Should check calendar
- Return "available" or "not available" with details

---

## Test 2: Get Available Slots ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Show me available times for tomorrow", "actor_id": "test"}'
```

**Expected**:
- List 3-5 available time slots
- Format: "6:00 PM, 6:30 PM, 7:30 PM..."

**Actual Result** (2025-01-09):
```
Here are the available times for tomorrow:
- 6:00 PM
- 7:00 PM
- 9:00 PM
```
✅ PASS

---

## Test 3: Create Booking ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Book tomorrow at 3pm for 2 people, name Test User, phone +23099999999", "actor_id": "test"}'
```

**Expected**:
- Check availability first
- Create booking if available
- Return confirmation with calendar link

**Verify**: Check Google Calendar - booking should appear

---

## Test 4: Handle Conflict ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Book tomorrow at 8pm for 2 people, name Jane Doe, phone +23088888888", "actor_id": "test"}'
```

**Expected**:
- Detect conflict
- Suggest alternative time
- Do NOT create booking

---

## Test 5: List Bookings ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Show me all bookings for tomorrow", "actor_id": "test"}'
```

**Expected**:
- List all bookings with:
  - Booking ID
  - Customer name
  - Date/time
  - Party size

---

## Test 6: Cancel Booking ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Cancel my booking tomorrow at 3pm", "actor_id": "test"}'
```

**Expected**:
- Find booking by time
- Delete from calendar
- Confirm cancellation

**Verify**: Check Google Calendar - booking should be gone

---

## Test 7: Verify Cancellation ✓

**Command**:
```bash
uv run agentcore invoke '{"prompt": "Show me all bookings for tomorrow", "actor_id": "test"}'
```

**Expected**:
- 3pm booking should NOT appear
- All other bookings intact

---

## Quick Test Script

Run all tests at once:

```bash
# Test 1: Available slots
echo "Test 1: Available Slots"
uv run agentcore invoke '{"prompt": "Show available times tomorrow", "actor_id": "test"}'

# Test 2: Create booking
echo -e "\nTest 2: Create Booking"
uv run agentcore invoke '{"prompt": "Book tomorrow 3pm for 2, Test User +23099999999", "actor_id": "test"}'

# Test 3: List bookings
echo -e "\nTest 3: List Bookings"
uv run agentcore invoke '{"prompt": "Show my bookings tomorrow", "actor_id": "test"}'

# Test 4: Cancel booking
echo -e "\nTest 4: Cancel Booking"
uv run agentcore invoke '{"prompt": "Cancel my 3pm booking tomorrow", "actor_id": "test"}'

# Test 5: Verify
echo -e "\nTest 5: Verify Cancellation"
uv run agentcore invoke '{"prompt": "Show my bookings tomorrow", "actor_id": "test"}'
```

---

## WhatsApp Test

Test via real WhatsApp:

1. **Available times**: "Show me available times tomorrow"
2. **Book**: "Book tomorrow at 3pm for 2 people, my name is Test User, phone +23099999999"
3. **List**: "Show me my bookings"
4. **Cancel**: "Cancel my booking tomorrow at 3pm"
5. **Verify**: "Show me my bookings"

---

## Success Criteria

- ✅ Check availability works
- ✅ Get available slots returns 3-5 options
- ✅ Create booking adds to calendar
- ✅ Conflict detection prevents double booking
- ✅ List bookings shows all reservations
- ✅ Cancel booking removes from calendar
- ✅ All operations work via natural language
- ✅ No `<thinking>` tags in responses

---

## Google Calendar Verification

After tests, check Google Calendar directly:
1. Open: https://calendar.google.com
2. Navigate to tomorrow's date
3. Verify:
   - Test booking at 3pm should be GONE (if canceled)
   - All other bookings intact
   - No duplicate bookings

---

## Troubleshooting

**If booking not appearing**:
- Check calendar ID in agent prompt
- Verify service account has write access
- Check Lambda logs for errors

**If cancellation not working**:
- Verify booking ID is correct
- Check deleteEvent tool is available
- Review agent logs

**If conflicts not detected**:
- Verify checkAvailability tool is working
- Check time zone (Indian/Mauritius UTC+4)
- Review calendar query parameters
