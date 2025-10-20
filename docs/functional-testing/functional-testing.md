# Functional Testing Guide

## Overview

---

## Prerequisites

### Required

- ✅ Python 3.11+
- ✅ Virtual environment activated
- ✅ AWS Account with Bedrock access
- ✅ Valid AWS credentials (temporary or permanent)
- ✅ Nova Pro model access enabled in AWS Console

### Optional

- AWS CLI configured (for credential verification)
- Access to AWS Console (for model access setup)

---

## Quick Start (5 Minutes)

### 1. Activate Virtual Environment

```bash
cd aws-ai-agent-global-hackathon-2025
source venv/bin/activate
```

**Expected output:**

```
(venv) user@machine:~/project$
```

### 2. Verify Dependencies

```bash
pip list | grep -E "(strands|bedrock|boto3)"
```

**Expected packages:**

- `strands-agents` ≥ 1.0.0
- `bedrock-agentcore` ≥ 0.1.0
- `boto3` ≥ 1.35.0

### 3. Configure AWS Credentials

Edit `.env` file:

```bash
cp .env.example .env  # If .env doesn't exist
nano .env             # Or use your preferred editor
```

**Required configuration:**

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjE...  # Only for temporary credentials

# Bedrock Configuration
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### 4. Run Functional Test

```bash
python -m src.agents.simple_qa_agent
```

**Expected output (success):**

```
============================================================
============================================================

Model: us.amazon.nova-pro-v1:0
Region: us-east-1

Question: What is Amazon Bedrock and how does it work?

Thinking...

============================================================
Answer:
============================================================
Amazon Bedrock is a fully managed service that provides access
to foundation models from leading AI companies through a single
API. It allows developers to build and scale generative AI
applications without managing infrastructure...

[Full AI-generated answer]

============================================================
✅ Agent test completed successfully!
============================================================
```

---

## Detailed Test Procedures

### Test 1: Basic Functionality Test

**Purpose:** Verify agent can answer the hardcoded question

**Steps:**

1. Activate virtualenv

   ```bash
   source venv/bin/activate
   ```

2. Run the agent

   ```bash
   python -m src.agents.simple_qa_agent
   ```

3. Verify output contains:
   - ✅ Model ID: `us.amazon.nova-pro-v1:0`
   - ✅ Region: `us-east-1`
   - ✅ Question displayed
   - ✅ Answer received (non-empty text)
   - ✅ Success message

**Pass criteria:**

- No errors
- Answer is coherent and relevant to Amazon Bedrock
- Execution time: 2-10 seconds

### Test 2: Custom Question Test

**Purpose:** Verify agent can answer custom questions

**Steps:**

1. Open Python interactive shell

   ```bash
   source venv/bin/activate
   python
   ```

2. Test with custom question

   ```python
   from src.agents.simple_qa_agent import invoke

   # Test custom question
   result = invoke({"prompt": "What are the key features of AWS Lambda?"})
   print(result['result'])
   ```

3. Verify output contains:
   - ✅ Relevant answer about AWS Lambda
   - ✅ No error in response
   - ✅ Metadata includes model and region

**Pass criteria:**

- Answer is relevant to the question
- Response format is correct (dict with 'result' key)
- No exceptions raised

### Test 3: Error Handling Test

**Purpose:** Verify agent handles errors gracefully

**Steps:**

1. Temporarily break credentials (backup `.env` first)

   ```bash
   cp .env .env.backup
   echo "AWS_ACCESS_KEY_ID=INVALID" >> .env
   ```

2. Run the agent

   ```bash
   python -m src.agents.simple_qa_agent
   ```

3. Verify error handling:
   - ✅ Error message displayed
   - ✅ No application crash
   - ✅ Error includes details

4. Restore credentials
   ```bash
   mv .env.backup .env
   ```

**Pass criteria:**

- Error message is clear and informative
- Application exits gracefully
- No stack traces exposed to user

### Test 4: Response Format Test

**Purpose:** Verify response structure is correct

**Steps:**

1. Run test in Python

   ```python
   from src.agents.simple_qa_agent import invoke

   result = invoke({"prompt": "What is AWS?"})

   # Verify structure
   assert "result" in result
   assert "model" in result
   assert "region" in result
   assert result["model"] == "us.amazon.nova-pro-v1:0"
   assert result["region"] == "us-east-1"
   assert isinstance(result["result"], str)
   assert len(result["result"]) > 0

   print("✅ All assertions passed")
   ```

**Pass criteria:**

- All assertions pass
- Response contains expected keys
- Data types are correct

### Test 5: Multiple Invocations Test

