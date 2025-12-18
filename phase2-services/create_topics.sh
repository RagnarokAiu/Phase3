#!/bin/bash
echo "Waiting for Kafka to be ready..."
# Simple sleep loop or use kafka-topics to check
sleep 30

echo "Creating topics..."
KAFKA_HOST="kafka-1:29092"

# Topics for Member 1 Requirements
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic document.uploaded
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic document.processed
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic notes.generated

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic quiz.requested
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic quiz.generated

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic audio.transcription.requested
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic audio.transcription.completed

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic audio.generation.requested
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic audio.generation.completed

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_HOST --partitions 3 --replication-factor 3 --topic chat.message

echo "All topics created successfully."
