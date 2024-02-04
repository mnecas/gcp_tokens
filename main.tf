terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.13.0"
    }
  }
}

data "google_client_config" "current" {}
