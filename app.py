import os

from flask import Flask, request, make_response

from db_postgre import PostgreDatabase
from db_postgre_service import PostgreDatabaseService

from db_mongo import MongoDB
from db_mongo_service import MongoDatabaseService

POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
POSTGRES_DB_PORT = os.getenv('POSTGRES_DB_PORT')

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT'))
MONGO_DB_USER = os.getenv('MONGO_DB_USER')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')

postgre_db = PostgreDatabase(database=POSTGRES_DB_NAME, host=POSTGRES_DB_HOST,
                                user=POSTGRES_DB_USER, password=POSTGRES_DB_PASSWORD,
                                port=POSTGRES_DB_PORT)

mongo_db = MongoDB(host=MONGO_DB_HOST, port=MONGO_DB_PORT, usernamen=MONGO_DB_USER, password=MONGO_DB_PASSWORD)

app = Flask(__name__)
postgre_db_service = PostgreDatabaseService(database=postgre_db)
mongo_db_service = MongoDatabaseService(database=mongo_db)

@app.route('/')
def home():
    return 'Hello, World!'

# ENDPOINT MUESTRA DE CONSULTA A BASE DE DATOS POSTGRESQL
@app.route('/prueba')
def prueba():
    data = postgre_db_service.query_prueba()
    return data

# ENDPOINT MUESTRA DE INSERCIÓN A BASE DE DATOS POSTGRESQL
@app.route('/insertar_user', methods=['POST'])
def insertar_user():
    user = request.json
    data = postgre_db_service.insertar_user(user)
    return data

#Endpoints para autenticación
@app.route('/auth/register', methods = ['POST'])
def register():
    user = request.json
    data = postgre_db_service.insertar_user(user)
    return data

#Aqui se tiene que crear el Token y guardarlo en la cookie
@app.route('/auth/login', methods = ['POST'])
def login():
    None

@app.route('/auth/logout')
def logout():
    None

#Endpoints para Usuarios
@app.route('/users')
def getUsers():
    None

@app.route('/users/<int:id>')
def getUser():
    None

@app.route('/users/<int:id>', methods = ['PUT'])
def putUser():
    None

@app.route('/users/<int:id>', methods = ['DELETE'])
def deleteUser():
    None

#Enpoints para Encuestas [Anthony]
@app.route('/surveys', methods = ['POST'])
def postEncuesta():
    None

@app.route('/surveys')
def getSurveys():
    None

@app.route('/surveys/<int:id>')
def getSurvey():
    None

@app.route('/surveys/<int:id>', methods = ['PUT'])
def putSurvey():
    None

@app.route('/surveys/<int:id>', methods = ['DELETE'])
def deleteSurvey():
    None

@app.route('/surveys/<int:id>/publish', methods = ['POST'])
def publishSurvey():
    None

#Endpoints para las Preguntas de las Encuestas [Anthony]
@app.route('/surveys/<int:id>/questions', methods = ['POST'])
def postQuestion():
    None

@app.route('/surveys/<int:id>/questions')
def getQuestions():
    None

@app.route('/surveys/<int:id>/questions/<int:questionId>', methods = ['PUT'])
def putQuestion():
    None

@app.route('/surveys/<int:id>/questions/<int:questionId>', methods = ['DELETE'])
def deleteQuestion():
    None

#Endpoints para las Respuestas de las Encuestas [Anthony]
@app.route('/surveys/<int:id>/responses', methods = ['POST'])
def postResponse():
    None

@app.route('/surveys/<int:id>/responses')
def getResponses():
    None

#Endpoints para los encuestados [Decidir - Preguntar algo al profe]
@app.route('/respondents', methods = ['POST'])
def postRespondent():
    None

@app.route('/respondents')
def getRespondents():
    None

@app.route('/respondents/<int:id>')
def getDetailsRespondent():
    None

@app.route('/respondents/<int:id>', methods = ['PUT'])
def putDetailsRespondent():
    None

@app.route('/respondents/<int:id>', methods = ['DELETE'])
def deleteRespondent():
    None

#Endpoint para los Reportes y Análisis [Dario - Preguntar acerca del analisis al profe]
@app.route('/surveys/<int:id>/analysis')
def getAnalisis():
    None