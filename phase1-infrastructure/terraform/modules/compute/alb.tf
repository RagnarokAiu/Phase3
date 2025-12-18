# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.name_prefix}-alb-${var.random_suffix}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-alb"
  })
}

# ALB Listener (HTTP)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "application/json"
      message_body = "{\"message\": \"Not Found\", \"error\": 404}"
      status_code  = "404"
    }
  }
}

# Target Groups
resource "aws_lb_target_group" "services" {
  for_each = var.service_ports

  name        = "${var.name_prefix}-${each.key}-tg-${var.random_suffix}"
  port        = each.value
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-${each.key}-tg"
  })
}

# Target Group Attachments
# Note: We need to attach instances to target groups. 
# Since we have multiple app nodes and multiple target groups, we need a complex loop or separate attachments.
# For simplicity in this static setup, we'll attach all app nodes to all TGs.
# Ideally each service runs on specific nodes, but here all services run on all app nodes.

resource "aws_lb_target_group_attachment" "services" {
  for_each = {
    for pair in setproduct(keys(var.service_ports), range(var.app_node_count)) :
    "${pair[0]}-${pair[1]}" => {
      service_name = pair[0]
      node_index   = pair[1]
    }
  }

  target_group_arn = aws_lb_target_group.services[each.value.service_name].arn
  target_id        = aws_instance.app_nodes[each.value.node_index].id
  port             = var.service_ports[each.value.service_name]
}


# Listener Rules

resource "aws_lb_listener_rule" "documents" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["document"].arn
  }

  condition {
    path_pattern {
      values = ["/api/documents*"]
    }
  }
}

resource "aws_lb_listener_rule" "tts" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 110

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["tts"].arn
  }

  condition {
    path_pattern {
      values = ["/api/tts*"]
    }
  }
}

resource "aws_lb_listener_rule" "stt" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 120

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["stt"].arn
  }

  condition {
    path_pattern {
      values = ["/api/stt*"]
    }
  }
}

resource "aws_lb_listener_rule" "chat" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 130

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["chat"].arn
  }

  condition {
    path_pattern {
      values = ["/api/chat*"]
    }
  }
}

resource "aws_lb_listener_rule" "quiz" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 140

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["quiz"].arn
  }

  condition {
    path_pattern {
      values = ["/api/quiz*"]
    }
  }
}

resource "aws_lb_listener_rule" "user" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 150

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.services["user"].arn
  }

  condition {
    path_pattern {
      values = ["/api/users*"]
    }
  }
}
