variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "otel_exporter_otlp_endpoint" {
  description = "The OpenTelemetry Collector OTLP endpoint"
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
