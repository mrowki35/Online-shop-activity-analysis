terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rq-clickstream-kappa-dev"
  location = "Switzerland North"
}

resource "random_string" "random" {
  length  = 8
  special = false
  upper   = false
}

resource "azurerm_storage_account" "storage" {
  name                     = "rqclickstream${random_string.random.result}" 
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
  name                = "eh-clickstream-${random_string.random.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Basic" 
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
  name                = "db-clickstream-${random_string.random.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"
}