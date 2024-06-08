import findspark
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql import Row
import os
import datetime as dt

import json

from kafka import KafkaConsumer, KafkaProducer

# Variables de entorno
KAFKA_BROKER_SPARK = os.getenv("KAFKA_BROKER_SPARK")
KAFKA_TOPIC_SPARK_RESPONSES = os.getenv("KAFKA_TOPIC_SPARK_RESPONSES")
KAFKA_TOPIC_SPARK_SURVEYS = os.getenv("KAFKA_TOPIC_SPARK_SURVEYS")

broker = KAFKA_BROKER_SPARK
topic_responses = KAFKA_TOPIC_SPARK_RESPONSES
topic_surveys = KAFKA_TOPIC_SPARK_SURVEYS

def convertir_a_dataframe_encuesta(coleccion_mongo: dict) -> dict:
        try:
                df = spark.createDataFrame([
                        Row(id=coleccion_mongo["id_encuesta"],
                            titulo=coleccion_mongo["titulo"],
                            descripcion=coleccion_mongo["descripcion"],
                            publicada=coleccion_mongo["publicada"],
                            fecha_creacion=dt.datetime.now())
                ])
                return df
        except Exception as e:
                return {"error": str(e)}

def convertir_a_dataframe_respuesta(coleccion_mongo: dict) -> None:
        try:
                df = spark.createDataFrame([
                        Row(survey_id=coleccion_mongo["id_encuesta"],
                            user_id=coleccion_mongo["user_id"],
                            respuestas=json.dumps(coleccion_mongo["respuestas"]),
                            publicada=coleccion_mongo["publicada"],
                            fecha_respuesta=dt.datetime.now())
                ])
                return df
        except Exception as e:
                return {"error": str(e)}

def guardar_encuesta_en_postgre(dataframe: dict) -> dict:
        try:
                dataframe.select("titulo", "descripcion", "publicada", "fecha_creacion")\
                        .write.format("jdbc")\
                        .option("url", "jdbc:postgresql://postgredb:5432/encuesta")\
                        .option("dbtable", "surveys")\
                        .option("user", "postgres")\
                        .option("password", "postgres")\
                        .option("driver", "org.postgresql.Driver")\
                        .mode("append")\
                        .save()
                return {"message": "Encuesta guardada correctamente"}
        except Exception as e:
                return {"error": str(e)}
        
def guardar_respuesta_en_postgre(dataframe: dict) -> dict:
        try:
                dataframe.select("user_id", "respuestas", "publicada", "fecha_respuesta")\
                        .write.format("jdbc")\
                        .option("url", "jdbc:postgresql://postgredb:5432/encuesta")\
                        .option("dbtable", "responses")\
                        .option("user", "postgres")\
                        .option("password", "postgres")\
                        .option("driver", "org.postgresql.Driver")\
                        .mode("append")\
                        .save()
                return {"message": "Respuesta guardada correctamente"}
        except Exception as e:
                return {"error": str(e)}

try:
        # Inicializar Spark
        spark = SparkSession.builder\
                .appName("Encuesta_Spark")\
                .master("spark://spark-master:7077")\
                .config("spark.jars", "/opt/app/jars/postgresql-42.7.3.jar")\
                .getOrCreate()
                # .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1")\

        spark.sparkContext.setLogLevel("ERROR")
except Exception as e:
        print(f"Error al inicializar Spark: {str(e)}")
        exit()

try:
        consumer = KafkaConsumer(topic_responses, topic_surveys,bootstrap_servers=broker)
        producer = KafkaProducer(bootstrap_servers=broker)
        for message in consumer:
                if message is not None and message.topic == topic_responses:
                        mensaje = message.value.decode("utf-8")

                        # Convertir mensaje a diccionario
                        mensaje = eval(mensaje)

                        # Convertir mensaje a DataFrame
                        df = convertir_a_dataframe_respuesta(mensaje)

                        # Guardar encuesta en Postgre
                        resultado = guardar_respuesta_en_postgre(df)
                elif message is not None and message.topic == topic_surveys:
                        mensaje = message.value.decode("utf-8")

                        # Convertir mensaje a diccionario
                        mensaje = eval(mensaje)

                        # Convertir mensaje a DataFrame
                        df = convertir_a_dataframe_encuesta(mensaje)

                        # Guardar encuesta en Postgre
                        resultado = guardar_encuesta_en_postgre(df)

except Exception as e:
        print(f"Error al conectar con Kafka: {str(e)}")
        exit()