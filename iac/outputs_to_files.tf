resource "local_file" "generator_env" {
  content = <<EOT
EVENT_HUB_CONNECTION_STR=${azurerm_eventhub_namespace.eh_ns.default_primary_connection_string}
EVENT_HUB_NAME=${azurerm_eventhub.eh.name}
EOT

  filename = "${path.module}/../data_generator/.env"
}