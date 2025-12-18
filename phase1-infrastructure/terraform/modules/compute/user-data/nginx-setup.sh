#!/bin/bash

# Update system
apt-get update -y
apt-get upgrade -y

# Install Nginx
apt-get install -y nginx

# Create Nginx configuration
cat <<EOF > /etc/nginx/sites-available/cloud-platform
upstream document_service {
    server ${app_node_ips[0]}:${service_ports["document"]};
    server ${app_node_ips[1]}:${service_ports["document"]};
    server ${app_node_ips[2]}:${service_ports["document"]};
}

upstream tts_service {
    server ${app_node_ips[0]}:${service_ports["tts"]};
    server ${app_node_ips[1]}:${service_ports["tts"]};
    server ${app_node_ips[2]}:${service_ports["tts"]};
}

upstream stt_service {
    server ${app_node_ips[0]}:${service_ports["stt"]};
    server ${app_node_ips[1]}:${service_ports["stt"]};
    server ${app_node_ips[2]}:${service_ports["stt"]};
}

upstream chat_service {
    server ${app_node_ips[0]}:${service_ports["chat"]};
    server ${app_node_ips[1]}:${service_ports["chat"]};
    server ${app_node_ips[2]}:${service_ports["chat"]};
}

upstream quiz_service {
    server ${app_node_ips[0]}:${service_ports["quiz"]};
    server ${app_node_ips[1]}:${service_ports["quiz"]};
    server ${app_node_ips[2]}:${service_ports["quiz"]};
}

upstream user_service {
    server ${app_node_ips[0]}:${service_ports["user"]};
    server ${app_node_ips[1]}:${service_ports["user"]};
    server ${app_node_ips[2]}:${service_ports["user"]};
}

server {
    listen 80;
    server_name _;
    
    # Document Service
    location /api/documents {
        proxy_pass http://document_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # TTS Service
    location /api/tts {
        proxy_pass http://tts_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # STT Service
    location /api/stt {
        proxy_pass http://stt_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Chat Service
    location /api/chat {
        proxy_pass http://chat_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Quiz Service
    location /api/quiz {
        proxy_pass http://quiz_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # User Service
    location /api/users {
        proxy_pass http://user_service;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check endpoint
    location /health {
        return 200 '{"status": "healthy", "service": "nginx"}';
        add_header Content-Type application/json;
    }
    
    # Default route
    location / {
        return 200 'Cloud Learning Platform API Gateway';
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/cloud-platform /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test configuration and restart
nginx -t
systemctl restart nginx
systemctl enable nginx

# Install monitoring tools
apt-get install -y htop net-tools

echo "Nginx setup complete!"