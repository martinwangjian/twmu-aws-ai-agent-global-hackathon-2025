# Real-World A2A Booking System Demo

## Scenario: Weekend Getaway Planning

**User Story**: Sarah is planning a romantic weekend in Mauritius and wants to book dinner at an Italian restaurant for Friday evening.

---

## Demo Flow

### Phase 1: Agent Discovery

**User Request** (via Claude Desktop with MCP):

```
"I'm planning a romantic dinner in Mauritius next Friday at 7:30 PM for 2 people.
We love Italian food and need vegetarian options. Can you help me find and book a restaurant?"
```

**Orchestrator Action**:

```
🔍 Discovering available restaurant agents...

GET https://restaurant-booking-agent.teamwork-mu.net/.well-known/agent-card.json

✅ Found: La Bella Vita Restaurant Agent
   - Location: Mauritius
   - Cuisine: Authentic Italian
   - Capabilities: 1 skill (invoke_booking_agent)
   - Protocol: A2A v0.3.0
```

---

### Phase 2: Information Gathering

**Orchestrator → Restaurant Agent** (via A2A Protocol):

```json
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "kind": "message",
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "Tell me about your restaurant. Do you have vegetarian options? What are your opening hours on Friday?"
        }
      ],
      "message_id": "msg_001"
    }
  },
  "id": 1
}
```

**Restaurant Agent Response**:

```
🍝 La Bella Vita - Authentic Italian Cuisine

📍 Location: Beachfront, Grand Baie, Mauritius
⭐ Rating: 4.8/5 (250+ reviews)

🌿 Vegetarian Options:
   • Margherita Pizza (wood-fired)
   • Penne Arrabbiata (spicy tomato sauce)
   • Eggplant Parmigiana (signature dish)
   • Caprese Salad (buffalo mozzarella)
   • Mushroom Risotto (truffle oil)

⏰ Friday Hours: 6:00 PM - 11:00 PM
   Kitchen closes: 10:30 PM

💰 Price Range: $$$ (MUR 800-1500 per person)
🌅 Ambiance: Romantic, beachfront seating available
```

---

### Phase 3: Availability Check

**Orchestrator → Restaurant Agent**:

```
"Check availability for 2 people on Friday, October 17, 2025 at 7:30 PM.
We prefer outdoor seating if available."
```

**Restaurant Agent** (queries Google Calendar via AgentCore):

```
✅ Availability Confirmed!

📅 Date: Friday, October 17, 2025
⏰ Time: 7:30 PM
👥 Party Size: 2 people
🪑 Seating: Outdoor beachfront table available
🌅 Sunset: 6:15 PM (perfect timing for sunset views!)

⚠️ Note: Friday evenings are popular. Recommend booking soon.
```

---

### Phase 4: Menu Recommendations

**Orchestrator → Restaurant Agent**:

```
"What vegetarian dishes would you recommend for a romantic dinner?"
```

**Restaurant Agent** (queries Knowledge Base):

```
👨‍🍳 Chef's Recommendations for Vegetarian Romantic Dinner:

🥗 Starter:
   Caprese Salad - Fresh buffalo mozzarella, heirloom tomatoes,
   basil, aged balsamic (MUR 450)

🍝 Main Course (Choose One):
   1. Eggplant Parmigiana ⭐ SIGNATURE
      Layers of grilled eggplant, tomato sauce, mozzarella,
      parmesan, fresh basil (MUR 850)

   2. Mushroom Risotto
      Arborio rice, porcini mushrooms, truffle oil,
      parmesan (MUR 950)

🍰 Dessert:
   Tiramisu - Classic Italian, house-made (MUR 350)

🍷 Wine Pairing:
   Chianti Classico (vegetarian-friendly) - Glass MUR 400

💡 Total Estimate: MUR 2,400-2,600 for two
```

---

### Phase 5: Booking Confirmation

