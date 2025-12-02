########################################
# Secrets Manager skeleton
########################################

resource "aws_secretsmanager_secret" "oracle" {
  name        = "dbmigration/oracle"
  description = "Oracle connection details for DBMigration"
}

resource "aws_secretsmanager_secret" "postgres" {
  name        = "dbmigration/postgres"
  description = "PostgreSQL connection details for DBMigration"
}

resource "aws_secretsmanager_secret" "openai" {
  name        = "dbmigration/openai"
  description = "OpenAI credentials for DBMigration"
}

# Note: secret values should be created/updated using aws_secretsmanager_secret_version
# or via the AWS console/CLI, not committed to source control.


