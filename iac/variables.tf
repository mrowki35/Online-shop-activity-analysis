variable "resource_group_name" {
  description = "Nazwa grupy zasobów"
  default     = "rg-clickstream-student-dev"
}

variable "location" {
  description = "Lokalizacja zasobów"
  default     = "Switzerland North"
}

variable "alert_email" {
  description = "Adres email do powiadomień o budżecie"
  type        = string
  default     = "twoj@email.com" # Tutaj wpisz swój domyślny
}