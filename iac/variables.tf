variable "resource_group_name" {
  description = "Nazwa grupy zasobów"
  default     = "rg-clickstream-student"
}

variable "location" {
  description = "Lokalizacja zasobów"
  default     = "Switzerland North"
}

variable "eh_conn_string" {
  description = "Connection string do Event Hub (dla Databricks)"
  type        = string
  sensitive   = true # Terraform ukryje to w logach
}