from kafka import KafkaProducer

class KafkaProducerSparkService:
    def __init__(self, kafka_broker: str, topic: str) -> None:
        self.producer = KafkaProducer(bootstrap_servers=[kafka_broker])
        self.topic = topic
    
    def enviar_mensaje(self, topic: str, mensaje: dict) -> dict:
        try:
            self.producer.send(topic, str(mensaje).encode("utf-8"))
            self.producer.flush()

            return {"message": "Mensaje enviado correctamente"}
        except Exception as e:
            return {"error": str(e)}
