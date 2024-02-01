provider "aws" {
  region = var.region
}

# Filter out local zones, which are not currently supported 
# with managed node groups
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

locals {
  cluster_name = "${var.name}-eks-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "${var.name}-vpc"

  cidr = "10.0.0.0/16"
  azs  = slice(data.aws_availability_zones.available.names, 0, 3)

  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = 1
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = 1
  }
}

resource "aws_security_group" "efs" {
  name        = "${var.name}-efs"
  description = "Allow traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "nfs"
    from_port   = 2049
    to_port     = 2049
    protocol    = "TCP"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }
}

resource "aws_iam_policy" "node_efs_policy" {
  name        = "eks_node_efs-${var.name}"
  path        = "/"
  description = "Policy for EKS nodes to use EFS"

  policy = jsonencode({
    "Statement" : [
      {
        "Action" : [
          "elasticfilesystem:DescribeMountTargets",
          "elasticfilesystem:DescribeFileSystems",
          "elasticfilesystem:DescribeAccessPoints",
          "elasticfilesystem:CreateAccessPoint",
          "elasticfilesystem:DeleteAccessPoint",
          "ec2:DescribeAvailabilityZones"
        ],
        "Effect" : "Allow",
        "Resource" : "*",
        "Sid" : ""
      }
    ],
    "Version" : "2012-10-17"
    }
  )
}

resource "aws_efs_file_system" "models_efs" {
  creation_token = "eks-efs"
  tags = {
    "name" : "models-efs"
  }
}

locals {
  private_subnets_map = { for idx, subnet in module.vpc.private_subnets : "subnet-${idx}" => subnet }
}

resource "aws_efs_mount_target" "mount" {
  for_each        = local.private_subnets_map
  file_system_id  = aws_efs_file_system.models_efs.id
  subnet_id       = each.value
  security_groups = [aws_security_group.efs.id]
}


module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = local.cluster_name
  cluster_version = "1.28"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_group_defaults = {
    ami_type               = "AL2_x86_64"
    vpc_security_group_ids = [aws_security_group.efs.id]
  }

  eks_managed_node_groups = {
    general_node_group = {
      name = "general_node_group"

      instance_types = ["t3.xlarge"]

      min_size     = 1
      max_size     = 4
      desired_size = 3

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 30
            volume_type           = "gp3"
            iops                  = 1000
            throughput            = 125
            encrypted             = false
            delete_on_termination = true
          }
        }
      }
    },
    gpu_node_group = {
      name     = "gpu_node_group"
      ami_type = "AL2_x86_64_GPU"

      instance_types = ["g4dn.xlarge"]

      min_size     = 0
      max_size     = 1
      desired_size = 1

      labels = {
        workload-type = "gpu"
      }

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 40
            volume_type           = "gp3"
            iops                  = 1000
            throughput            = 125
            encrypted             = false
            delete_on_termination = true
          }
        }
      }
    }
  }
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name = module.eks.cluster_name
  addon_name   = "vpc-cni"
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = module.eks.cluster_name
  addon_name   = "kube-proxy"
}

resource "aws_eks_addon" "codedns" {
  cluster_name = module.eks.cluster_name
  addon_name   = "coredns"
}

resource "aws_eks_addon" "efs-csi" {
  cluster_name = module.eks.cluster_name
  addon_name   = "aws-efs-csi-driver"
}

# https://aws.amazon.com/blogs/containers/amazon-ebs-csi-driver-is-now-generally-available-in-amazon-eks-add-ons/ 
data "aws_iam_policy" "ebs_csi_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

module "irsa-ebs-csi" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version = "4.7.0"

  create_role                   = true
  role_name                     = "AmazonEKSTFEBSCSIRole-${module.eks.cluster_name}"
  provider_url                  = module.eks.oidc_provider
  role_policy_arns              = [data.aws_iam_policy.ebs_csi_policy.arn]
  oidc_fully_qualified_subjects = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
}

resource "aws_eks_addon" "ebs-csi" {
  cluster_name             = module.eks.cluster_name
  addon_name               = "aws-ebs-csi-driver"
  addon_version            = "v1.20.0-eksbuild.1"
  service_account_role_arn = module.irsa-ebs-csi.iam_role_arn
  tags = {
    "eks_addon" = "ebs-csi"
    "terraform" = "true"
  }
}

resource "aws_s3_bucket" "generated_images_bucket" {
  bucket        = var.s3_bucket_name
  force_destroy = true
  tags          = {}
}

resource "aws_iam_policy" "s3_access" {
  name        = "${var.name}-s3-access"
  description = "Policy to access specific S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.generated_images_bucket.arn}",
          "${aws_s3_bucket.generated_images_bucket.arn}/*"
        ]
      }
    ]
  })
}

data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_name
}

output "eks_cluster_oidc_issuer_url" {
  value = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
}

data "aws_caller_identity" "current" {}

locals {
  oidc_url       = data.aws_eks_cluster.cluster.identity[0].oidc[0].issuer
  oidc_host_path = replace(local.oidc_url, "https://", "")
  oidc_arn       = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${local.oidc_host_path}"
}

output "eks_cluster_oidc_provider_arn" {
  value = local.oidc_arn
}

module "iam_eks_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  role_name = "image-saver-s3"

  role_policy_arns = {
    policy = aws_iam_policy.s3_access.arn
  }

  oidc_providers = {
    one = {
      provider_arn               = local.oidc_arn
      namespace_service_accounts = ["genai:s3-interaction"]
    }
  }
}

output "iam_s3_interaction_role_arn" {
  value = module.iam_eks_role.iam_role_arn
}
