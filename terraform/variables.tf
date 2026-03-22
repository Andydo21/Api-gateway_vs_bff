# variables.tf
variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for tagging"
  default     = "api-gateway-bff"
}

# outputs.tf
output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "ARN of the Target Group to register services"
  value       = aws_lb_target_group.api_gateway.arn
}
