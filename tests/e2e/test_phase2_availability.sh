#!/bin/bash
# E2E test for Phase 2: Availability Checking

set -e

echo "============================================================"
echo "Phase 2: Availability Checking - E2E Tests"
echo "============================================================"
echo ""

# Test 1: Conflict Detection
echo "Test 1: Conflict Detection"
echo "------------------------------------------------------------"
echo "📤 Booking tomorrow at 8pm (should conflict with existing booking)"
RESPONSE=$(uv run agentcore invoke '{"prompt": "I want to book a table for tomorrow at 8pm for 2 people. My name is Jane Doe, phone +23099999999", "actor_id": "test-phase2"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')

echo "📥 Response: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -qi "not available\|unavailable\|already\|conflict\|occupied\|booked"; then
    echo "✅ PASS: Agent detected conflict"
    TEST1_PASS=true
else
    echo "❌ FAIL: Agent did not detect conflict"
    TEST1_PASS=false
fi

echo ""

# Test 2: Available Slot
echo "Test 2: Available Slot Booking"
echo "------------------------------------------------------------"
echo "📤 Booking tomorrow at 2:30pm (likely available)"
RESPONSE=$(uv run agentcore invoke '{"prompt": "Book a table for tomorrow at 2:30pm for 3 people. Name: Test User, phone +23011111111", "actor_id": "test-phase2-2"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')

echo "📥 Response: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -qi "created\|confirmed\|booked\|reservation\|successfully\|available"; then
    echo "✅ PASS: Agent handled available slot correctly"
    TEST2_PASS=true
else
    echo "⚠️  WARN: Unexpected response"
    TEST2_PASS=false
fi

echo ""

# Test 3: Business Hours
echo "Test 3: Business Hours Validation"
echo "------------------------------------------------------------"
echo "📤 Booking tomorrow at 2am (outside business hours)"
RESPONSE=$(uv run agentcore invoke '{"prompt": "Book a table for tomorrow at 2am for 2 people. Name: Night Owl, phone +23022222222", "actor_id": "test-phase2-3"}' 2>/dev/null | grep -A 1 "Response:" | tail -1 | jq -r '.result')

echo "📥 Response: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -qi "closed\|not open\|business hours\|operating hours\|11"; then
    echo "✅ PASS: Agent validated business hours"
    TEST3_PASS=true
else
    echo "⚠️  WARN: Agent may not have validated business hours"
    TEST3_PASS=false
fi

echo ""

# Summary
echo "============================================================"
echo "Test Summary"
echo "============================================================"

PASSED=0
TOTAL=3

if [ "$TEST1_PASS" = true ]; then
    echo "✅ PASS: Conflict Detection"
    ((PASSED++))
else
    echo "❌ FAIL: Conflict Detection"
fi

if [ "$TEST2_PASS" = true ]; then
    echo "✅ PASS: Available Slot"
    ((PASSED++))
else
    echo "❌ FAIL: Available Slot"
fi

if [ "$TEST3_PASS" = true ]; then
    echo "✅ PASS: Business Hours"
    ((PASSED++))
else
    echo "❌ FAIL: Business Hours"
fi

echo ""
echo "Total: $PASSED/$TOTAL tests passed"

if [ $PASSED -eq $TOTAL ]; then
    echo ""
    echo "🎉 All tests passed!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed"
    exit 1
fi
