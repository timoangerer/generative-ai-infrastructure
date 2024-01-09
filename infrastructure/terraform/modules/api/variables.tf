variable "config_context" {
  description = "The Kubernetes context to deploy into"
  type        = string
}

variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "otel_exporter_otlp_endpoint" {
  description = "The OpenTelemetry Collector OTLP endpoint"
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

variable "pulsar_cluster" {
  description = "The Pulsar cluster name"
  type        = string
}

variable "pulsar_tenant" {
  description = "The Pulsar tenant name"
  type        = string
}

variable "pulsar_namespace" {
  description = "The Pulsar namespace"
  type        = string
}

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
}

variable "trino_schema" {
  description = "The schema for Trino"
  type        = string
}
