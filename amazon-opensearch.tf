terraform {
  required_version = "~> 1.5.7"
}

variable "domain_name" {
  type    = string
  default = "opensearch-remote-models"
}

variable "master_user_arn" {
  type = string
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_opensearch_domain" "opensearch" {

  domain_name    = var.domain_name
  engine_version = "OpenSearch_2.9"

  cluster_config {
    dedicated_master_count   = 0
    dedicated_master_type    = null
    dedicated_master_enabled = false
    instance_type            = "r6g.large.search"
    instance_count           = 3
    zone_awareness_enabled   = false
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = false
    master_user_options {
      master_user_arn     = var.master_user_arn
    }
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  encrypt_at_rest {
    enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 300
    volume_type = "gp3"
    throughput  = 250
  }

  node_to_node_encryption {
    enabled = true
  }

  access_policies = <<CONFIG
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "es:*",
            "Principal": "*",
            "Effect": "Allow",
            "Resource": "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.domain_name}/*"
        }
    ]
}
CONFIG
}
