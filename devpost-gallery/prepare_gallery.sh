#!/bin/bash
# Prepare images for Devpost gallery (3:2 ratio, 1200x800)

# 1. System Architecture
sips -z 800 1200 ../generated-diagrams/system-architecture.png --out 01-system-architecture.png

# 2. WhatsApp Path Architecture
sips -z 800 1200 ../docs/architecture/whatsapp-path-architecture.png --out 02-whatsapp-architecture.png

# 3. A2A Path Architecture
sips -z 800 1200 ../docs/architecture/a2a-path-architecture.png --out 03-a2a-architecture.png

# 4. WhatsApp Demo - Info Query
sips -z 800 1200 -c 800 1200 ../docs/demo/whatsapp/info.png --out 04-whatsapp-info.png

# 5. WhatsApp Demo - Booking
sips -z 800 1200 -c 800 1200 ../docs/demo/whatsapp/booking.png --out 05-whatsapp-booking.png

# 6. A2A - Customer Delegates
sips -z 800 1200 ../docs/demo/a2a/3-customer-delegate-booking-tasks.png --out 06-a2a-delegate.png

# 7. A2A - Claude Discovery
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/4-claude-use-tools-to-find-availability-discover-resto.png --out 07-a2a-discovery.png

# 8. A2A - Payment Approval
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/6-user-approve-payment.png --out 08-a2a-payment.png

# 9. A2A - Booking Confirmed
sips -z 800 1200 -c 800 1200 ../docs/demo/a2a/7-claude-trigger-payment-got-booking-confirmation.png --out 09-a2a-confirmed.png

# 10. Payment Flow Diagram
sips -z 800 1200 ../docs/architecture/x402-integrated-A2A-message-payment-flow.png --out 10-payment-flow.png

echo "Gallery images prepared in devpost-gallery/"
ls -lh *.png
