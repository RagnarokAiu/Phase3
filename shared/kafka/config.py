import os

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Producer Configuration
PRODUCER_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    "value_serializer": lambda v: __import__('json').dumps(v).encode('utf-8'),
    "key_serializer": lambda k: k.encode('utf-8') if k else None,
}

# Consumer Configuration
CONSUMER_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
    "value_deserializer": lambda v: __import__('json').loads(v.decode('utf-8')),
    "auto_offset_reset": "earliest",
    "enable_auto_commit": True,
}

def get_producer_config():
    """Get Kafka producer configuration."""
    return PRODUCER_CONFIG.copy()

def get_consumer_config(group_id: str):
    """Get Kafka consumer configuration with group ID."""
    config = CONSUMER_CONFIG.copy()
    config["group_id"] = group_id
    return config
