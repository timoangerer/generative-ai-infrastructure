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

variable "s3_bucket_name" {
  description = "S3 bucket name for generated images"
  type        = string
  default     = "genai-generated-images-1"
}
