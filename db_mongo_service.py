from db_mongo import MongoDB
from kafka_service_for_spark import KafkaProducerSparkService
import os

KAFKA_BROKER_SPARK = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC_SPARK_RESPONSES = os.getenv("KAFKA_TOPIC_SPARK_RESPONSES")
KAFKA_TOPIC_SPARK_SURVEYS = os.getenv("KAFKA_TOPIC_SPARK_SURVEYS")

class MongoDatabaseService:
    def __init__(self, database: MongoDB) -> None:
        self.database = database
        # Servicio de Kafka para Spark
        self.kafka_service_for_spark_responses = KafkaProducerSparkService(kafka_broker=KAFKA_BROKER_SPARK, topic=KAFKA_TOPIC_SPARK_RESPONSES)
        self.kafka_service_for_spark_surveys = KafkaProducerSparkService(kafka_broker=KAFKA_BROKER_SPARK, topic=KAFKA_TOPIC_SPARK_SURVEYS)
        self.topic_spark_responses = KAFKA_TOPIC_SPARK_RESPONSES
        self.topic_spark_surveys = KAFKA_TOPIC_SPARK_SURVEYS
    
    # ----------------- Consultas Encuestas ----------------- #
    def crear_encuesta(self, encuesta: dict, token: int) -> dict:
        try:
            database_response = self.database.crear_encuesta(encuesta, token)

            # agregar id de la encuesta a las respuestas
            encuesta["id_encuesta"] = str(database_response.inserted_id)
            # Convertir el id de la encuesta a string para que sea serializable
            encuesta['_id'] = str(encuesta['_id'])

            # Enviar encuesta a Spark mediante Kafka
            self.kafka_service_for_spark_surveys.enviar_mensaje(self.topic_spark_surveys, encuesta)
            return encuesta
        except Exception as e:
            return {"error": str(e)}
    
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

            # agregar id de la encuesta a las respuestas
            respuestas["id_encuesta"] = id
            self.kafka_service_for_spark_responses.enviar_mensaje(self.topic_spark_responses, respuestas)
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