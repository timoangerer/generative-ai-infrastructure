variable "config_context" {
  description = "Kubectl cluster context"
  type        = string
}

variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}
