data "archive_file" "source" {
  type        = "zip"
  source_dir  = "${path.module}/function/"
  output_path = "${path.module}/builds/function-source.zip"
}

resource "google_storage_bucket" "default" {
  name                        = "gcf-honeytoken-source"
  location                    = "US"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "default" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.default.name
  source = data.archive_file.source.output_path # Add path to the zipped function source code
}

resource "google_cloudfunctions2_function" "honeytoken_function" {
  name     = "honeytoken-function"
  location = data.google_client_config.current.region

  build_config {
    runtime     = "python38"
    entry_point = "honeytokens" # Set the entry point
    environment_variables = {
      BUILD_CONFIG_TEST = "build_test"
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.default.name
      }
    }
  }

  service_config {
    environment_variables = {
      WEBHOOK_URL = var.webhook_url
    }
  }
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.honeytokens_pubsub.id
  }
}
