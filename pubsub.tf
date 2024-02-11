
resource "google_project_iam_audit_config" "honeytokens_iam_audit" {
  project = data.google_client_config.current.project
  service = "allServices"
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
}

resource "google_pubsub_topic" "honeytokens_pubsub" {
  name = "honeytokens-pubsub"
}


#  If the request from account failed -> does not have permissions, there are other service logs which might not be related to the usage.
#  And if the email service accounts email has "@project-id" inside it report the usage.
# https://console.cloud.google.com/logs/query;query=severity%3DERROR%20and%20protoPayload.authenticationInfo.principalEmail%3D~%22%5E.*@honeytokens-401815.*$%22;cursorTimestamp=2024-01-26T18:59:59.541977879Z;duration=P7D?referrer=search&hl=en&project=honeytokens-401815
resource "google_logging_project_sink" "honeytokens_sink" {
  name                   = "honeytokens-sink"
  destination            = "pubsub.googleapis.com/projects/${data.google_client_config.current.project}/topics/${google_pubsub_topic.honeytokens_pubsub.name}"
  filter                 = "severity=ERROR and protoPayload.authenticationInfo.principalEmail=~\"${var.user_prefix}.*@${data.google_client_config.current.project}.*$\""
  unique_writer_identity = true
}

# We must grant that writer access to the pub/sub because our sink uses a unique_writer,
resource "google_project_iam_binding" "gcs-bucket-writer" {
  project = data.google_client_config.current.project
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_project_sink.honeytokens_sink.writer_identity,
  ]
}