**Purpose:** Verify agent can handle multiple requests

**Steps:**

1. Run multiple invocations

   ```python
   from src.agents.simple_qa_agent import invoke

   questions = [
       "What is AWS?",
       "Explain Amazon S3",
       "What is serverless computing?",
       "How does AWS Lambda work?",
       "What is Amazon DynamoDB?"
   ]

   for i, question in enumerate(questions, 1):
       print(f"\n--- Question {i} ---")
       result = invoke({"prompt": question})
       print(f"Answer length: {len(result['result'])} chars")
       assert "error" not in result or result["error"] is None

   print("\n✅ All invocations successful")
   ```

**Pass criteria:**

- All 5 questions receive answers
- No errors occur
- Responses are different (not cached incorrectly)

---

## Common Issues & Solutions

### Issue 1: Invalid Credentials

**Error:**

```
ERROR: Error processing request: An error occurred (UnrecognizedClientException)
```

**Solutions:**

1. Verify credentials in `.env` are correct
2. Check if temporary credentials expired
3. Generate new credentials from AWS Console

**Get new temporary credentials:**

- AWS Console → Security Credentials → Access Keys
- Or use: `aws sts get-session-token`

### Issue 2: Bedrock Access Not Enabled

**Error:**

```
ERROR: An error occurred (AccessDeniedException) when calling the InvokeModel
```

**Solution:**

1. Go to AWS Console → Amazon Bedrock
2. Click "Model access" in left sidebar
3. Click "Manage model access"
4. Enable "Amazon Nova Pro" model
5. Save changes
6. Wait 1-2 minutes for propagation

### Issue 3: Region Not Supported

**Error:**

```
ERROR: Could not connect to the endpoint URL
```

**Solution:**

Update `.env` with supported region:

```bash
AWS_REGION=us-east-1  # Recommended
# or
AWS_REGION=us-east-1
# or
AWS_REGION=us-east-1
```

### Issue 4: Insufficient IAM Permissions

**Error:**

```
ERROR: User is not authorized to perform: bedrock:InvokeModel
```

**Solution:**

Add IAM policy to user/role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-pro-v1:0"
    }
  ]
}
```

**Quick fix (dev only):**

- Attach managed policy: `AmazonBedrockFullAccess`

### Issue 5: Module Not Found

**Error:**

```
ModuleNotFoundError: No module named 'strands'
```

**Solution:**

```bash
# Ensure virtualenv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Pre-Flight Checklist

Use this checklist before running functional tests:

```
☐ Virtual environment activated (venv)
☐ Dependencies installed (strands-agents, bedrock-agentcore, boto3)
☐ .env file exists and configured
☐ AWS credentials valid (not expired)
☐ AWS region set to supported region (us-east-1)
☐ Bedrock Nova Pro model access enabled
☐ IAM permissions for bedrock:InvokeModel
☐ Network connectivity to AWS
```

---

## AWS Setup Verification

### Verify AWS Credentials

```bash
# Test AWS CLI access (if installed)
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

### Verify Bedrock Model Access

```bash
# List available models (requires AWS CLI)
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'nova-pro')].modelId"

# Expected: ["amazon.nova-pro-v1:0"] or similar
```

---

## Cost Estimation

**Amazon Nova Pro Pricing (us-east-1):**

- Input: $0.80 per 1M tokens
- Output: $3.20 per 1M tokens

**Per Test Costs:**

- Input tokens: ~50 tokens (question)
- Output tokens: ~200-300 tokens (answer)
- **Cost per test: < $0.001** (less than 1 cent)

**Cost for 100 tests: ~$0.05-0.10**

---

## Security Best Practices

### 1. Never Commit Credentials

```bash
# Verify .env is gitignored
git status  # Should NOT show .env

# If .env appears:
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: ensure .env is gitignored"
```

### 2. Use Temporary Credentials

For development, use temporary credentials that expire:

- AWS Console → Security Credentials → Create Access Key
- AWS SSO / IAM Identity Center (recommended)
- `aws sts get-session-token` (CLI)

### 3. Principle of Least Privilege

Create dedicated IAM user for development with minimal permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0"
      ]
    }
  ]
}
```

### 4. Rotate Credentials Regularly

- Rotate access keys every 90 days
- Delete unused access keys
- Use IAM Access Advisor to review permissions

---

## Test Results Documentation

### Test Execution Template

**Date:** YYYY-MM-DD
**Tester:** [Your Name]
**Environment:** Development / Staging / Production
**AWS Account:** [Account ID]
**Region:** us-east-1

