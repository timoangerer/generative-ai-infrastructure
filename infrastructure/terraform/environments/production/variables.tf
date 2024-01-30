# Kubernetes
variable "config_context" {
  description = "The Kubernetes context to deploy into"
  type        = string
}

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

# WORKER

variable "sd_server_url" {
  description = "URL for the SD server"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "aws_access_key_id" {
  description = "AWS access key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret access key"
  type        = string
  sensitive   = true
}

# MODELS
variable "model_links" {
  description = "List of model download links and filenames"
  type = list(object({
    url       = string
    rename_to = string
  }))
  default = [
    {
      url       = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true"
      rename_to = "v1-5-pruned-emaonly.safetensors"
    }
  ]
}
