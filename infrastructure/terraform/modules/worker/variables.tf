variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "otel_exporter_otlp_endpoint" {
  description = "The OpenTelemetry Collector OTLP endpoint"
  type        = string
  default     = "http://signoz-otel-collector:4317"
}
