# MySQL 8.4 in the private data subnets. Encrypted, automated backups; Multi-AZ and deletion
# protection are switched on per environment.

resource "aws_db_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}

resource "aws_db_parameter_group" "this" {
  name   = var.name
  family = "mysql8.4"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }

  parameter {
    name  = "require_secure_transport"
    value = "1"
  }
}

resource "aws_db_instance" "this" {
  identifier                   = var.name
  engine                       = "mysql"
  engine_version               = "8.4"
  instance_class               = var.instance_class
  allocated_storage            = var.storage_gb
  max_allocated_storage        = var.storage_gb * 5
  storage_type                 = "gp3"
  storage_encrypted            = true
  db_name                      = var.database
  username                     = var.username
  password                     = var.password
  db_subnet_group_name         = aws_db_subnet_group.this.name
  parameter_group_name         = aws_db_parameter_group.this.name
  vpc_security_group_ids       = [var.security_group_id]
  multi_az                     = var.multi_az
  publicly_accessible          = false
  backup_retention_period      = var.backup_days
  deletion_protection          = var.deletion_protection
  skip_final_snapshot          = !var.deletion_protection
  final_snapshot_identifier    = var.deletion_protection ? "${var.name}-final" : null
  auto_minor_version_upgrade   = true
  performance_insights_enabled = true
  copy_tags_to_snapshot        = true
}
