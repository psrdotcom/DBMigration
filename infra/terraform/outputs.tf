output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.dbmigration.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = [for s in aws_subnet.public : s.id]
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = [for s in aws_subnet.private : s.id]
}

output "oracle_rds_endpoint" {
  description = "Oracle RDS endpoint"
  value       = aws_db_instance.oracle.address
}

output "postgres_rds_endpoint" {
  description = "PostgreSQL RDS endpoint"
  value       = aws_db_instance.postgres.address
}

output "alb_dns_name" {
  description = "ALB DNS name for Streamlit UI"
  value       = aws_lb.app.dns_name
}


