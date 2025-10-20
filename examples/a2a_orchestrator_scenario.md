# Real-World A2A Orchestrator Scenario

## Scenario: Travel Planning Assistant

A travel orchestrator agent helps users plan trips by coordinating with multiple specialized agents, including our restaurant booking agent.

---

## The Flow

### 1. User Request
```
👤 User → Travel Orchestrator:
"I'm planning a romantic trip to Mauritius next Friday. 
Can you help me book a dinner at a nice Italian restaurant? 
We're 2 people and prefer 7:30 PM."
```

### 2. Agent Discovery
```
🤖 Travel Orchestrator:
"Let me find available restaurant agents in Mauritius..."

📡 Discovery Request:
GET https://restaurant-booking-agent.teamwork-mu.net/.well-known/agent-card.json

📥 Agent Card Response:
{
  "name": "La Bella Vita Restaurant Agent",
  "description": "Restaurant booking and information agent",
  "skills": [
    "check-availability",
    "create-booking",
    "cancel-booking",
    "get-menu",
    "get-opening-hours",
    "get-pricing",
    "get-allergens"
  ]
}

✅ Found: La Bella Vita Restaurant Agent
   Capabilities: 7 skills available
```

### 3. Check Availability
```
🤖 Travel Orchestrator → Restaurant Agent:
"Is there a table available for 2 people next Friday at 7:30 PM?"

📤 A2A Message:
POST https://restaurant-booking-agent.teamwork-mu.net/a2a/v1/messages
{
  "kind": "message",
  "role": "user",
  "parts": [{"kind": "text", "text": "Is there a table available..."}],
  "message_id": "abc123"
}

📥 Restaurant Agent Response:
"Yes, we have availability for 2 guests on Friday, October 17th at 7:30 PM. 
La Bella Vita offers authentic Italian cuisine in a romantic beachfront setting. 
Would you like to proceed with the reservation?"
```

### 4. Get Menu Information
```
🤖 Travel Orchestrator → Restaurant Agent:
"What's on your menu? Any vegetarian options?"

📥 Restaurant Agent Response:
"Our menu features:
- Antipasti: Bruschetta, Caprese Salad
- Pasta: Carbonara, Penne Arrabbiata (vegetarian)
- Mains: Osso Buco, Grilled Sea Bass, Eggplant Parmigiana (vegetarian)
- Desserts: Tiramisu, Panna Cotta

We have excellent vegetarian options including our signature 
Eggplant Parmigiana and fresh pasta dishes."
```

### 5. Confirm Details
```
🤖 Travel Orchestrator → Restaurant Agent:
"What are your opening hours on Friday?"

📥 Restaurant Agent Response:
"We're open Friday from 6:00 PM to 11:00 PM. 
Kitchen closes at 10:30 PM."
```

### 6. Orchestrator Summary
```
🤖 Travel Orchestrator → User:

"✅ Perfect! I found La Bella Vita, an Italian restaurant in Mauritius.

📋 Booking Details:
   • Restaurant: La Bella Vita
   • Date: Friday, October 17th
   • Time: 7:30 PM
   • Party Size: 2 people
   • Cuisine: Authentic Italian
   • Setting: Romantic beachfront

🍝 Menu Highlights:
   • Fresh pasta dishes
   • Seafood specialties
   • Excellent vegetarian options
   • Homemade desserts

⏰ Opening Hours:
   • Friday: 6:00 PM - 11:00 PM

Would you like me to:
1. Confirm this booking?
2. Check other restaurants?
3. Add this to your trip itinerary?"
```

### 7. Complete Booking
```
👤 User → Travel Orchestrator:
"Yes, please confirm the booking!"

🤖 Travel Orchestrator → Restaurant Agent:
"Please create a booking for 2 people on Friday, October 17th at 7:30 PM. 
Name: John Smith, Phone: +230-5123-4567"

📥 Restaurant Agent Response:
"✅ Booking confirmed!
   Confirmation #: RES-2024-10-17-001
   
   We've sent a confirmation to your phone.
   Looking forward to welcoming you!"

🤖 Travel Orchestrator → User:
"✅ All set! Your dinner reservation is confirmed.
   I've added it to your Mauritius trip itinerary.
   
   Next, would you like me to help with:
   • Hotel recommendations
   • Activity bookings
   • Transportation arrangements"
```

---

## Technical Flow Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ "Book dinner in Mauritius"
       ▼
┌─────────────────────┐
│ Travel Orchestrator │ (Main Agent)
└──────┬──────────────┘
       │
       │ 1. Discover agents
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
┌──────────────────┐            ┌──────────────────┐
│ Restaurant Agent │ (A2A)      │  Hotel Agent     │
│ La Bella Vita    │            │  (Future)        │
└──────┬───────────┘            └──────────────────┘
       │
       │ 2. Check availability
       │ 3. Get menu
       │ 4. Get hours
       │ 5. Create booking
       │
       ▼
┌──────────────────┐
│ AgentCore Runtime│
│ (Backend)        │
└──────┬───────────┘
       │
       ├─→ Knowledge Base (restaurant info)
       ├─→ Calendar Lambda (bookings)
       └─→ Memory (conversation context)
```

---

## Key Benefits of A2A Protocol

1. **Loose Coupling**: Orchestrator doesn't need to know implementation details
2. **Discovery**: Agents advertise their capabilities via agent cards
3. **Standardization**: Common message format across all agents
4. **Scalability**: Easy to add new specialized agents
5. **Interoperability**: Works with agents from different providers

---

## Running the Demo

```bash
# Install dependencies
uv pip install a2a-sdk httpx

# Run the demo
python examples/a2a_orchestrator_demo.py

# Or test against local container
A2A_TEST_URL="http://localhost:9000" python examples/a2a_orchestrator_demo.py
```

---

## Real-World Use Cases

### 1. Travel Planning (This Example)
- Orchestrator coordinates: restaurants, hotels, activities, transport
- Each specialized agent handles its domain
- User gets unified experience

### 2. Event Planning
- Orchestrator: venue booking, catering, entertainment
- Restaurant agent: handles catering quotes and bookings

### 3. Corporate Concierge
- Orchestrator: business travel, dining, meetings
- Restaurant agent: team dinners, client entertainment

### 4. Smart City Services
- Orchestrator: tourism, dining, transport, events
- Restaurant agent: part of city's dining ecosystem
