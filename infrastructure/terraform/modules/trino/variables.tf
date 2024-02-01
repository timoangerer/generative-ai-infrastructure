variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "pulsar_cluster" {
  description = "Name of the pulsar cluster"
  type        = string
}
variable "pulsar_service_url" {
  description = "The HTTP service URL for Pulsar"
  type        = string
}

variable "pulsar_broker_service_url" {
  description = "The broker service URL for Pulsar"
  type        = string
}
