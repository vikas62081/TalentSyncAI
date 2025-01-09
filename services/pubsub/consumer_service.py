from kafka import KafkaConsumer
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self, kafka_broker="localhost:9092", topic="test-topic", group_id="test-group"):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.group_id = group_id

        # Create the Kafka consumer
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.kafka_broker,
            group_id=self.group_id,
            auto_offset_reset="earliest",  # Start from the beginning of the topic if no offset is found
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))  # Deserialize messages from JSON
        )
        logger.info(f"Connected to Kafka broker at {self.kafka_broker}. Subscribed to topic '{self.topic}'.")

    def get_messages(self):
        """
        Consumes messages from the Kafka topic.
        """
        return self.consumer

    def close(self):
        """
        Closes the consumer connection.
        """
        self.consumer.close()
        logger.info("Kafka consumer connection closed.")

# Example usage
if __name__ == "__main__":
    kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "test-topic")
    group_id = os.getenv("KAFKA_GROUP_ID", "test-group")

    consumer = KafkaConsumerService(kafka_broker=kafka_broker, topic=topic, group_id=group_id)

    try:
        consumer.consume_messages()
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user.")
        consumer.close()