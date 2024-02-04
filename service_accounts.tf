

resource "google_service_account" "honeytokens_users_gcp" {
  for_each   = var.users
  account_id = "${var.user_prefix}-${each.key}"
  # Limited size of describtion to 256 char
  description = jsonencode(each.value)
}

resource "google_service_account_key" "honeytokens_users_keys_gcp" {
  for_each           = var.users
  service_account_id = google_service_account.honeytokens_users_gcp[each.key].name
  depends_on         = [google_service_account.honeytokens_users_gcp]
}
