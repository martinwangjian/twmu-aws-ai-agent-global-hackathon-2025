#!/usr/bin/env python3
"""
A2A Orchestrator Demo - Travel Planning Scenario

Usage:
  python examples/run_orchestrator_demo.py              # Mock mode
  python examples/run_orchestrator_demo.py --live       # Live API calls
"""
import sys
import time


def print_step(emoji, title, content=""):
    """Print formatted step."""
    print(f"\n{emoji} {title}")
    if content:
        print(f"   {content}")


def print_message(sender, receiver, message):
    """Print A2A message exchange."""
    print(f"\n📤 {sender} → {receiver}:")
    print(f'   "{message}"')


def print_response(sender, receiver, response):
    """Print A2A response."""
    print(f"\n📥 {sender} → {receiver}:")
    for line in response.split('\n'):
        if line.strip():
            print(f"   {line}")


def run_mock_demo():
    """Run demo with mock responses."""
    print("\n" + "="*70)
    print("🌴 A2A ORCHESTRATOR DEMO: Travel Planning to Mauritius")
    print("="*70)
    
    # Step 1: User request
    print_step("👤", "USER REQUEST")
    user_request = """I'm planning a romantic trip to Mauritius next Friday.
Can you help me book a dinner at a nice Italian restaurant?
We're 2 people and prefer 7:30 PM."""
    print(f'   "{user_request}"')
    time.sleep(1)
    
    # Step 2: Discovery
    print_step("🔍", "AGENT DISCOVERY")
    print("   Travel Orchestrator discovering available agents...")
    time.sleep(1)
    
    print("\n   📡 GET /.well-known/agent-card.json")
    print("   🌐 https://restaurant-booking-agent.teamwork-mu.net")
    time.sleep(1)
    
    print("\n   ✅ Found: La Bella Vita Restaurant Agent")
    print("   📋 Skills: check-availability, create-booking, cancel-booking,")
    print("              get-menu, get-opening-hours, get-pricing, get-allergens")
    time.sleep(1)
    
    # Step 3: Check availability
    print_step("📅", "CHECK AVAILABILITY")
    print_message(
        "Travel Orchestrator",
        "Restaurant Agent",
        "Is there a table available for 2 people next Friday at 7:30 PM?"
    )
    time.sleep(1)
    
    print_response(
        "Restaurant Agent",
        "Travel Orchestrator",
        """Yes, we have availability for 2 guests on Friday, October 17th at 7:30 PM.
La Bella Vita offers authentic Italian cuisine in a romantic beachfront setting.
Would you like to proceed with the reservation?"""
    )
    time.sleep(1)
    
    # Step 4: Get menu
    print_step("🍝", "GET MENU INFORMATION")
    print_message(
        "Travel Orchestrator",
        "Restaurant Agent",
        "What's on your menu? Any vegetarian options?"
    )
    time.sleep(1)
    
    print_response(
        "Restaurant Agent",
        "Travel Orchestrator",
        """Our menu features:
• Antipasti: Bruschetta, Caprese Salad
• Pasta: Carbonara, Penne Arrabbiata (vegetarian)
• Mains: Osso Buco, Grilled Sea Bass, Eggplant Parmigiana (vegetarian)
• Desserts: Tiramisu, Panna Cotta

We have excellent vegetarian options including our signature
Eggplant Parmigiana and fresh pasta dishes."""
    )
    time.sleep(1)
    
    # Step 5: Get hours
    print_step("⏰", "CONFIRM OPENING HOURS")
    print_message(
        "Travel Orchestrator",
        "Restaurant Agent",
        "What are your opening hours on Friday?"
    )
    time.sleep(1)
    
    print_response(
        "Restaurant Agent",
        "Travel Orchestrator",
        "We're open Friday from 6:00 PM to 11:00 PM. Kitchen closes at 10:30 PM."
    )
    time.sleep(1)
    
    # Step 6: Summary
    print("\n" + "="*70)
    print("📋 ORCHESTRATOR SUMMARY FOR USER")
    print("="*70)
    
    summary = """
✅ Perfect! I found La Bella Vita, an Italian restaurant in Mauritius.

📍 Booking Details:
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
3. Add this to your trip itinerary?
"""
    print(summary)
    
    # Step 7: Booking
    print_step("✅", "USER CONFIRMS")
    print('   "Yes, please confirm the booking!"')
    time.sleep(1)
    
    print_step("📝", "CREATE BOOKING")
    print_message(
        "Travel Orchestrator",
        "Restaurant Agent",
        "Create booking for 2 people, Friday Oct 17 at 7:30 PM. Name: John Smith"
    )
    time.sleep(1)
    
    print_response(
        "Restaurant Agent",
        "Travel Orchestrator",
        """✅ Booking confirmed!
Confirmation #: RES-2024-10-17-001

We've sent a confirmation to your phone.
Looking forward to welcoming you!"""
    )
    time.sleep(1)
    
    print("\n" + "="*70)
    print("✨ DEMO COMPLETE!")
    print("="*70)
    print("\n🎯 Key Takeaways:")
    print("   • Orchestrator discovered agent via A2A protocol")
    print("   • 4 interactions: availability, menu, hours, booking")
    print("   • Seamless coordination between specialized agents")
    print("   • User gets unified travel planning experience")
    print("\n")


def main():
    """Run the demo."""
    if "--live" in sys.argv:
        print("❌ Live mode requires a2a-sdk. Use mock mode for now.")
        print("   Run: python examples/run_orchestrator_demo.py")
        sys.exit(1)
    
    run_mock_demo()


if __name__ == "__main__":
    main()
