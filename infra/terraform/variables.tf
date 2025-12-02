variable "project_name" {
  description = "Project name prefix for AWS resources"
  type        = string
  default     = "dbmigration"
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "tf_state_bucket" {
  description = "S3 bucket name for Terraform remote state"
  type        = string
}

variable "tf_state_key" {
  description = "S3 key (path) for Terraform state file"
  type        = string
  default     = "dbmigration/terraform.tfstate"
}

variable "tf_state_lock_table" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Map of public subnet configs"
  type = map(object({
    cidr = string
    az   = string
  }))

  default = {
    "a" = {
      cidr = "10.0.1.0/24"
      az   = "us-east-1a"
    }
    "b" = {
      cidr = "10.0.2.0/24"
      az   = "us-east-1b"
    }
  }
}

variable "private_subnets" {
  description = "Map of private subnet configs"
  type = map(object({
    cidr = string
    az   = string
  }))

  default = {
    "a" = {
      cidr = "10.0.11.0/24"
      az   = "us-east-1a"
    }
    "b" = {
      cidr = "10.0.12.0/24"
      az   = "us-east-1b"
    }
  }
}

variable "oracle_engine_version" {
  description = "Oracle RDS engine version"
  type        = string
  default     = "19.0.0.0.ru-2023-10.rur-2023-10.r1"
}

variable "oracle_instance_class" {
  description = "Instance class for Oracle RDS"
  type        = string
  default     = "db.t3.medium"
}

variable "oracle_master_username" {
  description = "Master username for Oracle RDS"
  type        = string
}

variable "oracle_master_password" {
  description = "Master password for Oracle RDS"
  type        = string
  sensitive   = true
}

variable "postgres_engine_version" {
  description = "PostgreSQL RDS engine version"
  type        = string
  default     = "16.3"
}

variable "postgres_instance_class" {
  description = "Instance class for PostgreSQL RDS"
  type        = string
  default     = "db.t3.medium"
}

variable "postgres_master_username" {
  description = "Master username for PostgreSQL RDS"
  type        = string
}

variable "postgres_master_password" {
  description = "Master password for PostgreSQL RDS"
  type        = string
  sensitive   = true
}


