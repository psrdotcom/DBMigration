########################################
# CloudWatch Logs & basic alarms
########################################

resource "aws_cloudwatch_log_group" "ecs_streamlit" {
  name              = "/ecs/dbmigration-streamlit"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "ecs_cli" {
  name              = "/ecs/dbmigration-cli"
  retention_in_days = 14
}

# Example CPU alarm for ECS cluster (placeholder - requires ECS service resources)
# resource "aws_cloudwatch_metric_alarm" "ecs_high_cpu" {
#   alarm_name          = "${var.project_name}-ecs-high-cpu"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = 2
#   metric_name         = "CPUUtilization"
#   namespace           = "AWS/ECS"
#   period              = 60
#   statistic           = "Average"
#   threshold           = 80
# }


