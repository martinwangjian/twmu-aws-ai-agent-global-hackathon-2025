# A2A Orchestrator Examples

Real-world scenarios demonstrating how orchestrator agents interact with our restaurant booking agent via the A2A protocol.

## Quick Demo

```bash
# Run the interactive demo (mock mode)
python examples/run_orchestrator_demo.py
```

## Scenario: Travel Planning Assistant

A travel orchestrator helps users plan trips to Mauritius by coordinating with multiple specialized agents, including our restaurant booking agent.

### The Story

1. **User**: "I'm planning a romantic trip to Mauritius. Book dinner for 2 at 7:30 PM"
2. **Orchestrator**: Discovers restaurant agent via A2A protocol
3. **Orchestrator ↔ Restaurant Agent**: 
   - Check availability
   - Get menu information
   - Confirm opening hours
   - Create booking
4. **Orchestrator**: Presents unified summary to user
5. **Result**: Seamless booking experience across multiple agents

### Key Benefits

- **Loose Coupling**: Orchestrator doesn't need restaurant implementation details
- **Discovery**: Agent capabilities advertised via agent card
- **Standardization**: Common A2A message format
- **Scalability**: Easy to add hotels, activities, transport agents
- **Interoperability**: Works with any A2A-compatible agent

## Files

- `run_orchestrator_demo.py` - Interactive demo script (mock mode)
- `a2a_orchestrator_demo.py` - Full implementation with live API calls
- `a2a_orchestrator_scenario.md` - Detailed scenario documentation

## Running Live Demo

```bash
# Install dependencies
uv pip install a2a-sdk httpx

# Run against deployed agent
python examples/a2a_orchestrator_demo.py

# Or against local container
A2A_TEST_URL="http://localhost:9000" python examples/a2a_orchestrator_demo.py
```

## Real-World Use Cases

### 1. Travel Planning (This Example)
Orchestrator coordinates: restaurants, hotels, activities, transport

### 2. Event Planning
Orchestrator handles: venue, catering, entertainment, invitations

### 3. Corporate Concierge
Orchestrator manages: business travel, dining, meetings, accommodations

### 4. Smart City Services
Orchestrator integrates: tourism, dining, transport, events, emergency services

## Architecture

```
User
  ↓
Travel Orchestrator (Main Agent)
  ├─→ Restaurant Agent (A2A) ← Our Agent
  ├─→ Hotel Agent (A2A)
  ├─→ Activity Agent (A2A)
  └─→ Transport Agent (A2A)
```

Each specialized agent:
- Exposes capabilities via agent card
- Handles domain-specific requests
- Maintains own backend/data
- Communicates via standard A2A protocol

## Demo Output

The demo shows:
- ✅ Agent discovery via `.well-known/agent-card.json`
- ✅ 7 skills advertised (availability, booking, menu, hours, etc.)
- ✅ 4 A2A message exchanges
- ✅ Unified user experience
- ✅ Booking confirmation

Run it to see the full interaction flow!
