# AgentCore Deployment Architecture: CDK Custom Resource Pattern

## Design Decision

**Problem**: Amazon Bedrock AgentCore is in preview and lacks native CDK L2/L1 constructs.

**Wrong Approach**: Using a separate boto3 Python script to deploy AgentCore after CDK deployment.

**Correct Approach**: Use CDK `AwsCustomResource` to deploy AgentCore as part of the CloudFormation stack.

## Why CDK Custom Resource Instead of Boto3 Script?

### Infrastructure as Code Principles

| Aspect                | Boto3 Script                                 | CDK Custom Resource                         |
| --------------------- | -------------------------------------------- | ------------------------------------------- |
| **Version Control**   | Separate script, separate state              | Full IaC in CDK stack                       |
| **Atomic Deployment** | Two-step process, can fail between steps     | Single `cdk deploy`, atomic                 |
| **Cleanup**           | Manual deletion required                     | Automatic on `cdk destroy`                  |
| **Dependencies**      | Manual ordering, prone to errors             | CloudFormation handles deps                 |
| **Outputs**           | Need to save ARN to file, then update Lambda | Direct reference via `get_response_field()` |
| **Rollback**          | No automatic rollback                        | CloudFormation rollback on failure          |

### Benefits of CDK Custom Resource

1. **True Infrastructure as Code**
   - Everything defined in `agent_stack.py`
   - No post-deployment scripts needed
   - Version-controlled infrastructure

2. **Automatic Lifecycle Management**
   - `on_create`: Creates AgentCore runtime during stack creation
   - `on_delete`: Deletes AgentCore runtime during stack deletion
   - No manual cleanup required

3. **Atomic Deployment**
   - All resources succeed together or all roll back
   - No partial deployments
   - Consistent state

4. **Direct Integration**
   - Lambda gets `AGENTCORE_RUNTIME_ARN` directly from stack
   - No environment variable updates needed
   - No temporary files to track state

5. **CloudFormation Dependency Management**
   - Custom resource depends on IAM role
   - Lambda depends on custom resource
   - Proper ordering guaranteed

## Implementation

### Stack Resource Order

```
ECR Repository (existing)
    ↓
IAM Role (AgentCoreRuntimeRole)
    ↓
AwsCustomResource (creates AgentCore runtime)
    ↓
Lambda Function (receives runtime ARN)
    ↓
Function URL
```

### Key Code Patterns

```python
# 1. Create IAM role
agentcore_role = iam.Role(
    self,
    "AgentCoreRuntimeRole",
    assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
    ...
)

# 2. Create AgentCore via Custom Resource
agentcore_runtime = cr.AwsCustomResource(
    self,
    "AgentCoreRuntime",
    on_create=cr.AwsSdkCall(
        service="bedrock-agentcore-control",
        action="createAgentRuntime",
        parameters={...},
        physical_resource_id=cr.PhysicalResourceId.from_response("agentRuntimeArn"),
    ),
    on_delete=cr.AwsSdkCall(
        service="bedrock-agentcore-control",
        action="deleteAgentRuntime",
        parameters={"agentRuntimeArn": cr.PhysicalResourceIdReference()},
    ),
    policy=cr.AwsCustomResourcePolicy.from_statements([...]),
)

# 3. Extract ARN and pass to Lambda
runtime_arn = agentcore_runtime.get_response_field("agentRuntimeArn")

invoker_fn = lambda_.Function(
    self,
    "AgentInvoker",
    environment={"AGENTCORE_RUNTIME_ARN": runtime_arn},
    ...
)
```

## How It Works Under the Hood

1. **CDK Synthesis**: Generates CloudFormation with AWS::CloudFormation::CustomResource
2. **Stack Deployment**: CloudFormation invokes a Lambda (created by CDK) to execute the custom resource
3. **Custom Resource Lambda**:
   - Calls `boto3.client('bedrock-agentcore-control').create_agent_runtime(...)`
   - Returns `agentRuntimeArn` to CloudFormation
   - CloudFormation stores ARN as physical resource ID
4. **Lambda Environment**: Gets `AGENTCORE_RUNTIME_ARN` from custom resource output
5. **Stack Deletion**: CloudFormation calls custom resource Lambda to delete AgentCore runtime

## Required IAM Permissions for Deployment

**IMPORTANT**: Your AWS user/role deploying the CDK stack needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:CreateAgentRuntime",
        "bedrock-agentcore:DeleteAgentRuntime",
        "bedrock-agentcore:GetAgentRuntime",
        "bedrock-agentcore:ListAgentRuntimes"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::*:role/AgentCoreRuntimeRole"
    }
  ]
}
```

Or use the AWS managed policy: `BedrockAgentCoreFullAccess`

**Why?** The Custom Resource Lambda is created by CDK and inherits permissions from the CloudFormation service role, but the deployer also needs permissions to create the Lambda and grant it the necessary policies.

## Deployment Workflow

### Old (Broken) Workflow

```bash
1. cdk deploy              # Deploy IAM role + Lambda
2. python deploy_script.py # Manually create AgentCore
3. aws lambda update-...   # Manually update Lambda env var
4. Manual cleanup needed   # No automatic deletion
```

### New (Correct) Workflow

```bash
1. docker push <ecr-uri>   # Push agent image
2. cdk deploy              # Everything deployed atomically
   - IAM role created
   - AgentCore runtime created via Custom Resource
   - Lambda created with runtime ARN
   - Outputs printed
3. cdk destroy             # Everything cleaned up automatically
```

### Common Deployment Errors

**Error: AccessDenied on CreateAgentRuntime**

- **Cause**: Your AWS credentials don't have `bedrock-agentcore:CreateAgentRuntime` permission
- **Fix**: Attach `BedrockAgentCoreFullAccess` managed policy or add custom permissions above

**Error: Role cannot be assumed**

- **Cause**: IAM eventual consistency - role not propagated yet
- **Fix**: Added explicit dependency `agentcore_runtime.node.add_dependency(agentcore_role)`

## When to Use This Pattern

Use CDK Custom Resource when:

- ✅ AWS service lacks native CDK constructs (preview services)
- ✅ You need IaC for boto3-only APIs
- ✅ You want atomic deployment and cleanup
- ✅ You need CloudFormation-managed lifecycle

Don't use separate boto3 scripts when:

- ❌ It breaks IaC principles
- ❌ Manual state management is required
- ❌ Cleanup is not automatic
- ❌ Deployment order is manual

## References

- [AWS CDK Custom Resources](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.custom_resources-readme.html)
- [Amazon Bedrock AgentCore Control API](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [CloudFormation Custom Resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html)

## Related Files

- `cdk_infra/cdk_infra/agent_stack.py` - Stack implementation with Custom Resource
- `scripts/deploy-agentcore.sh` - Deployment automation (no longer creates AgentCore manually)
