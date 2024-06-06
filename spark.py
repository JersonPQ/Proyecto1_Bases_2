import findspark
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import os

# Variables de entorno
KAFKA_BROKER_SPARK_EXTERNAL = os.getenv("KAFKA_BROKER_SPARK_EXTERNAL")
KAFKA_TOPIC_SPARK = os.getenv("KAFKA_TOPIC_SPARK")

# Inicializar el servicio de Spark
findspark.init()
spark = SparkSession.builder.appName("Encuesta_Spark")\
        .master("spark://spark-master:7077").getOrCreate()

broker = KAFKA_BROKER_SPARK_EXTERNAL
topic = KAFKA_TOPIC_SPARK

dfraw = spark.readStream.format("kafka")\
    .option("kafka.bootstrap.servers", broker)\
    .option("subscribe", topic)\
    .option("includeHeaders", "false")\
    .option("startingOffsets", "latest")\
    .load()