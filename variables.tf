
variable "user_prefix" {
  type    = string
  default = "test"
}

variable "users" {
  type    = map(map(string))
  default = {}
}

# Slack configuration
variable "webhook_url" {
  type    = string
  default = "https://hooks.slack.com/TXXXXX/BXXXXX/XXXXXXXXXX"
}


