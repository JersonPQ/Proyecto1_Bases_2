import json
import os

from flask import Flask, request, make_response, jsonify, redirect
from Security import Security

from db_postgre import PostgreDatabase
from db_postgre_service import PostgreDatabaseService

from db_mongo import MongoDB
from db_mongo_service import MongoDatabaseService

from db_redis import RedisDB
from db_redis_service import RedisDBService

from bson import json_util

from kafka_service import KafkaService

POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
POSTGRES_DB_PORT = os.getenv('POSTGRES_DB_PORT')

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST', 'localhost')
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT', '27017'))  
MONGO_DB_USER = os.getenv('MONGO_DB_USER', 'default_user')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', 'default_password')

REDIS_DB_HOST = os.getenv('REDIS_DB_HOST')
REDIS_DB_PORT = int(os.getenv('REDIS_DB_PORT'))

KAFKA_BROKER = os.getenv('KAFKA_BROKER')

# Conexion a las bases de datos
postgre_db = PostgreDatabase(database=POSTGRES_DB_NAME, host=POSTGRES_DB_HOST,
                                user=POSTGRES_DB_USER, password=POSTGRES_DB_PASSWORD,
                                port=POSTGRES_DB_PORT)

mongo_db = MongoDB(host=MONGO_DB_HOST, port=MONGO_DB_PORT, usernamen=MONGO_DB_USER, password=MONGO_DB_PASSWORD)

redis_db = RedisDB(host=REDIS_DB_HOST, port=REDIS_DB_PORT)

# Creación de la aplicación
app = Flask(__name__)

# Servicios de las bases de datos
postgre_db_service = PostgreDatabaseService(database=postgre_db)
mongo_db_service = MongoDatabaseService(database=mongo_db)
redis_db_service = RedisDBService(redis_databse=redis_db)

# Servicio de Kafka
kafka_service = KafkaService(database=mongo_db_service, kafka_broker=KAFKA_BROKER)


@app.route('/')
def home():
    return 'Proyecto de Base de Datos 2024-I Semestre \n \
        Integrantes: \n\tAnthony Guevara \n\tDarío Espinoza \n\tMarbel Brenes \n\tJerson Prendas'

#Endpoints para autenticación
@app.route('/auth/register', methods = ['POST'])
def register():
    user = request.json
    if not user or 'name' not in user or 'password' not in user or 'userRol' not in user:
        return jsonify({'message' : 'Faltan datos para realizar esta consulta.'})
    data = postgre_db_service.insertUser(user)

    # eliminar el cache de redis de users
    redis_db_service.delete_key("users")

    return data

#Aqui se tiene que crear el Token y guardarlo en la cookie
@app.route('/auth/login', methods = ['POST'])
def login():
    user = request.json
    if not user or 'name' not in user or 'password' not in user:
        return jsonify({'message' : 'Faltan datos para realizar esta consulta.'})
    data = postgre_db_service.getUser(user["name"], user["password"])
    if data is None:
        return jsonify({'message' : 'User not found.'})
    token = Security.generateTokem(data)
    response = make_response(data)
    response.set_cookie("token", token)
    response.set_cookie("userType", str(data["userRol"]))
    return response

@app.route('/auth/logout')
def logout():
    token = request.cookies.get("token")
    userType = request.cookies.get("userType")
    hasAccess = Security.verifyToken({"token" : token, "userType" : userType})
    if hasAccess[0]:
        response = make_response({"message" : "Log out. Hasta pronto"})
        response.set_cookie("token", "", expires=0)
        response.set_cookie("userType", "", expires=0)
        return response
    return jsonify({"message" : hasAccess[1]})

