# ==================================================================================
# AWS Application Load Balancer - DISABLED
# ==================================================================================
# This file is disabled because the project uses Nginx for load balancing instead 
# of AWS ALB (per project requirements - cannot use AWS Load Balancer).
# The Nginx configuration is in: phase2-services/nginx-config.conf
# ==================================================================================

# # Application Load Balancer
# resource "aws_lb" "main" {
#   name               = "clp-${var.environment}-alb-${var.random_suffix}"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [var.alb_sg_id]
#   subnets            = var.public_subnet_ids
#
#   enable_deletion_protection = false
#
#   tags = merge(var.common_tags, {
#     Name = "${var.name_prefix}-alb"
#   })
# }
#
# # ALB Listener (HTTP)
# resource "aws_lb_listener" "http" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = "80"
#   protocol          = "HTTP"
#
#   default_action {
#     type = "fixed-response"
#
#     fixed_response {
#       content_type = "application/json"
#       message_body = "{\"message\": \"Not Found\", \"error\": 404}"
#       status_code  = "404"
#     }
#   }
# }
#
# # Target Groups
# resource "aws_lb_target_group" "services" {
#   for_each = var.service_ports
#
#   name        = "clp-${each.key}-tg-${var.random_suffix}"
#   port        = each.value
#   protocol    = "HTTP"
#   vpc_id      = var.vpc_id
#   target_type = "instance"
#
#   health_check {
#     enabled             = true
#     path                = "/health"
#     interval            = 30
#     timeout             = 5
#     healthy_threshold   = 2
#     unhealthy_threshold = 2
#     matcher             = "200"
#   }
#
#   tags = merge(var.common_tags, {
#     Name = "${var.name_prefix}-${each.key}-tg"
#   })
# }
#
# # Target Group Attachments
# resource "aws_lb_target_group_attachment" "services" {
#   for_each = {
#     for pair in setproduct(keys(var.service_ports), range(var.app_node_count)) :
#     "${pair[0]}-${pair[1]}" => {
#       service_name = pair[0]
#       node_index   = pair[1]
#     }
#   }
#
#   target_group_arn = aws_lb_target_group.services[each.value.service_name].arn
#   target_id        = aws_instance.app_nodes[each.value.node_index].id
#   port             = var.service_ports[each.value.service_name]
# }
#
# # Listener Rules - All commented out (using Nginx instead)
# # Documents, TTS, STT, Chat, Quiz, User service routes are all handled by Nginx
