variable "name" {
  description = "Name of project"
  type        = string
  default     = "genai"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}
