resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "random_string" "random" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_storage_account" "storage" {
  name                     = "stclickstream${random_string.random.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

resource "azurerm_storage_data_lake_gen2_filesystem" "dl_fs" {
  name               = "data"
  storage_account_id = azurerm_storage_account.storage.id
}

resource "azurerm_eventhub_namespace" "eh_ns" {
  name                = "eh-ns-${random_string.random.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1
}

resource "azurerm_eventhub" "eh" {
  name                = "input-stream"
  namespace_name      = azurerm_eventhub_namespace.eh_ns.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_databricks_workspace" "db" {
  name                = "db-workspace-${random_string.random.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"
}

locals {
  current_month_start = "${formatdate("YYYY-MM", timestamp())}-01T00:00:00Z"
}

resource "azurerm_consumption_budget_resource_group" "budget" {
  name              = "Budget-${azurerm_resource_group.rg.name}"
  resource_group_id = azurerm_resource_group.rg.id
  amount            = 50 
  time_grain        = "Monthly"

  time_period {
    start_date = local.current_month_start
  }

  # Alert 10% 
  notification {
    enabled        = true
    threshold      = 10.0
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = [var.alert_email] 
  }

  # Alert 50% 
  notification {
    enabled        = true
    threshold      = 50.0
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = [var.alert_email]
  }

  # Alert 75% 
  notification {
    enabled        = true
    threshold      = 75.0
    operator       = "GreaterThan"
    threshold_type = "Actual"
    contact_emails = [var.alert_email]
  }

  lifecycle {
    ignore_changes = [time_period[0].start_date]
  }
}