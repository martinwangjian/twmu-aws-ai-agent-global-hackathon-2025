# WhatsApp Integration Setup Guide

## Why Manual Setup is Required

AWS End User Messaging (Social) for WhatsApp Business is **not yet supported in AWS CDK**. The service requires manual configuration through the AWS Console to:

1. **Verify Business Identity**: WhatsApp requires business verification
2. **Phone Number Registration**: Link your WhatsApp Business phone number
3. **Facebook Business Manager**: Connect to Meta's platform
4. **Webhook Configuration**: Point WhatsApp events to AWS infrastructure

**CDK handles**: SNS Topic, Lambda, Secrets Manager (infrastructure)
**Manual setup**: WhatsApp Business channel, phone number verification

---

## Prerequisites

- AWS Account with End User Messaging access
- WhatsApp Business Account
- Facebook Business Manager account
- Phone number for WhatsApp Business

---

## Step-by-Step Setup

### Step 1: Deploy Infrastructure

```bash
# Deploy WhatsApp stack (creates SNS Topic)
cd cdk_infra
source .venv/bin/activate
export $(cat ../.env | xargs)
cdk deploy WhatsAppStack
```

**Save the SNS Topic ARN** from outputs:

```
WhatsAppStack.SNSTopicArn = arn:aws:sns:us-east-1:ACCOUNT:WhatsAppMessages
```

---

### Step 2: Configure AWS End User Messaging (Console)

1. **Open AWS Console** → **End User Messaging** → **Social messaging**

2. **Create WhatsApp Channel**:
   - Click "Create channel"
   - Select "WhatsApp"
   - Follow WhatsApp Business verification flow

3. **Connect Facebook Business Manager**:
   - Link your Facebook Business Manager account
   - Authorize AWS to access WhatsApp Business API

4. **Register Phone Number**:
   - Add your WhatsApp Business phone number
   - Complete verification (SMS/call)
   - **Save the Phone Number ID** (format: `waba-xxxxx`)

5. **Configure Event Destination**:
   - Select "Amazon SNS"
   - **Paste SNS Topic ARN** from Step 1
   - Enable message events

6. **Test Connection**:
   - Send test message from AWS Console
   - Verify Lambda receives event

---

### Step 3: Update Environment Variables

Add Phone Number ID to `.env`:

```bash
# WhatsApp Configuration
# Obtained from AWS End User Messaging (Social) console
WHATSAPP_PHONE_NUMBER_ID="waba-01234567890abcdef"
```

**Why this variable?**

- Required to send WhatsApp replies via API
- Identifies your WhatsApp Business phone number
- Used by Lambda to send messages back to users

---

### Step 4: Redeploy with Phone Number ID

```bash
# Redeploy WhatsApp stack with phone number ID
cd cdk_infra
export $(cat ../.env | xargs)
cdk deploy WhatsAppStack
```

Lambda now has `WHATSAPP_PHONE_NUMBER_ID` environment variable.

---

### Step 5: Test End-to-End

**Send WhatsApp message** to your business number:

```
"Hello, what services do you offer?"
```

**Check Lambda logs**:

```bash
aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator* --follow
```

**Expected flow**:

```
WhatsApp Message
  → AWS End User Messaging
  → SNS Topic
  → Lambda Orchestrator
  → AgentCore
  → Bedrock
  → Response (logged)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp User                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         AWS End User Messaging (Social)                     │
│         [MANUAL SETUP REQUIRED]                             │
│                                                             │
│  • WhatsApp Business Channel                                │
│  • Phone Number: WHATSAPP_PHONE_NUMBER_ID                   │
│  • Event Destination: SNS Topic ARN                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         SNS Topic: WhatsAppMessages                         │
│         [CDK MANAGED]                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: WhatsAppOrchestrator                        │
│         [CDK MANAGED]                                       │
│                                                             │
│  Environment Variables:                                     │
│  • AGENTCORE_RUNTIME_ARN                                    │
│  • WHATSAPP_PHONE_NUMBER_ID (from .env)                     │
│  • WHATSAPP_SECRET_ARN                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         AgentCore Runtime → Bedrock                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

### `WHATSAPP_PHONE_NUMBER_ID`

**Purpose**: Identifies your WhatsApp Business phone number for sending replies

**Format**: `waba-` followed by alphanumeric ID (e.g., `waba-01234567890abcdef`)

**Where to find**:

1. AWS Console → End User Messaging → Social messaging
2. Select your WhatsApp channel
3. Copy "Phone Number ID" from channel details

**Why required**:

- AWS End User Messaging API requires this ID to send messages
- Each WhatsApp Business phone has a unique ID
- Cannot be automated (requires business verification)

**When to set**:

- After completing WhatsApp Business setup in AWS Console
- Before deploying stack with reply functionality
- Can be empty initially (receive-only mode)

---

## Troubleshooting

### Messages not received by Lambda

**Check**:

1. SNS Topic ARN correctly configured in AWS End User Messaging
2. Lambda has permission to be invoked by SNS (auto-configured by CDK)
3. WhatsApp channel status is "Active"

**Verify**:

```bash
# Check SNS subscription
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:WhatsAppMessages
```

### Cannot send replies

**Check**:

1. `WHATSAPP_PHONE_NUMBER_ID` set in `.env`
2. Lambda has environment variable (redeploy after setting)
3. WhatsApp Business phone number verified

---

## Security Notes

- **Never commit** `.env` file (contains credentials)
- Store WhatsApp API tokens in **Secrets Manager** (already configured)
- Use **IAM roles** for Lambda permissions (CDK managed)
- **Rotate secrets** regularly via Secrets Manager

---

## Cost Considerations

- **AWS End User Messaging**: Pay per message
- **SNS**: Pay per notification (minimal)
- **Lambda**: Pay per invocation
- **AgentCore**: Pay per runtime usage
- **Bedrock**: Pay per token

**Estimated cost**: ~$0.01-0.05 per conversation

---

## Next Steps

After setup complete:

1. Test with real WhatsApp messages
2. Implement reply functionality (send messages back)
3. Add conversation state management
4. Integrate Google Calendar for bookings
5. Add business-specific knowledge base

---

## References

- [AWS End User Messaging Documentation](https://docs.aws.amazon.com/social-messaging/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/)
