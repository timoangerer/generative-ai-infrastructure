variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "pulsar_cluster" {
  description = "Name of the pulsar cluster"
  type        = string
  default     = "pulsar"
}

variable "pulsar_service_port" {
  description = "The HTTP service URL port for Pulsar"
  type        = string
}

variable "pulsar_cluster_config_file" {
  description = "Config values of the pulsar cluster used for setup"
  type        = string
}