| Test # | Test Name            | Status  | Duration | Notes                    |
| ------ | -------------------- | ------- | -------- | ------------------------ |
| 1      | Basic Functionality  | ✅ Pass | 3.2s     | Answer coherent          |
| 2      | Custom Question      | ✅ Pass | 2.8s     | Lambda question answered |
| 3      | Error Handling       | ✅ Pass | 0.5s     | Graceful error           |
| 4      | Response Format      | ✅ Pass | 2.9s     | All keys present         |
| 5      | Multiple Invocations | ✅ Pass | 14.5s    | 5/5 successful           |

**Overall Result:** ✅ All tests passed

**Issues Found:** None

**Recommendations:**

- Response time acceptable (2-4s average)
- Consider caching for repeated questions
- Monitor costs in production

---

## Automated Test Script

Save this as `scripts/run_functional_tests.sh`:

```bash
#!/usr/bin/env bash
set -e

echo "=========================================="
echo "=========================================="
echo

# Check virtualenv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Check .env exists
if [[ ! -f .env ]]; then
    echo "❌ .env file not found"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Test 1: Basic functionality
echo "Test 1: Basic Functionality"
python -m src.agents.simple_qa_agent || exit 1
echo "✅ Test 1 passed"
echo

# Test 2: Custom question (Python script)
echo "Test 2: Custom Question"
python -c "
from src.agents.simple_qa_agent import invoke
result = invoke({'prompt': 'What is AWS Lambda?'})
assert 'result' in result
assert len(result['result']) > 0
print('✅ Test 2 passed')
"
echo

# Test 3: Unit tests
echo "Test 3: Unit Tests"
pytest tests/test_simple_agent.py -v -q
echo "✅ Test 3 passed"
echo

echo "=========================================="
echo "✅ All functional tests passed!"
echo "=========================================="
```

Make executable:

```bash
chmod +x scripts/run_functional_tests.sh
```

Run:

```bash
source venv/bin/activate
./scripts/run_functional_tests.sh
```

---

## Success Criteria Summary

### Agent is considered functional when:

✅ **Core Functionality**

- Agent answers the hardcoded question correctly
- Responses are coherent and relevant
- Response time is reasonable (< 10 seconds)

✅ **Error Handling**

- Invalid credentials produce clear error messages
- Application doesn't crash on errors
- Errors include actionable information

✅ **Response Format**

- Returns dict with 'result', 'model', 'region' keys
- 'result' contains non-empty string
- Metadata matches configuration

✅ **Reliability**

- Can handle multiple consecutive requests
- Responses are different for different questions
- No memory leaks or performance degradation

✅ **AWS Integration**

- Successfully authenticates with AWS
- Calls Bedrock InvokeModel API
- Uses correct model (Nova Pro)
- Respects region configuration

---

## Next Steps

After verifying basic functionality:

1. **Performance Testing**
   - Measure average response time
   - Test with longer prompts
   - Monitor token usage

2. **Integration Testing**
   - Test with different models (if available)
   - Test with different regions
   - Test with rate limiting

3. **Production Readiness**
   - Add logging and monitoring
   - Implement retry logic
   - Add request throttling
   - Set up CloudWatch alarms

4. **Advanced Features**
   - Add streaming responses
   - Implement conversation history
   - Add tool integration
   - Deploy to AWS Lambda

---

## Support & Troubleshooting

### Getting Help

- **Project Documentation:** See `README.md`, `CLAUDE.md`
- **Pre-commit Issues:** See `PRE_COMMIT_SETUP.md`
- **Implementation Plan:** See `PLAN.md`
- **Changelog:** See `CHANGELOG.md`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.agents.simple_qa_agent import invoke
result = invoke({"prompt": "Test question"})
```

### Verbose Output

For more details, modify `src/agents/simple_qa_agent.py` temporarily:

```python
# Add before agent invocation
print(f"DEBUG: Invoking agent with: {user_message}")
result = agent(user_message)
print(f"DEBUG: Raw result: {result}")
```

---

## Appendix: AWS Bedrock Regions

**Nova Pro Model Availability (as of 2025):**

| Region         | Region Name | Status       |
| -------------- | ----------- | ------------ |
| us-east-1      | N. Virginia | ✅ Available |
| us-east-1      | Oregon      | ✅ Available |
| us-east-1      | Ireland     | ✅ Available |
| ap-southeast-1 | Singapore   | ✅ Available |
| ap-northeast-1 | Tokyo       | ✅ Available |

Check latest availability: [AWS Bedrock Regions Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-07
**Author:** Teamwork Mauritius
**Project:** AWS AI Agent Global Hackathon 2025
