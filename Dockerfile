FROM python:3.11

ENV MONGO_DB_USER='root'
ENV MONGO_DB_PASSWORD='example'

ENV POSTGRES_DB_USER='postgres'
ENV POSTGRES_DB_PASSWORD='postgres'
ENV POSTGRES_DB_NAME='encuesta'
ENV POSTGRES_DB_HOST='localhost'
ENV POSTGRES_DB_PORT=5432

ENV REDIS_DB_HOST='redis'
ENV REDIS_DB_PORT=6379

ENV KAFKA_BROKER='kafka:29092'

ENV NEO4J_USER='neo4j'
ENV NEO4J_PASSWORD='password'
ENV NEO4J_PORT=7687

# Set the working directory
WORKDIR /opt/app

COPY . .

# Install Poetry
RUN pip install poetry
# Install dependencies
RUN poetry install

# Create a volume
VOLUME /data_store

# Expose the port
EXPOSE 5000

# Run the application
CMD ["poetry", "run", "python3", "-m", "flask", "run", "--host=0.0.0.0"]