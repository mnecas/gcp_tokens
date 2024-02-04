
output "honeytokens_access_keys" {
  value = [
    for user_name, user in google_service_account.honeytokens_users_gcp :
    {
      name        = user_name
      private_key = base64decode(google_service_account_key.honeytokens_users_keys_gcp[user_name].private_key)
    }
  ]
  sensitive = true
}

resource "local_file" "output_key_files" {
  for_each       = var.users
  content_base64 = google_service_account_key.honeytokens_users_keys_gcp[each.key].private_key
  filename       = "output/${each.key}.json"
}
