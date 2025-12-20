import json
import threading
from typing import Callable, Dict, Any, List, Optional

try:
    from kafka import KafkaConsumer as KafkaConsumerLib
except ImportError:
    KafkaConsumerLib = None

from .config import KAFKA_BOOTSTRAP_SERVERS


class KafkaMessageConsumer:
    """Kafka consumer wrapper for receiving events."""
    
    def __init__(self, topics: List[str], group_id: str):
        self.topics = topics
        self.group_id = group_id
        self.consumer = None
        self._running = False
        self._thread = None
        self._handlers: Dict[str, Callable] = {}
        
    def _initialize_consumer(self):
        """Initialize Kafka consumer."""
        if not KafkaConsumerLib:
            print("Warning: kafka-python not installed")
            return False
            
        try:
            self.consumer = KafkaConsumerLib(
                *self.topics,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            print(f"Kafka consumer connected: {self.topics}")
            return True
        except Exception as e:
            print(f"Kafka consumer connection failed: {e}")
            return False
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """Register a handler for a specific event type."""
        self._handlers[event_type] = handler
        
    def _consume_loop(self):
        """Main consumption loop."""
        if not self.consumer:
            return
            
        while self._running:
            try:
                for message in self.consumer:
                    if not self._running:
                        break
                    
                    data = message.value
                    event_type = data.get('event', message.topic)
                    
                    # Call registered handler
                    if event_type in self._handlers:
                        try:
                            self._handlers[event_type](data)
                        except Exception as e:
                            print(f"Handler error for {event_type}: {e}")
                    else:
                        print(f"No handler for event: {event_type}")
                        
            except Exception as e:
                print(f"Consumer error: {e}")
                
    def start(self):
        """Start consuming messages in background thread."""
        if not self._initialize_consumer():
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        print(f"Kafka consumer started for: {self.topics}")
        
    def stop(self):
        """Stop consuming messages."""
        self._running = False
        if self.consumer:
            self.consumer.close()
        if self._thread:
            self._thread.join(timeout=5)
