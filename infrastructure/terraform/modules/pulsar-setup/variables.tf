variable "namespace" {
  description = "Name of the kubernetes namespace"
  type        = string
}

variable "pulsar_cluster" {
  description = "Name of the pulsar cluster"
  type        = string
  default     = "pulsar-mini"
}

variable "pulsar_namespace" {
  description = "Name of the pulsar namespace"
  type        = string
  default     = "genai"
}

variable "pulsar_tenant" {
  description = "Name of the pulsar tenant"
  type        = string
  default     = "rocky"
}

variable "pulsar_topics" {
  description = "List of topic names"
  type        = list(string)
  default     = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
}