**Orchestrator → Restaurant Agent**:

```
"Perfect! Please create a booking with these details:
- Name: Sarah Johnson
- Phone: +230-5999-8888
- Email: sarah.j@email.com
- Date: Friday, October 17, 2025
- Time: 7:30 PM
- Party Size: 2
- Seating: Outdoor beachfront
- Dietary: Vegetarian options
- Special: Romantic occasion"
```

**Restaurant Agent** (creates Google Calendar event):

```
✅ BOOKING CONFIRMED!

📋 Confirmation Details:
   Booking ID: LBV-20251017-1930-002
   Restaurant: La Bella Vita
   Guest: Sarah Johnson
   Phone: +230-5999-8888
   Email: sarah.j@email.com

   Date: Friday, October 17, 2025
   Time: 7:30 PM (arrive by 7:25 PM)
   Party Size: 2 people
   Table: Outdoor Beachfront #7

   Special Arrangements:
   ✓ Vegetarian menu prepared
   ✓ Romantic table setup
   ✓ Sunset view reserved
   ✓ Complimentary prosecco on arrival

📧 Confirmation sent to: sarah.j@email.com
📱 SMS reminder: 24 hours before

📍 Directions:
   La Bella Vita, Royal Road, Grand Baie
   GPS: -20.0104, 57.5828
   Parking: Available on-site

❓ Questions? Call +230-263-5555

🙏 Looking forward to welcoming you!
```

---

### Phase 6: Follow-up Services

**Orchestrator → User**:

```
✅ Your romantic dinner is all set!

📅 Booking Summary:
   • Restaurant: La Bella Vita (Italian)
   • Date: Friday, Oct 17 at 7:30 PM
   • Party: 2 people
   • Location: Beachfront, Grand Baie
   • Confirmation: LBV-20251017-1930-002

🎯 What's Next?

Would you like me to help with:

1. 🚗 Transportation
   - Book taxi/Uber to restaurant
   - Arrange hotel pickup

2. 🏨 Accommodation
   - Find nearby hotels
   - Check weekend packages

3. 🎭 Activities
   - Sunset catamaran cruise (before dinner)
   - Beach activities (Saturday)
   - Spa treatments

4. 📸 Special Touches
   - Photographer for dinner
   - Flower delivery to table
   - Custom cake for occasion

Just let me know what else you need!
```

---

## Technical Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Claude Desktop                         │
│                  (User Interface)                         │
└────────────────────┬─────────────────────────────────────┘
                     │ MCP Protocol
                     ▼
┌──────────────────────────────────────────────────────────┐
│              A2A Orchestrator MCP Server                  │
│         (Docker: a2a-orchestrator-mcp)                    │
│                                                           │
│  Tools:                                                   │
│  • discover_and_call_agent                                │
│                                                           │
│  Uses: Strands A2AClientToolProvider                      │
└────────────────────┬─────────────────────────────────────┘
                     │ A2A Protocol (HTTPS)
                     ▼
┌──────────────────────────────────────────────────────────┐
│           Restaurant Booking Agent (A2A Server)           │
│    https://restaurant-booking-agent.teamwork-mu.net       │
│                                                           │
│  Deployment: ECS Fargate                                  │
│  Framework: Strands A2AServer                             │
│  Protocol: A2A v0.3.0                                     │
└────────────────────┬─────────────────────────────────────┘
                     │ Bedrock API
                     ▼
