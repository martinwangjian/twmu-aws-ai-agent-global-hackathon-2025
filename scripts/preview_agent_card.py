#!/usr/bin/env python3
"""Preview the A2A spec-compliant agent card"""

import json

# A2A spec-compliant agent card with comprehensive skills
agent_card = {
    "name": "La Bella Vita Restaurant Agent",
    "description": "Restaurant booking and information agent for La Bella Vita in Mauritius",
    "url": "https://booking-agent.example.com/a2a/v1",
    "version": "1.0.0",
    "protocolVersion": "1.0.0",
    "skills": [
        {
            "id": "check-availability",
            "description": "Check restaurant table availability for specific date and time",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {"date": "2025-10-15", "time": "19:00", "party_size": 2},
                    "output": {"available": True, "slots": ["19:00", "19:30", "20:00"]},
                }
            ],
        },
        {
            "id": "create-booking",
            "description": "Create a restaurant table booking",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {
                        "date": "2025-10-15",
                        "time": "19:00",
                        "party_size": 2,
                        "customer_name": "John Doe",
                        "phone": "+230-5123-4567",
                    },
                    "output": {"booking_id": "BK123", "status": "confirmed"},
                }
            ],
        },
        {
            "id": "cancel-booking",
            "description": "Cancel an existing restaurant booking",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {"booking_id": "BK123"},
                    "output": {"status": "cancelled", "message": "Booking cancelled successfully"},
                }
            ],
        },
        {
            "id": "get-menu",
            "description": "Get restaurant menu with dishes and prices",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {"category": "mains"},
                    "output": {
                        "category": "mains",
                        "items": [
                            {
                                "name": "Grilled Salmon",
                                "price": "MUR 450",
                                "description": "Fresh Atlantic salmon",
                            }
                        ],
                    },
                }
            ],
        },
        {
            "id": "get-opening-hours",
            "description": "Get restaurant opening hours and schedule",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {},
                    "output": {
                        "hours": {"monday": "11:00 AM - 10:00 PM", "friday": "11:00 AM - 11:00 PM"},
                        "timezone": "Indian/Mauritius (UTC+4)",
                    },
                }
            ],
        },
        {
            "id": "get-pricing",
            "description": "Get pricing information for menu items or services",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {"item": "Grilled Salmon"},
                    "output": {"item": "Grilled Salmon", "price": "MUR 450", "currency": "MUR"},
                }
            ],
        },
        {
            "id": "get-allergens",
            "description": "Get allergen information for menu items",
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
            "examples": [
                {
                    "input": {"item": "Grilled Salmon"},
                    "output": {
                        "item": "Grilled Salmon",
                        "allergens": ["fish"],
                        "dietary_info": ["gluten-free", "dairy-free"],
                    },
                }
            ],
        },
    ],
    "preferredTransport": "JSONRPC",
    "additionalInterfaces": [],
    "defaultInputModes": ["application/json"],
    "defaultOutputModes": ["application/json"],
}

print("=" * 80)
print("LA BELLA VITA - A2A AGENT CARD")
print("=" * 80)
print("\n✅ Endpoint: GET https://<ALB-DNS>/.well-known/agent-card.json")
print("\nAgent Card JSON:\n")
print(json.dumps(agent_card, indent=2))
print("\n" + "=" * 80)
print("\nSkills Available:")
print("=" * 80)
for skill in agent_card["skills"]:
    print(f"  • {skill['id']}: {skill['description']}")
print("\n" + "=" * 80)
print("\nHow to Use:")
print("=" * 80)
print("""
# Discovery
curl https://<ALB-DNS>/.well-known/agent-card.json

# With A2A orchestrator
from strands_tools.a2a_client import A2AClientToolProvider

provider = A2AClientToolProvider(
    known_agent_urls=['https://<ALB-DNS>']
)

orchestrator = Agent(
    name='Travel Orchestrator',
    tools=provider.tools
)

# Check availability
response = orchestrator('Check if La Bella Vita has tables for 2 on Oct 15 at 7pm')

# Get menu
response = orchestrator('What does La Bella Vita serve?')

# Check allergens
response = orchestrator('Does the Grilled Salmon contain any allergens?')
""")
