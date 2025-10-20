#!/bin/bash
# Simple test for Google Calendar features via AgentCore

set -e

echo "🗓️  Google Calendar Features Test"
echo "=================================="
echo ""

# Test 1: Check Availability
echo "Test 1: Check Availability"
echo "--------------------------"
echo "📤 Checking if tomorrow 8pm is available..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Is tomorrow at 8pm available for booking?", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

# Test 2: Get Available Slots
echo "Test 2: Get Available Slots"
echo "---------------------------"
echo "📤 Getting available times for tomorrow..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Show me available times for tomorrow", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

# Test 3: Create Booking
echo "Test 3: Create Booking"
echo "----------------------"
echo "📤 Creating test booking..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Book tomorrow at 3pm for 2 people, name Test Calendar, phone +23099999999", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

# Test 4: List Bookings
echo "Test 4: List Bookings"
echo "---------------------"
echo "📤 Listing all bookings for tomorrow..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Show me all bookings for tomorrow", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

# Test 5: Cancel Booking
echo "Test 5: Cancel Booking"
echo "----------------------"
echo "📤 Canceling the test booking at 3pm..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Cancel my booking tomorrow at 3pm", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

# Test 6: Verify Cancellation
echo "Test 6: Verify Cancellation"
echo "---------------------------"
echo "📤 Verifying booking was removed..."
RESPONSE=$(uv run agentcore invoke '{"prompt": "Show me all bookings for tomorrow", "actor_id": "calendar-test"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')
echo "📥 $RESPONSE"
echo ""

echo "✅ All tests complete!"
echo ""
echo "Manual Verification:"
echo "  1. Check Google Calendar for test booking (should be gone)"
echo "  2. Verify no 3pm booking exists"
echo "  3. All other bookings should be intact"
