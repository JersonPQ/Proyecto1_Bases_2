from db_mongo import MongoDB
from kafka_service_for_spark import KafkaProducerSparkService
import os

KAFKA_BROKER_SPARK = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC_SPARK = os.getenv("KAFKA_TOPIC_SPARK")

class MongoDatabaseService:
    def __init__(self, database: MongoDB) -> None:
        self.database = database
        # Servicio de Kafka para Spark
        self.kafka_service_for_spark = KafkaProducerSparkService(kafka_broker=KAFKA_BROKER_SPARK, topic=KAFKA_TOPIC_SPARK)
        self.topic_spark = KAFKA_TOPIC_SPARK
    
    # ----------------- Consultas Encuestas ----------------- #
    def crear_encuesta(self, encuesta: dict, token: int) -> dict:
        return self.database.crear_encuesta(encuesta, token)
    
    def listar_encuestas(self) -> list:
        return self.database.listar_encuestas()
    
    def detalles_encuesta(self, id: str) -> dict:
        return self.database.detalles_encuesta(id)
    
    def actualizar_encuesta(self, id: str, encuesta: dict) -> dict:
        return self.database.actualizar_encuesta(id, encuesta)
    
    def eliminar_encuesta(self, id: str) -> dict:
        return self.database.eliminar_encuesta(id)
    
    def publicar_encuesta(self, id: str) -> dict:
        return self.database.publicar_encuesta(id)
    
    # ----------------- Consultas Preguntas ----------------- #
    def agregar_preguntas(self, id: str, preguntas: list) -> dict:
        return self.database.agregar_preguntas(id, preguntas)
    
    def listar_preguntas(self, id: str) -> list:
        return self.database.listar_preguntas(id)
    
    def actualizar_pregunta(self, id: str, pregunta: dict, id_pregunta:str) -> dict:
        return self.database.actualizar_pregunta(id, pregunta, id_pregunta)
    
    def eliminar_pregunta(self, id: str, id_pregunta: str) -> dict:
        return self.database.eliminar_pregunta(id, id_pregunta)
    
    # ----------------- Consultas Respuestas ----------------- #
    def enviar_respuestas(self, id: str, respuestas: list) -> dict:
        # Enviar respuestas a Spark
        try:
            return_database = self.database.enviar_respuestas(id, respuestas)
            self.kafka_service_for_spark.enviar_mensaje(self.topic_spark, respuestas)
            return return_database
        except Exception as e:
            return {"error": str(e)}

    def listar_respuestas(self, id: str) -> list:
        return self.database.listar_respuestas(id)
    

    # ----------------- Funciones de Kafka ----------------- #
    def guardar_mensaje_kafka(self, topic: str, autor: str, message: dict) -> None:
        return self.database.guardar_mensaje_kafka(topic, autor, message)
    
    def listar_mensajes_kafka(self, topic: str) -> list:
        return self.database.listar_mensajes_kafka(topic)