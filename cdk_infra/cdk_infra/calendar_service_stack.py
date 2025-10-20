"""CDK Stack for Google Calendar Lambda service with Service Account."""

from pathlib import Path

from aws_cdk import Duration, Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class CalendarServiceStack(Stack):
    """Lambda function for Google Calendar API with Service Account."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load service account credentials
        project_root = Path(__file__).parent.parent.parent
        service_account_path = project_root / "service-account-key.json"

        if not service_account_path.exists():
            raise FileNotFoundError(
                "service-account-key.json not found! "
                "Please create a service account and download the JSON key."
            )

        service_account_json = service_account_path.read_text()
        calendar_id = self.node.try_get_context("calendar_id") or "primary"

        # Lambda function
        self.calendar_function = lambda_.Function(
            self,
            "CalendarFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset(str(project_root / "lambda" / "calendar_service")),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "GOOGLE_SERVICE_ACCOUNT_JSON": service_account_json,
                "GOOGLE_CALENDAR_ID": calendar_id,
            },
        )

        # Store in SSM Parameter Store
        ssm.StringParameter(
            self,
            "CalendarIdParam",
            parameter_name="/restaurant-booking/calendar-id",
            string_value=calendar_id,
            description="Google Calendar ID for restaurant bookings",
        )

        # Output Lambda ARN
        self.lambda_arn = self.calendar_function.function_arn
