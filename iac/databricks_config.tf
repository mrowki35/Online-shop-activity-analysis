provider "databricks" {
  host                        = azurerm_databricks_workspace.db.workspace_url
  azure_workspace_resource_id = azurerm_databricks_workspace.db.id
}
locals {
  spark_v = "13.3.x-scala2.12"
  node_v  = "Standard_DS3_v2"
}

resource "databricks_cluster" "single_node" {
  cluster_name            = "Clickstream Cluster"
  spark_version           = local.spark_v
  node_type_id            = local.node_v
  autotermination_minutes = 20

  spark_conf = {
    "spark.databricks.cluster.profile" : "singleNode"
    "spark.master" : "local[*]"
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }

  spark_env_vars = {
    "EVENT_HUB_CONN_STR"   = azurerm_eventhub_namespace.eh_ns.default_primary_connection_string
    "EVENT_HUB_NAME"       = azurerm_eventhub.eh.name
    "STORAGE_ACCOUNT_NAME" = azurerm_storage_account.storage.name
    "STORAGE_ACCOUNT_KEY"  = azurerm_storage_account.storage.primary_access_key
  }
  
  depends_on = [azurerm_databricks_workspace.db]
}

resource "databricks_notebook" "etl" {
  path     = "/Shared/etl_pipeline"
  language = "PYTHON"
  source   = "../data_generator/etl_pipeline.py" 
  
  depends_on = [azurerm_databricks_workspace.db]
}

resource "databricks_library" "eventhubs" {
  cluster_id = databricks_cluster.single_node.id
  maven {
    coordinates = "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.22"
  }
}