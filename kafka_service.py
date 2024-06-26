import json
from kafka import KafkaProducer, KafkaConsumer
import threading
from db_mongo_service import MongoDatabaseService

class KafkaService:
    def __init__(self, database: MongoDatabaseService, kafka_broker: str) -> None:
        self.database = database
        self.kafka_broker = kafka_broker
        self.topics = []
    
    def enviar_mensaje(self, topic: str, autor: str, mensaje: str) -> None: 
        producer = KafkaProducer(bootstrap_servers=[self.kafka_broker])
        producer.send(topic, mensaje.encode('utf-8'))
        producer.flush()
    
        # guardar mensaje en base de datos
        self.database.guardar_mensaje_kafka(topic, autor, mensaje)
        
    def escuchar_mensajes(self, topic: str) -> KafkaConsumer:
        consumer = KafkaConsumer(topic, bootstrap_servers=[self.kafka_broker])
        self.topics.append(topic)

        def consumir_mensajes():
            for message in consumer:
                mensaje = message.value.decode('utf-8')
                print(f"Nuevo mensaje en {topic}: {mensaje}")
        
        thread = threading.Thread(target=consumir_mensajes)
        thread.start()

        return consumer
    
    def listar_mensajes(self, topic: str) -> list:
        return self.database.listar_mensajes_kafka(topic)
    
    def listar_topics(self) -> list:
        return self.topics
    
#Kafka endpoints
#inicializar sesion de edicion de encuesta
    def start_session(self, survey_id: str):
        topic = f"survey_{survey_id}_edit"
        if topic not in self.topics:
            self.escuchar_mensajes(topic)
        return topic
    
#enviar cambios al sistema
    def submit_changes(self, survey_id: str, cambios: dict, autor: str) -> None:
        topic = f"survey_{survey_id}_edit"
        cambios_json = json.dumps(cambios)
        #Guardar cambios en la base de datos
        self.database.actualizar_encuesta(survey_id, cambios)
        self.enviar_mensaje(topic, autor, cambios_json)

#Consulta el estado de los cambios
    def get_status(self, survey_id: str):
        topic = f"survey_{survey_id}_edit"
        return self.listar_mensajes(topic)
    