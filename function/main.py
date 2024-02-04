from cloudevents.http import CloudEvent
import functions_framework
import base64
import os
import json
from utils import *


WEBHOOK_URL = os.environ["WEBHOOK_URL"]


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def honeytokens(cloud_event: CloudEvent) -> None:
    raw_data = cloud_event.get_data()["message"]["data"]
    decoded_data = base64.b64decode(raw_data)
    data = json.loads(decoded_data)

    metadata = GcpMetadata(data)
    slack = SlackRequest(WEBHOOK_URL)
    slack.send(metadata)
