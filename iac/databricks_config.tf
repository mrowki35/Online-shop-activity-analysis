data "databricks_current_user" "me" {}
data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}
data "databricks_node_type" "smallest" {
  local_disk = true
}

resource "databricks_cluster" "single_node" {
  cluster_name            = "Clickstream Cluster"
  spark_version           = data.databricks_spark_version.latest_lts.id
  node_type_id            = data.databricks_node_type.smallest.id
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
  path     = "/Users/${data.databricks_current_user.me.user_name}/etl_pipeline"
  language = "PYTHON"
  source   = "../notebooks/etl_pipeline.py" # Upewnij się, że masz ten plik!
}