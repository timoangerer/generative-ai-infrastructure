variable "namespace" {
  description = "The Kubernetes namespace to deploy into"
  type        = string
}

variable "model_links" {
  description = "List of model download links and filenames"
  type = list(object({
    url       = string
    rename_to = string
  }))
}
