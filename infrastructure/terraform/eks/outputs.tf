output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "region" {
  description = "AWS region"
  value       = var.region
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}

output "models_efs_id" {
  description = "ID of the models EFS"
  value       = aws_efs_file_system.models_efs.id
}

output "s3_bucket_name" {
  description = "S3 bucket name for generated images"
  value       = aws_s3_bucket.generated_images_bucket.bucket
}