┌──────────────────────────────────────────────────────────┐
│              AWS Bedrock AgentCore Runtime                │
│         (agentcore_mcp_agent-9qQrwZB5ns)                  │
│                                                           │
│  Components:                                              │
│  • Agent: Booking assistant with tools                    │
│  • Model: Amazon Nova Pro                                 │
│  • Memory: AgentCore Memory (semantic search)             │
│  • Tools:                                                 │
│    - Google Calendar (via AgentCore Gateway)              │
│    - Knowledge Base (restaurant info)                     │
└───────────────────────────────────────────────────────────┘
```

---

## Key Features Demonstrated

### 1. **Agent Discovery** (A2A Protocol)

- Automatic discovery via `.well-known/agent-card.json`
- No hardcoded endpoints
- Dynamic capability detection

### 2. **Natural Language Interface**

- User speaks naturally
- Orchestrator translates to A2A messages
- Agent responds conversationally

### 3. **Multi-Turn Conversation**

- Information gathering
- Availability checking
- Menu recommendations
- Booking confirmation

### 4. **Backend Integration**

- Google Calendar for bookings
- Knowledge Base for restaurant info
- Memory for conversation context

### 5. **Real-World Booking Flow**

- Check availability
- Provide recommendations
- Confirm details
- Send confirmations

---

## Running the Demo

### Prerequisites

```bash
# 1. AWS credentials in .env
source .env

# 2. Update Claude Desktop config
./scripts/update-claude-config.sh

# 3. Restart Claude Desktop
killall Claude && open -a Claude
```

### Demo Script

**In Claude Desktop, paste:**

```
I'm planning a romantic dinner in Mauritius next Friday at 7:30 PM for 2 people.
We love Italian food and need vegetarian options. Can you help me find and book a restaurant?

Contact: Sarah Johnson, +230-5999-8888, sarah.j@email.com
```

**Expected Flow:**

1. Agent discovers La Bella Vita
2. Checks availability for Friday 7:30 PM
3. Provides vegetarian menu options
4. Confirms booking
5. Sends confirmation details

---

## Success Metrics

✅ **Agent Discovery**: < 2 seconds
✅ **Availability Check**: < 5 seconds
✅ **Menu Query**: < 3 seconds
✅ **Booking Creation**: < 5 seconds
✅ **Total Flow**: < 20 seconds

---

## Troubleshooting

### Issue: "Technical difficulties with booking system"

**Cause**: AgentCore Runtime permissions
**Fix**: Check IAM policy includes `bedrock-agentcore:InvokeAgentRuntime` with `/*` wildcard

### Issue: "Agent not found"

**Cause**: A2A endpoint not accessible
**Fix**: Verify ECS service is running and ALB is healthy

### Issue: "Internal error"

**Cause**: Bedrock model permissions
**Fix**: Check IAM policy includes `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`

---

## Future Enhancements

### Phase 2: Multi-Agent Orchestration

```
Travel Orchestrator
├── Restaurant Agent (La Bella Vita) ✅ DONE
├── Hotel Agent (Booking.com API)
├── Activity Agent (Tours, Spa)
└── Transport Agent (Taxi, Car Rental)
```

### Phase 3: Payment Integration

- AP2 protocol for payments
- Deposit handling
- Cancellation refunds

### Phase 4: Personalization

- User preferences in memory
- Dietary restrictions
- Favorite cuisines
- Budget constraints

---

## Business Value

### For Restaurants

- 24/7 automated booking
- Reduced phone calls
- Better table management
- Customer data collection

### For Users

- Instant availability
- Menu browsing
- Easy booking
- Confirmation tracking

### For Platform

- Scalable architecture
- Easy agent addition
- Standard protocol
- Low maintenance

---

## Demo Video Script

**[0:00-0:15] Introduction**
"Watch how AI agents work together to book your perfect dinner"

**[0:15-0:30] Discovery**
"The orchestrator discovers La Bella Vita restaurant agent"

**[0:30-0:45] Information**
"Gets menu, hours, and vegetarian options"

**[0:45-1:00] Availability**
"Checks real-time availability via Google Calendar"

**[1:00-1:15] Booking**
"Creates confirmed reservation with all details"

**[1:15-1:30] Confirmation**
"Sends email and SMS confirmation automatically"

**[1:30-1:45] Closing**
"All powered by AWS Bedrock AgentCore and A2A protocol"
