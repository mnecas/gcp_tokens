from slack_sdk.webhook import WebhookClient
from abc import ABC, abstractmethod
import json
import os


class Metadata(ABC):
    @abstractmethod
    def generate_slack_text(self) -> dict:
        pass

    def slack_text_to_block(self, text) -> dict:
        return (
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            },
        )


class AwsMetadata(Metadata):
    def __init__(self, data=None) -> None:
        self.service_account = data.get("userIdentity").get("userName")
        self.agent = data.get("userAgent")
        self.caller_ip = data.get("sourceIPAddress")
        self.method = data.get("eventName")
        self.time = data.get("eventTime")
        self.service_account_labels = self.get_aws_service_accouts_details(
            self.service_account
        )

    def get_aws_service_accouts_details(self, service_account):
        import boto3

        resp = boto3.client("iam").list_user_tags(UserName=service_account)
        return resp.get("Tags")

    def generate_slack_text(self) -> dict:
        labels_string = ""
        for label in self.service_account_labels:
            key = label["Key"]
            val = label["Value"]
            labels_string += f"- {key}: {val}\n"
        SLACK_REPORT = os.environ.get("SLACK_REPORT", "")
        if SLACK_REPORT:
            return SLACK_REPORT.format(
                service_account=self.service_account,
                labels_string=labels_string,
                caller_ip=self.caller_ip,
                method=self.method,
            )

        return f"""
            AWS token "*{self.service_account}*" triggered
            \n*Labels*:\n{labels_string}
            \n*Metadata*:\n- IP: {self.caller_ip} \n- Method: {self.method}
        """


class GcpMetadata(Metadata):
    def __init__(self, data=None) -> None:
        payload_data = data.get("protoPayload")
        metadata = payload_data.get("requestMetadata")

        self.time = data.get("receiveTimestamp")
        self.service_account_email = payload_data.get("authenticationInfo", {}).get(
            "principalEmail"
        )
        self.service_account = self.service_account_email.split("@")[0]
        self.service_account_labels = self.get_gcp_service_accouts_details(
            self.service_account_email
        )
        self.method = payload_data.get("methodName")
        self.caller_ip = metadata.get("callerIp")
        self.agent = metadata.get("callerSuppliedUserAgent")

    def get_gcp_service_accouts_details(self, service_account_email: str) -> dict:
        import google.auth
        from google.auth.transport import requests
        from googleapiclient.discovery import build

        credentials, project_id = google.auth.default()
        credentials.refresh(requests.Request())
        iam = build("iam", "v1", credentials=credentials)
        get_account_response = (
            iam.projects()
            .serviceAccounts()
            .get(
                name="projects/{}/serviceAccounts/{}".format(
                    project_id, service_account_email
                )
            )
            .execute()
        )
        return json.loads(get_account_response["description"])

    def generate_slack_text(self) -> dict:
        labels_string = ""
        for key, val in self.service_account_labels.items():
            labels_string += f"- {key}: {val}\n"
        SLACK_REPORT = os.environ.get("SLACK_REPORT", "")

        if SLACK_REPORT:
            return SLACK_REPORT.format(
                service_account=self.service_account,
                labels_string=labels_string,
                caller_ip=self.caller_ip,
                method=self.method,
            )

        return f"""
            GCP token "*{self.service_account}*" triggered
            \n*Labels*:\n{labels_string}
            \n*Metadata*:\n- IP: {self.caller_ip} \n- Method: {self.method}
        """


class SlackRequest:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url
        self.client = WebhookClient(self.webhook_url)

    def send(self, metadata: Metadata):
        print(f"Sedning to: {self.webhook_url}")
        text = metadata.generate_slack_text()
        print(f"Sending blocks: {text}")
        response = self.client.send(
            text=f'Token "*{metadata.service_account}*" triggered',
            blocks=metadata.slack_text_to_block(text),
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {response.body}")
        return response
