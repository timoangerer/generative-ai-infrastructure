variable "namespace" {
  description = "Name of the kubernetes namespace"
  type        = string
}

variable "pulsar_service_url" {
  description = "The HTTP service URL for Pulsar"
  type        = string
}

variable "pulsar_cluster" {
  description = "Name of the pulsar cluster"
  type        = string
}

variable "pulsar_namespace" {
  description = "Name of the pulsar namespace"
  type        = string
}

variable "pulsar_tenant" {
  description = "Name of the pulsar tenant"
  type        = string
}

variable "pulsar_topics" {
  description = "List of topic names"
  type        = list(string)
}
