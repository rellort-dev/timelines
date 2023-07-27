
variable "TIMELINES_DEVELOPMENT_MODE" {
  type    = bool
  default = false
}

variable "ALLOWED_HOST" {
  type      = string
  sensitive = true
}

variable "MEILISEARCH_URL" {
  type      = string
  sensitive = true
}

variable "MEILISEARCH_KEY" {
  type      = string
  sensitive = true
}
