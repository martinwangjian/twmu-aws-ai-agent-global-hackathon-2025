"""
Real-world A2A Orchestrator Demo

Scenario: Travel Planning Assistant
A travel orchestrator agent helps a user plan a trip to Mauritius,
coordinating with our restaurant booking agent for dinner reservations.
"""
import asyncio
import logging
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
RESTAURANT_AGENT_URL = "https://restaurant-booking-agent.teamwork-mu.net"
TIMEOUT = 60


class TravelOrchestrator:
    """Orchestrator agent that coordinates multiple specialized agents."""
    
    def __init__(self):
        self.restaurant_client = None
        self.conversation_history = []
    
    async def initialize(self):
        """Discover and connect to restaurant agent."""
        logger.info("🔍 Discovering restaurant booking agent...")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as httpx_client:
            # Discover agent capabilities
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=RESTAURANT_AGENT_URL
            )
            agent_card = await resolver.get_agent_card()
            
            logger.info(f"✅ Found: {agent_card.name}")
            logger.info(f"   Skills: {', '.join([s.id for s in agent_card.skills])}")
            
            # Create client
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            self.restaurant_client = factory.create(agent_card)
    
    async def ask_restaurant_agent(self, question: str) -> str:
        """Send message to restaurant agent."""
        msg = Message(
            kind="message",
            role=Role.user,
            parts=[Part(TextPart(kind="text", text=question))],
            message_id=uuid4().hex,
        )
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as httpx_client:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=RESTAURANT_AGENT_URL
            )
            agent_card = await resolver.get_agent_card()
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            async for event in client.send_message(msg):
                if isinstance(event, Message):
                    response_text = ""
                    for part in event.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
                    return response_text
        
        return "No response received"
    
    async def plan_mauritius_trip(self):
        """Execute travel planning scenario."""
        logger.info("\n" + "="*60)
        logger.info("🌴 SCENARIO: Planning a Trip to Mauritius")
        logger.info("="*60)
        
        # Step 1: User request
        user_request = """
        I'm planning a romantic trip to Mauritius next Friday.
        Can you help me book a dinner at a nice Italian restaurant?
        We're 2 people and prefer 7:30 PM.
        """
        logger.info(f"\n👤 User: {user_request.strip()}")
        
        # Step 2: Orchestrator discovers restaurant agent
        await self.initialize()
        
        # Step 3: Check restaurant availability
        logger.info("\n🤖 Orchestrator: Let me check restaurant availability...")
        availability_query = "Is there a table available for 2 people next Friday at 7:30 PM?"
        
        logger.info(f"\n📤 Orchestrator → Restaurant Agent:")
        logger.info(f"   '{availability_query}'")
        
        availability_response = await self.ask_restaurant_agent(availability_query)
        logger.info(f"\n📥 Restaurant Agent → Orchestrator:")
        logger.info(f"   {availability_response}")
        
        # Step 4: Get menu information
        logger.info("\n🤖 Orchestrator: Let me get the menu details...")
        menu_query = "What's on your menu? Any vegetarian options?"
        
        logger.info(f"\n📤 Orchestrator → Restaurant Agent:")
        logger.info(f"   '{menu_query}'")
        
        menu_response = await self.ask_restaurant_agent(menu_query)
        logger.info(f"\n📥 Restaurant Agent → Orchestrator:")
        logger.info(f"   {menu_response}")
        
        # Step 5: Check opening hours
        logger.info("\n🤖 Orchestrator: Confirming restaurant hours...")
        hours_query = "What are your opening hours on Friday?"
        
        logger.info(f"\n📤 Orchestrator → Restaurant Agent:")
        logger.info(f"   '{hours_query}'")
        
        hours_response = await self.ask_restaurant_agent(hours_query)
        logger.info(f"\n📥 Restaurant Agent → Orchestrator:")
        logger.info(f"   {hours_response}")
        
        # Step 6: Orchestrator summarizes for user
        logger.info("\n" + "="*60)
        logger.info("📋 ORCHESTRATOR SUMMARY FOR USER")
        logger.info("="*60)
        summary = f"""
✅ Restaurant Found: La Bella Vita (Italian)
📍 Location: Mauritius
👥 Party Size: 2 people
📅 Date: Next Friday
🕖 Time: 7:30 PM

Availability: {availability_response[:100]}...

Menu Highlights: {menu_response[:100]}...

Opening Hours: {hours_response[:100]}...

Would you like me to proceed with the booking?
        """
        logger.info(summary)
        
        logger.info("\n" + "="*60)
        logger.info("✨ Demo Complete!")
        logger.info("="*60)


async def main():
    """Run the orchestrator demo."""
    orchestrator = TravelOrchestrator()
    await orchestrator.plan_mauritius_trip()


if __name__ == "__main__":
    asyncio.run(main())
