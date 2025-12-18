#!/bin/bash

# Update system
apt-get update -y
apt-get upgrade -y

# Install Java and dependencies
apt-get install -y openjdk-11-jdk wget tar net-tools

# Download Kafka
wget https://archive.apache.org/dist/kafka/3.5.1/kafka_2.13-3.5.1.tgz -O /tmp/kafka.tgz
tar -xzf /tmp/kafka.tgz -C /opt/
mv /opt/kafka_2.13-3.5.1 /opt/kafka

# Create Kafka directories
mkdir -p /tmp/kafka-logs
mkdir -p /var/log/kafka

# Get private IP
PRIVATE_IP=$(hostname -I | awk '{print $1}')

# Configure Kafka server.properties
cat <<EOF > /opt/kafka/config/server.properties
# Server Basics
broker.id=${broker_id}
listeners=PLAINTEXT://0.0.0.0:9092,PLAINTEXT_INTERNAL://0.0.0.0:9093
advertised.listeners=PLAINTEXT://$${PRIVATE_IP}:9092
inter.broker.listener.name=PLAINTEXT_INTERNAL

# Zookeeper
zookeeper.connect=${broker_ips[0]}:2181,${broker_ips[1]}:2181,${broker_ips[2]}:2181

# Logs
log.dirs=/tmp/kafka-logs
log.retention.hours=168
log.cleanup.policy=delete

# Replication
num.partitions=3
default.replication.factor=2
min.insync.replicas=2
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

# Performance
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
EOF

# Configure Zookeeper (only on first 3 brokers for Zookeeper)
if [ ${broker_id} -le 3 ]; then
  ZK_ID=${broker_id}
  
  cat <<EOF > /opt/kafka/config/zookeeper.properties
# Zookeeper Basics
dataDir=/tmp/zookeeper
clientPort=2181
maxClientCnxns=0
admin.enableServer=false

# Ensemble
server.1=${broker_ips[0]}:2888:3888
server.2=${broker_ips[1]}:2888:3888
server.3=${broker_ips[2]}:2888:3888

# Tick Time
tickTime=2000
initLimit=10
syncLimit=5
EOF
  
  # Create Zookeeper data directory and myid file
  mkdir -p /tmp/zookeeper
  echo $${ZK_ID} > /tmp/zookeeper/myid
  
  # Start Zookeeper
  /opt/kafka/bin/zookeeper-server-start.sh -daemon /opt/kafka/config/zookeeper.properties
  sleep 10
fi

# Start Kafka
/opt/kafka/bin/kafka-server-start.sh -daemon /opt/kafka/config/server.properties
sleep 20

# Create topics (only on first broker)
if [ ${broker_id} -eq 1 ]; then
  sleep 30  # Wait for cluster to stabilize
  
  # Create all required topics with proper replication
  /opt/kafka/bin/kafka-topics.sh --create --topic document.uploaded \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic document.processed \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic notes.generated \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic quiz.requested \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic quiz.generated \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic audio.generation.requested \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic audio.generation.completed \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic audio.transcription.requested \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic audio.transcription.completed \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  /opt/kafka/bin/kafka-topics.sh --create --topic chat.message \
    --bootstrap-server localhost:9092 --replication-factor 2 --partitions 3
  
  # List topics to verify
  /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
fi

# Create systemd service for Kafka
cat <<EOF > /etc/systemd/system/kafka.service
[Unit]
Description=Apache Kafka Server
Documentation=http://kafka.apache.org/documentation.html
After=network.target

[Service]
Type=simple
User=root
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable kafka
systemctl start kafka

echo "Kafka setup complete on broker ${broker_id}"