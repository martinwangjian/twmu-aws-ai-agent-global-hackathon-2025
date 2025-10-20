#!/bin/bash
# Use only manual images from docs/

# 1. WhatsApp Path Architecture (manual)
sips -z 800 1200 ../docs/architecture/whatsapp-path-architecture.png --out 01-whatsapp-architecture.png

# 2. A2A Path Architecture (manual)
sips -z 800 1200 ../docs/architecture/a2a-path-architecture.png --out 02-a2a-architecture.png

# 3. WhatsApp Demo - Info Query
sips -z 800 1200 -c 800 1200 ../docs/demo/whatsapp/info.png --out 03-whatsapp-info.png

# 4. WhatsApp Demo - Booking
sips -z 800 1200 -c 800 1200 ../docs/demo/whatsapp/booking.png --out 04-whatsapp-booking.png

# 5. A2A - Customer Delegates
sips -z 800 1200 ../docs/demo/a2a/3-customer-delegate-booking-tasks.png --out 05-a2a-delegate.png

# 6. A2A - Claude Discovery
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/4-claude-use-tools-to-find-availability-discover-resto.png --out 06-a2a-discovery.png

# 7. A2A - Payment Approval
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/6-user-approve-payment.png --out 07-a2a-payment.png

# 8. A2A - Booking Confirmed
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/7-claude-trigger-payment-got-booking-confirmation.png --out 08-a2a-confirmed.png

# 9. Payment Flow Diagram (manual)
sips -z 800 1200 ../docs/architecture/x402-integrated-A2A-message-payment-flow.png --out 09-payment-flow.png

echo "Gallery recreated with manual images only"
ls -lh *.png
