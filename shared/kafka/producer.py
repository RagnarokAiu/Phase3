import json
from typing import Any, Dict, Optional
from confluent_kafka import Producer, KafkaError

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class KafkaProducer:
    """Kafka producer for publishing events."""
    
    def __init__(self):
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer."""
        config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'cloud-learning-platform-producer',
            'acks': 'all',  # Wait for all replicas to acknowledge
            'retries': 3,   # Retry on failure
            'compression.type': 'snappy',
        }
        
        try:
            self.producer = Producer(config)
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    
    def delivery_callback(self, err: Optional[KafkaError], msg):
        """Callback for message delivery reports."""
        if err:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(
                f'Message delivered to {msg.topic()} '
                f'[partition {msg.partition()}] at offset {msg.offset()}'
            )
    
    def produce(
        self,
        topic: str,
        data: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """Produce a message to Kafka topic."""
        try:
            # Convert data to JSON
            message = json.dumps(data).encode('utf-8')
            
            # Produce message
            self.producer.produce(
                topic=topic,
                value=message,
                key=key,
                callback=self.delivery_callback
            )
            
            # Poll for events (triggers delivery callbacks)
            self.producer.poll(0)
            
            logger.debug(f"Produced message to topic '{topic}': {data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to produce message to Kafka: {e}")
            return False
    
    def produce_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce a standardized event to Kafka."""
        event = {
            "event_type": event_type,
            "timestamp": self._get_timestamp(),
            "data": data,
            "metadata": metadata or {},
            "version": "1.0"
        }
        
        return self.produce(event_type, event)
    
    def flush(self, timeout: float = 5.0):
        """Flush any outstanding messages."""
        try:
            self.producer.flush(timeout)
            logger.debug("Kafka producer flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush Kafka producer: {e}")
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    # Convenience methods for common events
    def produce_document_uploaded(
        self,
        document_id: str,
        filename: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce document.uploaded event."""
        data = {
            "document_id": document_id,
            "filename": filename,
            "user_id": user_id,
            "status": "uploaded"
        }
        return self.produce_event("document.uploaded", data, metadata)
    
    def produce_document_processed(
        self,
        document_id: str,
        text_length: int,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce document.processed event."""
        data = {
            "document_id": document_id,
            "text_length": text_length,
            "user_id": user_id,
            "status": "processed"
        }
        return self.produce_event("document.processed", data, metadata)
    
    def produce_notes_generated(
        self,
        document_id: str,
        summary: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce notes.generated event."""
        data = {
            "document_id": document_id,
            "summary": summary[:500],  # Truncate for event
            "user_id": user_id
        }
        return self.produce_event("notes.generated", data, metadata)
    
    def produce_audio_generation_requested(
        self,
        text: str,
        user_id: str,
        language: str = "en",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce audio.generation.requested event."""
        data = {
            "text": text[:1000],  # Truncate for event
            "user_id": user_id,
            "language": language
        }
        return self.produce_event("audio.generation.requested", data, metadata)
    
    def produce_chat_message(
        self,
        conversation_id: str,
        message: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Produce chat.message event."""
        data = {
            "conversation_id": conversation_id,
            "message": message[:1000],  # Truncate for event
            "user_id": user_id
        }
        return self.produce_event("chat.message", data, metadata)


# Global Kafka producer instance
kafka_producer = KafkaProducer()