# Kubernetes

variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "kubernetes_cluster_ip" {
  description = "IP of the Kubernetes cluster"
  type        = string
}

# PULSAR

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

variable "pulsar_service_url" {
  description = "The HTTP service URL for Pulsar"
  type        = string
}

variable "pulsar_broker_service_url" {
  description = "The broker service URL for Pulsar"
  type        = string
  default     = "pulsar://localhost:6650/"
}

# TRINO

variable "trino_host" {
  description = "The host for Trino"
  type        = string
}

variable "trino_port" {
  description = "The port for Trino"
  type        = string
}

variable "trino_user" {
  description = "The user for Trino"
  type        = string
}

variable "trino_catalog" {
  description = "The catalog for Trino"
  type        = string
  default     = "pulsar"
}

variable "trino_schema" {
  description = "The schema for Trino"
  type        = string
  default     = "public/default"
}

# OPEN TELEMETRY

variable "otel_exporter_otlp_endpoint" {
  description = "The OpenTelemetry Collector OTLP endpoint"
  type        = string
}
