variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "otel_exporter_otlp_endpoint" {
  description = "The OpenTelemetry Collector OTLP endpoint"
  type        = string
  default     = "http://signoz-otel-collector:4317"
}

variable "pulsar_service_url" {
  description = "URL for the Pulsar service"
  type        = string
}

variable "pulsar_broker_service_url" {
  description = "Broker service URL for Pulsar"
  type        = string
}

variable "pulsar_cluster" {
  description = "Pulsar cluster name"
  type        = string
}

variable "pulsar_tenant" {
  description = "Pulsar tenant"
  type        = string
}

variable "pulsar_namespace" {
  description = "Pulsar namespace"
  type        = string
}

variable "sd_server_url" {
  description = "URL for the SD server"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "service_account_name" {
  description = "Name of the service account to perform actions such as storing generated images"
  type        = string
}