#Endpoints para Usuarios
@app.route('/users')
def getUsers():
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        data = redis_db_service.get_key("users")
        if data is not None:
            return data
        
        data = postgre_db_service.getUsers()
        print(token)
        
        # guardar la consulta en el cache de redis
        redis_db_service.set_key("users", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire("users", 120) 

        return data
    return jsonify({"message" : hasAccess[1]})

@app.route('/users/<int:id>')
def getUser(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        data = redis_db_service.get_key(f"user_{id}")
        if data is not None:
            return data
        
        data = postgre_db_service.getUserId(id)
        print(token)
        
        # guardar la consulta en el cache de redis
        redis_db_service.set_key(f"user_{id}", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire(f"user_{id}", 120) 

        return data
    return jsonify({"message" : hasAccess[1]})

@app.route('/users/<int:id>', methods = ['PUT'])
def putUser(id):
    token = request.cookies.get("token")
    userType = request.cookies.get("userType")
    if userType == "1":  
        hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    else:
        # verificar si ya la consulta está en el cache de redis
        data = redis_db_service.get_key(f"user_{id}")
        if data is None:
            data = postgre_db_service.getUserId(id)
        
        if 'name' not in data:
            return jsonify({"message" : "User not found"})
        hasAccess = Security.verifyToken({"token" : token, "userType" : userType})
        if data["name"] != hasAccess[1]:
            return jsonify({"message" : "You don't have permission"})
    if hasAccess[0]:
        data = request.json
        updatedUser = postgre_db_service.updateUser(id, data)
        if updatedUser:
            # eliminar el cache de redis del user con el id
            redis_db_service.delete_key(f"user_{id}")

            # eliminar el cache de redis de users
            redis_db_service.delete_key("users")

            return jsonify({"message" : "Cambios realizados"})
        return jsonify({"message" : "Cambios no realizados"})
    else:
        return jsonify({"message" : hasAccess[1]})

@app.route('/users/<int:id>', methods = ['DELETE'])
def deleteUser(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if hasAccess[0]:
        response = postgre_db_service.deleteUser(id)
        if response:
            # eliminar el cache de redis del user con el id
            redis_db_service.delete_key(f"user_{id}")

            # eliminar el cache de redis de users
            redis_db_service.delete_key("users")
            
            return jsonify({"message" : "Usuario eliminado"})
        return jsonify({"message" : "Error al elminar"})
    return jsonify({"message" : hasAccess[1]})

#Enpoints para Encuestas [Anthony]
#Autenticacion
@app.route('/surveys', methods = ['POST'])
def post_encuesta():
    encuesta= request.get_json()
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        hasAccess = Security.verifyToken({"token" : token, "userType" : 2})
        if not hasAccess[0]:
            return jsonify({"message" : "Ypu don't have permission"})
    #Agregar id usuario que crea la encuesta
    tokenUser = request.cookies.get("token")
    token = Security.generateTokenSurvey(tokenUser)
    resultado= mongo_db_service.crear_encuesta(encuesta,token)
    if resultado.acknowledged:
        # eliminar el cache de redis de surveys
        redis_db_service.delete_key("surveys")

        return jsonify({"message": "Encuesta creada exitosamente", "id": str(resultado.inserted_id)}), 201
    else:
        return jsonify({"message": "Error al crear la encuesta"}), 400

@app.route('/surveys', methods = ['GET'])
def get_surveys():
    # verificar si ya la consulta está en el cache de redis
    data = redis_db_service.get_key("surveys")
    if data is None:
        data = mongo_db_service.listar_encuestas()
        data = [{**survey, '_id': str(survey['_id'])} for survey in data]

        # guardar la consulta en el cache de redis
        redis_db_service.set_key("surveys", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire("surveys", 60) 

        data= json_util.dumps(data)

    return data, 200

@app.route('/surveys/<string:id>', methods = ['GET'])
def get_survey(id):
    id_to_search = id
    # verificar si ya la consulta está en el cache de redis
    data = redis_db_service.get_key(f"survey_{id}")
    if data is None:
        data = mongo_db_service.detalles_encuesta(id_to_search)

        # guardar la consulta en el cache de redis
        redis_db_service.set_key(f"survey_{id}", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire(f"survey_{id}", 120) 
        
    return data

#Autenticacion
@app.route('/surveys/<string:id>', methods = ['PUT'])
def put_survey(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id)

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta = request.get_json()
    id_to_search = id

    # eliminar el cache de redis del survey con el id
    redis_db_service.delete_key(f"survey_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")
    

    return mongo_db_service.actualizar_encuesta(id_to_search, encuesta)

#Autenticacion
@app.route('/surveys/<string:id>', methods = ['DELETE'])
def delete_survey(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id)

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    id_to_search = id

    # eliminar el cache de redis del user con el id
    redis_db_service.delete_key(f"survey_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")

    return mongo_db_service.eliminar_encuesta(id_to_search)

#Autenticacion
@app.route('/surveys/<string:id>/publish', methods = ['POST'])
def publish_survey(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        survey = mongo_db_service.detalles_encuesta(id) 
        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    id_to_search = id

    # eliminar el cache de redis del survey con el id
    redis_db_service.delete_key(f"survey_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")

    return mongo_db_service.publicar_encuesta(id_to_search)

#Endpoints para las Preguntas de las Encuestas [Anthony]
@app.route('/surveys/<string:id>/questions', methods = ['POST'])
def post_question(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id)

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta= id
    pregunta = request.get_json()

    # eliminar el cache de redis del survey en preguntas con el id de la encuesta
    redis_db_service.delete_key(f"questions_encuesta_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")

    # eliminar el cache del survey con el id
    redis_db_service.delete_key(f"survey_{id}")

    return mongo_db_service.agregar_preguntas(encuesta, pregunta)

@app.route('/surveys/<string:id>/questions', methods = ['GET'])
def get_questions(id):
    encuesta= id

    # verificar si ya la consulta está en el cache de redis
    data = redis_db_service.get_key(f"questions_encuesta_{id}")
    if data is None:
        data = mongo_db_service.listar_preguntas(encuesta)

        # guardar la consulta en el cache de redis
        redis_db_service.set_key(f"questions_encuesta_{id}", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire(f"questions_encuesta_{id}", 120) 
        
    return data

@app.route('/surveys/<string:id>/questions/<string:question_id>', methods = ['PUT'])
def put_question(id, question_id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id) 
            
            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta= id
    pregunta = request.get_json()
    id_pregunta = question_id

    # eliminar el cache de redis del survey con el id
    redis_db_service.delete_key(f"questions_encuesta_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")

    # eliminar el cache del survey con el id
    redis_db_service.delete_key(f"survey_{id}")

    return mongo_db_service.actualizar_pregunta(encuesta, pregunta, id_pregunta)

@app.route('/surveys/<string:id>/questions/<string:question_id>', methods = ['DELETE'])
def delete_question(id, question_id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id) 

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 
            
        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta= id
    id_pregunta = question_id

    # eliminar el cache de redis del survey con el id y pregunta con el question_id
    redis_db_service.delete_key(f"questions_encuesta_{id}")

    # eliminar el cache de redis de surveys
    redis_db_service.delete_key("surveys")

    # eliminar el cache del survey con el id
    redis_db_service.delete_key(f"survey_{id}")

    return mongo_db_service.eliminar_pregunta(encuesta, id_pregunta)

#Endpoints para las Respuestas de las Encuestas [Anthony]
@app.route('/surveys/<string:id>/responses', methods = ['POST'])
def post_response(id):
    encuesta= id
    respuestas = request.get_json()

    # eliminar el cache de redis de responses_encuesta con el id
    redis_db_service.delete_key(f"responses_encuesta_{id}")

    return mongo_db_service.enviar_respuestas(encuesta, respuestas)


#Autenticacion
@app.route('/surveys/<string:id>/responses', methods = ['GET'])
def get_responses(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id) 

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta= id

    # verificar si ya la consulta está en el cache de redis
    data = redis_db_service.get_key(f"responses_encuesta_{id}")
    if data is None:
        data = mongo_db_service.listar_respuestas(encuesta)
                    
        # guardar la consulta en el cache de redis
        redis_db_service.set_key(f"responses_encuesta_{id}", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire(f"responses_encuesta_{id}", 120)

        data = json_util.dumps(data)
    return data


#Endpoints para los encuestados 

#POST /respondents - Registra un nuevo encuestado.

@app.route('/respondents', methods=['POST'])
#implementar lo de seguridad con token
def register_respondent():
    respondent_data = request.get_json()
    if not respondent_data or 'name' not in respondent_data or 'email' not in respondent_data:
        return jsonify({'error': 'Missing name or email'}), 400
    
    try:
        result = postgre_db_service.insert_respondent(respondent_data)
        # eliminar el cache de redis de respondents
        redis_db_service.delete_key("respondents")

        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#GET /respondents - Obtiene todos los encuestados
@app.route('/respondents', methods=['GET'])
#@token_required
def list_respondents():
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        hasAccess = Security.verifyToken({"token" : token, "userType" : 2})
        if not hasAccess[0]:
            return jsonify({"message" : "You don't have permission"})
    
    # verificar si ya la consulta está en el cache de redis
    data = redis_db_service.get_key("respondents")
    if data is None:
        data = postgre_db_service.get_all_respondents()

        # guardar la consulta en el cache de redis
        redis_db_service.set_key("respondents", data) 
        # setear el tiempo de expiración
        redis_db_service.set_expire("respondents", 120) 
    return jsonify(data), 200


#GET /respondents/{id} - Obtiene el encuestado según el id
@app.route('/respondents/<int:id>', methods=['GET'])
#@token_required
def get_respondent(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        hasAccess = Security.verifyToken({"token" : token, "userType" : 2})
        if not hasAccess[0]:
            return jsonify({"message" : "You don't have permission"})
    
    # verificar si ya la consulta está en el cache de redis
    respondent = redis_db_service.get_key(f"respondent_{id}")
    if respondent is None:
        respondent = postgre_db_service.get_respondent_by_id(id)

        # guardar la consulta en el cache de redis
        redis_db_service.set_key(f"respondent_{id}", respondent) 
        # setear el tiempo de expiración
        redis_db_service.set_expire(f"respondent_{id}", 120) 

    if respondent:
        return jsonify(respondent), 200
    else:
        return jsonify({"error": "Respondent not found"}), 404


# PUT /respondents/{id} - Actualiza la información de un encuestado 
@app.route('/respondents/<int:id>', methods=['PUT'])
#@token_required
def update_respondent(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        hasAccess = Security.verifyToken({"token" : token, "userType" : 2})
        if not hasAccess[0]:
            return jsonify({"message" : "You don't have permission"})
    data = request.json
    updated_respondent = postgre_db_service.update_respondent(id, data)
    if updated_respondent:
        # eliminar el cache de redis del respondent con el id
        redis_db_service.delete_key(f"respondent_{id}")

        # eliminar el cache de redis de respondents
        redis_db_service.delete_key("respondents")

        return jsonify(updated_respondent), 200
    else:
        return jsonify({"error": "Unable to update respondent"}), 404


# DELETE /respondents/{id} - Elimina un encuestado de la base de datos
@app.route('/respondents/<int:id>', methods=['DELETE'])
#@token_required
def delete_respondent(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        hasAccess = Security.verifyToken({"token" : token, "userType" : 2})
        if not hasAccess[0]:
            return jsonify({"message" : "You don't have permission"})
    result = postgre_db_service.delete_respondent(id)
    if result:
        # eliminar el cache de redis del respondent con el id
        redis_db_service.delete_key(f"respondent_{id}")

        # eliminar el cache de redis de respondents
        redis_db_service.delete_key("respondents")

        return '', 204
    else:
        return jsonify({"error": "Respondent not found"}), 404


#Endpoint para los Reportes y Análisis [Dario - Preguntar acerca del analisis al profe]
@app.route('/surveys/<string:id>/analysis')
def get_analisis(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        # verificar si ya la consulta está en el cache de redis
        survey = redis_db_service.get_key(f"survey_{id}")
        if survey is None:
            survey = mongo_db_service.detalles_encuesta(id) 

            # agregar la consulta al cache de redis
            redis_db_service.set_key(f"survey_{id}", survey) 
            # setear el tiempo de expiración
            redis_db_service.set_expire(f"survey_{id}", 120) 

        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    encuesta= id
    return mongo_db_service.listar_respuestas(encuesta)

#Endpoints kafka
#Inicia sesión colaborativa
@app.route('/surveys/<string:id>/edit/start', methods = ['POST'])
def start_session(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        survey = mongo_db_service.detalles_encuesta(id) 
        if 'token' not in survey:
            return survey
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    id_to_search = id
    return kafka_service.start_session(id_to_search)

#Envia cambios al sistema
@app.route('/surveys/<string:id>/edit/submit', methods = ['POST']) 
def submit_changes_app(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        survey = mongo_db_service.detalles_encuesta(id) 
        if 'token' not in survey:
            return jsonify(survey), 403
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"}), 403
    id_to_search = id    
    cambios = request.get_json()
    autor = request.cookies.get("token")
    try:
        kafka_service.submit_changes(id_to_search, cambios, autor)
        return jsonify({"message" : "Cambios realizados"}), 200
    except Exception as e:
        return jsonify({"message" : f"Failed to submit changes: {str(e)}"}), 500

#Consulta el estado de los cambios
@app.route('/surveys/<string:id>/edit/status', methods = ['GET'])
def get_status_app(id):
    token = request.cookies.get("token")
    hasAccess = Security.verifyToken({"token" : token, "userType" : 1})
    if not hasAccess[0]:
        survey = mongo_db_service.detalles_encuesta(id) 
        if 'token' not in survey:
            return jsonify(survey), 403
        else:
            hasAccess = Security.verifyToken({"token" : survey["token"], "tokenKey" : token})
            if not hasAccess[0]:
                return jsonify({"message" : "You don't have permission"})
    id_to_search = id
    try:
        status = kafka_service.get_status(id_to_search)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"message" : f"Failed to get status: {str(e)}"}), 500
    
#Endpoint para el Dashboard 
@app.route('/dashboard-url')
def dashboard_url():
    dashboard_url = 'http://localhost:8088/superset/dashboard/p/w41lv7en7Xp/'
    return jsonify({'dashboard_url': dashboard_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)