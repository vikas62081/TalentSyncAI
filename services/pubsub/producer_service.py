from kafka import KafkaProducer
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self, kafka_broker="localhost:9092", topic="test-topic"):
        self.kafka_broker = kafka_broker
        self.topic = topic

        # Create the Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages as JSON
        )
        logger.info(f"Connected to Kafka broker at {self.kafka_broker}")

    def send_message(self, key, value):
        """
        Sends a message to the Kafka topic.

        :param key: Message key (optional).
        :param value: Message value (payload).
        """
        try:
            future = self.producer.send(self.topic, key=key.encode('utf-8') if key else None, value=value)
            # Block for 'send' to complete
            result = future.get(timeout=10)
            logger.info(f"Message sent to topic '{self.topic}': {value}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")

    def close(self):
        """
        Closes the producer connection.
        """
        self.producer.close()
        logger.info("Kafka producer connection closed.")

# Example usage
if __name__ == "__main__":
    kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "test-topic")

    producer = KafkaProducerService(kafka_broker=kafka_broker, topic=topic)

    try:
        # Example messages
        messages = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Doe", "email": "jane@example.com"},
        ]
        
        for message in messages:
            producer.send_message(key=str(message["id"]), value=message)

    finally:
        producer.close()