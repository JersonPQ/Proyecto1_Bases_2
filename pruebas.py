from unittest.mock import patch
import os
import unittest
from flask import Flask, jsonify, request, make_response
from db_postgre_service import PostgreDatabaseService
from db_mongo_service_test import MongoDatabaseService
from db_mongo_service_test import MongoDatabaseService
import os
from Security import Security
from pymongo import MongoClient
from bson import json_util
import unittest
import json
        
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY='your_secret_key',
        # Configuración de PostgreSQL
        POSTGRES_DB_NAME=os.getenv('POSTGRES_DB_NAME', 'fallback_db_name'),
        POSTGRES_DB_HOST=os.getenv('POSTGRES_DB_HOST', 'fallback_host'),
        POSTGRES_DB_USER=os.getenv('POSTGRES_DB_USER', 'fallback_user'),
        POSTGRES_DB_PASSWORD=os.getenv('POSTGRES_DB_PASSWORD', 'fallback_password'),
        POSTGRES_DB_PORT=int(os.getenv('POSTGRES_DB_PORT', 5432)),
        # Configuración de MongoDB
        MONGO_DB_USER=os.getenv('MONGO_DB_USER', 'root'),
        MONGO_DB_PASSWORD=os.getenv('MONGO_DB_PASSWORD', 'example'),
        MONGO_DB_HOST=os.getenv('MONGO_DB_HOST', 'localhost'),
        MONGO_DB_PORT=int(os.getenv('MONGO_DB_PORT', 27017)),
        MONGO_DB_NAME=os.getenv('MONGO_DB_NAME', 'encuestas')
    )

    # Inicialización de los servicios de las bases de datos
    mongo_db_service = MongoDatabaseService(database=app.config['MONGO_DB_NAME'])
    postgre_db_service = PostgreDatabaseService(database=app.config['POSTGRES_DB_NAME'])
    app.postgre_db_service = postgre_db_service
    app.mongo_db_service = mongo_db_service      
        
    #---------------------Autenticación y Autorización------------------------  
    @app.route('/auth/register', methods=['POST'])
    def register():
        user = request.json
        data = postgre_db_service.insertUser(user)
        return jsonify(data)
        
    @app.route('/auth/login', methods=['POST'])
    def login():
        user = request.json
        data = postgre_db_service.getUser(user["name"], user["password"])
        if data:
            token = Security.generateTokem(data)
            response = make_response(data)
            response.set_cookie("token", token)
            response.set_cookie("userType", str(data["userRol"]))
            return response
        else:
            return jsonify({"error": "Invalid credentials"}), 401
        
    @app.route('/auth/logout')
    def logout():
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        hasAccess = Security.verifyToken({"token": token, "userType": userType})
        if hasAccess[0]:
            response = make_response({"message": "Log out. Hasta pronto"})
            response.set_cookie("token", "", expires=0)
            return response
        return jsonify({"message": hasAccess[1]})

     #---------------------- Usuarios ----------------------------------
    @app.route('/users')
    def getUsers():
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        hasAccess = Security.verifyToken({"token": token, "userType": userType})
        if hasAccess[0]:
            data = postgre_db_service.getUsers()
            return jsonify(data)
        return jsonify({"message": hasAccess[1]})
    
    @app.route('/users/<int:id>')
    def getUser(id):
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        hasAccess = Security.verifyToken({"token": token, "userType": userType})
        if hasAccess[0]:
            data = postgre_db_service.getUserId(id)
            return jsonify(data)
        return jsonify({"message": hasAccess[1]})

    @app.route('/users/<int:id>', methods=['PUT'])
    def putUser(id):
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        if userType == "1":  # Admin check
            hasAccess = Security.verifyToken({"token": token, "userType": "1"})
        else:
            data = postgre_db_service.getUserId(id)
            if 'name' not in data:
                return jsonify({"message": "User not found"})
            hasAccess = Security.verifyToken({"token": token, "userType": userType})
            if data["name"] != hasAccess[1]:
                return jsonify({"message": "You don't have permission"})

        if hasAccess[0]:
            data = request.json
            updatedUser = postgre_db_service.updateUser(id, data)
            if updatedUser:
                return jsonify({"message": "Cambios realizados"})
            return jsonify({"message": "Cambios no realizados"})
        else:
            return jsonify({"message": hasAccess[1]})

    @app.route('/users/<int:id>', methods=['DELETE'])
    def deleteUser(id):
        token = request.cookies.get("token")
        hasAccess = Security.verifyToken({"token": token, "userType": "1"})
        if hasAccess[0]:
            response = postgre_db_service.deleteUser(id)
            if response:
                return jsonify({"message": "Usuario eliminado"}), 200
            return jsonify({"message": "Error al eliminar"}), 500
        return jsonify({"message": hasAccess[1]}), 403

    # -----------------------Encuestas------------------------------------------
    #1
    @app.route('/surveys', methods=['POST'])
    def post_encuesta():
        encuesta = request.get_json()
        resultado = mongo_db_service.crear_encuesta(encuesta)
        if resultado.acknowledged:
            return jsonify({"message": "Encuesta creada exitosamente", "id": str(resultado.inserted_id)}), 201
        else:
            return jsonify({"message": "Error al crear la encuesta"}), 400
        
    #2
    @app.route('/surveys', methods=['GET'])
    def get_surveys():
        surveys = [survey for survey in mongo_db_service.listar_encuestas()]
        surveys_json = json_util.dumps(surveys)
        return surveys_json, 200
        
    #3
    @app.route('/surveys/<int:id>', methods=['GET'])
    def get_survey(id):
        id_to_search = str(id) 
        survey_details = mongo_db_service.detalles_encuesta(id_to_search)
        if 'message' in survey_details:
            return jsonify(survey_details), 404 
        return jsonify(survey_details), 200
    #4
    @app.route('/surveys/<int:id>', methods=['PUT'])
    def put_survey(id):
        token = request.cookies.get("token")
        user_type = request.cookies.get("userType")
        has_access = Security.verifyToken({"token": token, "userType": user_type})
        
        if has_access[0]:
            encuesta = request.get_json()
            id_to_search = str(id) 
            update_result = mongo_db_service.actualizar_encuesta(id_to_search, encuesta)
            if isinstance(update_result, dict) and "message" in update_result:
                return jsonify(update_result), 404
            return jsonify({"message": "Encuesta actualizada"}), 200
        else:
            return jsonify({"message": "Acceso denegado"}), 403
    
        #5
    @app.route('/surveys/<int:id>', methods=['DELETE'])
    def delete_survey(id):
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        hasAccess = Security.verifyToken({"token": token, "userType": userType})
        
        if hasAccess[0]:
            id_to_search = str(id) 
            delete_result = mongo_db_service.eliminar_encuesta(id_to_search)
            if isinstance(delete_result, dict) and "message" in delete_result:
                return jsonify(delete_result), 404
            return jsonify({"message": "Encuesta eliminada"}), 200
        else:
            return jsonify({"message": "Acceso denegado"}), 403
    
    #6
    @app.route('/surveys/<int:id>/publish', methods=['POST'])
    def publish_survey(id):
        token = request.cookies.get("token")
        userType = request.cookies.get("userType")
        hasAccess = Security.verifyToken({"token": token, "userType": userType})
        
        if hasAccess[0]:
            id_to_search = str(id) 
            publish_result = mongo_db_service.publicar_encuesta(id_to_search)
            if isinstance(publish_result, dict) and "message" in publish_result:
                return jsonify(publish_result), 404
            return jsonify({"message": "Encuesta publicada exitosamente"}), 200
        else:
            return jsonify({"message": "Acceso denegado"}), 403
    
    # -----------------------Preguntas de Encuestas---------------------------
    
    #1
    @app.route('/surveys/<int:id>/questions', methods=['POST'])
    def post_question(id):
        pregunta = request.get_json()
        result = mongo_db_service.agregar_preguntas(str(id), pregunta) 
        if isinstance(result, dict) and "message" in result:
            return jsonify(result), 404  
        return jsonify({"message": "Preguntas agregadas correctamente"}), 201
    #2
    @app.route('/surveys/<int:id>/questions', methods=['GET'])
    def get_questions(id):
        questions = mongo_db_service.listar_preguntas(str(id)) 
        if isinstance(questions, list):
            return jsonify(questions), 200
        return jsonify({"message": "Encuesta no encontrada"}), 404
    #3
    @app.route('/surveys/<int:id>/questions/<int:question_id>', methods=['PUT'])
    def put_question(id, question_id):
        pregunta = request.get_json()
        resultado = mongo_db_service.actualizar_pregunta(str(id), pregunta, str(question_id))
        if isinstance(resultado, dict) and "message" in resultado:
            return jsonify(resultado), 404 if "no encontrada" in resultado["message"] else 400
        return jsonify({"message": "Pregunta actualizada"}), 200
    #4
    @app.route('/surveys/<int:id>/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(id, question_id):
        resultado = mongo_db_service.eliminar_pregunta(str(id), str(question_id))
        if isinstance(resultado, dict) and "message" in resultado:
            return jsonify(resultado), 404 if "no encontrada" in resultado["message"] else 400
        return jsonify({"message": "Pregunta eliminada"}), 200    

        
    # ----------Respuesta de Encuestas--------------------------
    @app.route('/surveys/<int:id>/responses', methods=['POST'])
    def post_response(id):
        encuesta = id
        respuestas = request.json
        return mongo_db_service.enviar_respuestas(encuesta, respuestas)
    
    @app.route('/surveys/<int:id>/responses', methods=['GET'])
    def get_responses(id):
        encuesta = id
        respuestas = app.mongo_db_service.listar_respuestas(encuesta)
        return jsonify(respuestas)
    #-----------------------Encuestados-------------------------------------
    @app.route('/respondents', methods=['GET'])
    def list_respondents():
        respondents = [{"id": 1, "name": "John Doe", "email": "john@example.com"}]
        return jsonify(respondents), 200
    
    @app.route('/respondents', methods=['POST'])
    def register_respondent():
        respondent_data = request.get_json()
        if not respondent_data or 'name' not in respondent_data or 'email' not in respondent_data:
            return jsonify({'error': 'Missing name or email'}), 400
        try:
            result = postgre_db_service.insert_respondent(respondent_data)
            return jsonify(result), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/respondents/<int:id>', methods=['GET'])
    def get_respondent(id):
        respondent = app.postgre_db_service.get_respondent_by_id(id)
        if respondent:
            return jsonify(respondent), 200
        else:
            return jsonify({"error": "Respondent not found"}), 404
        
    @app.route('/respondents/<int:id>', methods=['PUT'])
    def update_respondent(id):
        data = request.json
        updated_respondent = app.postgre_db_service.update_respondent(id, data)
        if updated_respondent:
            return jsonify({"success": "Respondent updated"}), 200
        else:
            return jsonify({"error": "Unable to update respondent"}), 404
        
    @app.route('/respondents/<int:id>', methods=['DELETE'])
    def delete_respondent(id):
        result = app.postgre_db_service.delete_respondent(id)
        if result:
            return '', 204
        else:
            return jsonify({"error": "Respondent not found"}), 404
        
        
    #------- ANÁLISIS -----------
    @patch('db_mongo_service.MongoDatabaseService.listar_respuestas')
    def test_get_survey_analysis(self, mock_listar_respuestas):
        mock_data = {'_id': '123', 'respuestas': [{'pregunta': '¿Qué piensas?', 'respuesta': 'Es bueno'}]}
        mock_listar_respuestas.return_value = mock_data
        response = self.client.get('/surveys/123/analysis')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), mock_data)
    return app
    

class TestApp(unittest.TestCase):
    def setUp(self):
        """Configurar la aplicación para pruebas."""
        self.app = create_app()
        self.client = self.app.test_client()
        
    #---------------------Autenticación y Autorización------------------------  
    @patch('db_postgre_service.PostgreDatabaseService.insertUser')
    def test_register_user(self, mock_insert_user):
        """Prueba la creación de un nuevo usuario."""
        
        user_data = {"name": "John Doe", "password": "secure123", "userRol": "admin"}
        mock_insert_user.return_value = user_data
        response = self.client.post('/auth/register', json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, user_data)
        
    @patch('db_postgre_service.PostgreDatabaseService.getUser')    
    @patch('Security.Security.generateTokem')
    def test_login(self, mock_generate_tokem, mock_get_user):
        """Prueba la autenticación de un usuario y la generación de un token."""
        user_data = {"name": "John Doe", "userRol": 1}
        mock_get_user.return_value = user_data
        mock_generate_tokem.return_value = "fake_token"
        login_data = {"name": "John Doe", "password": "secure123"}

        response = self.client.post('/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Set-Cookie', response.headers)
        cookies = response.headers.getlist('Set-Cookie')
        self.assertTrue(any("token=fake_token" in cookie for cookie in cookies))
        self.assertTrue(any("userType=1" in cookie for cookie in cookies))
        
      
    @patch('Security.Security.verifyToken')
    def test_logout(self, mock_verify_token):
        """Prueba el cierre de sesión del usuario."""
        mock_verify_token.return_value = [True, "John Doe"]
        with self.app.test_client() as client:
            client.set_cookie('token', 'valid_token')
            client.set_cookie('userType', '1')
            response = client.get('/auth/logout')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Log out. Hasta pronto"})
            self.assertIn('Set-Cookie', response.headers)
            cookies = response.headers.getlist('Set-Cookie')
            self.assertTrue(any("token=;" in cookie for cookie in cookies)) 

    # ------------------------- Usuarios ------------------------------------

    @patch('Security.Security.verifyToken')
    @patch('db_postgre_service.PostgreDatabaseService.getUsers')
    def test_get_users(self, mock_get_users, mock_verify_token):
        """Prueba la obtención de todos los usuarios cuando se tiene un token válido de administrador."""
        mock_verify_token.return_value = [True, "admin_user"]
        mock_get_users.return_value = [
            {"id": 1, "name": "John Doe", "password": "secure123", "UserRol": "admin"},
            {"id": 2, "name": "Jane Doe", "password": "secure456", "UserRol": "user"}
        ]
        with self.client as client:
            client.set_cookie('token', 'valid_token')
            client.set_cookie('userType', '1')
            response = client.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [
                {"id": 1, "name": "John Doe", "password": "secure123", "UserRol": "admin"},
                {"id": 2, "name": "Jane Doe", "password": "secure456", "UserRol": "user"}
            ])

    @patch('Security.Security.verifyToken')
    @patch('db_postgre_service.PostgreDatabaseService.getUserId')
    def test_get_user_by_id(self, mock_get_user_id, mock_verify_token):
        """Prueba la obtención de un usuario específico cuando se tiene un token válido de administrador."""
        mock_verify_token.return_value = [True, "admin_user"]
        user_id = 1
        mock_get_user_id.return_value = {"id": user_id, "name": "John Doe", "password": "secure123", "userRol": "admin"}
        with self.client as client:
            client.set_cookie('token', 'valid_token')
            client.set_cookie('userType', '1')
            response = client.get(f'/users/{user_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"id": user_id, "name": "John Doe", "password": "secure123", "userRol": "admin"})


    @patch('Security.Security.verifyToken')
    @patch('db_postgre_service.PostgreDatabaseService.getUserId')
    @patch('db_postgre_service.PostgreDatabaseService.updateUser')
    def test_put_user(self, mock_update_user, mock_get_user_id, mock_verify_token):
        """Prueba la actualización de un usuario por un usuario administrador."""
        mock_verify_token.return_value = [True, "admin_user"]
        user_id = 1
        user_data = {"name": "John Doe", "password": "new_secure123"}
        mock_get_user_id.return_value = {"id": user_id, "name": "John Doe", "password": "secure123"}
        mock_update_user.return_value = True
        with self.client as client:
            client.set_cookie('token', 'valid_token')
            client.set_cookie('userType', '1')
            response = client.put(f'/users/{user_id}', json=user_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Cambios realizados"})
            



    @patch('Security.Security.verifyToken')
    @patch('db_postgre_service.PostgreDatabaseService.deleteUser')
    def test_delete_user(self, mock_delete_user, mock_verify_token):
        """Prueba la eliminación de un usuario administrador."""
        mock_verify_token.return_value = [True, "admin_user"]
        user_id = 1
        mock_delete_user.return_value = True
        with self.client as client:
            client.set_cookie('token', 'valid_token')
            client.set_cookie('userType', '1')
            response = client.delete(f'/users/{user_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Usuario eliminado"})


    # -----------------------Encuestas------------------------------------------
    #1
    @patch('db_mongo_service.MongoDatabaseService.crear_encuesta')
    def test_post_encuesta(self, mock_crear_encuesta):
        resultado_mock = type('Mock', (object,), {"acknowledged": True, "inserted_id": "abc123"})
        mock_crear_encuesta.return_value = resultado_mock
        encuesta_data = {
            "titulo": "Encuesta de Satisfacción",
            "descripcion": "Una encuesta sobre la satisfacción del servicio."
        }

        response = self.client.post('/surveys', json=encuesta_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "Encuesta creada exitosamente", "id": "abc123"})
    #2
    @patch('db_mongo_service.MongoDatabaseService.listar_encuestas')
    def test_get_surveys(self, mock_listar_encuestas):
        mock_listar_encuestas.return_value = [
            {"_id": "1", "title": "Encuesta 1", "publicada": True},
            {"_id": "2", "title": "Encuesta 2", "publicada": True}
        ]
        response = self.client.get('/surveys')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], "Encuesta 1")
        self.assertEqual(data[1]['title'], "Encuesta 2")
        
        
     #3   
    @patch('db_mongo_service.MongoDatabaseService.detalles_encuesta')
    def test_get_survey(self, mock_detalles_encuesta):
        mock_detalles_encuesta.return_value = {
            "_id": "1",
            "title": "Survey on IT",
            "description": "A survey about IT preferences and experiences."
        }

        response = self.client.get('/surveys/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['title'], "Survey on IT")
        mock_detalles_encuesta.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.get('/surveys/999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Encuesta no encontrada")
    #4
    @patch('db_mongo_service.MongoDatabaseService.actualizar_encuesta')
    @patch('Security.Security.verifyToken')
    def test_put_survey(self, mock_verify_token, mock_actualizar_encuesta):
        """Test updating a specific survey by its ID."""
        mock_verify_token.return_value = [True, "admin"]
        update_result = {"acknowledged": True, "modified_count": 1}
        mock_actualizar_encuesta.return_value = update_result
        
        survey_data = {"title": "Updated Survey", "description": "Updated Description"}
        response = self.client.put('/surveys/1', json=survey_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Encuesta actualizada"})
        mock_verify_token.return_value = [False, "Acceso denegado"]
        response = self.client.put('/surveys/1', json=survey_data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"message": "Acceso denegado"})
    #5
    @patch('db_mongo_service.MongoDatabaseService.eliminar_encuesta')
    @patch('Security.Security.verifyToken')
    def test_delete_survey(self, mock_verify_token, mock_eliminar_encuesta):
        """Test deleting a specific survey by its ID."""
        mock_verify_token.return_value = [True, "admin"]
        delete_result = {"acknowledged": True, "deleted_count": 1}
        mock_eliminar_encuesta.return_value = delete_result
        response = self.client.delete('/surveys/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Encuesta eliminada"})
        mock_verify_token.return_value = [False, "Acceso denegado"]
        response = self.client.delete('/surveys/1')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"message": "Acceso denegado"})
        mock_verify_token.return_value = [True, "admin"]
        mock_eliminar_encuesta.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.delete('/surveys/2')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})
 #6
    @patch('db_mongo_service.MongoDatabaseService.publicar_encuesta')
    @patch('Security.Security.verifyToken')
    def test_publish_survey(self, mock_verify_token, mock_publicar_encuesta):
        mock_verify_token.return_value = [True, "admin"]
        update_result = {"acknowledged": True, "modified_count": 1}
        mock_publicar_encuesta.return_value = update_result 
        response = self.client.post('/surveys/1/publish')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Encuesta publicada exitosamente"})
        mock_verify_token.return_value = [False, "Acceso denegado"]
        response = self.client.post('/surveys/1/publish')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"message": "Acceso denegado"})
        mock_verify_token.return_value = [True, "admin"]
        mock_publicar_encuesta.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.post('/surveys/2/publish')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})

    # -----------------------Preguntas de Encuestas---------------------------
        #1
    @patch('db_mongo_service.MongoDatabaseService.agregar_preguntas')
    def test_post_question(self, mock_agregar_preguntas):
        mock_agregar_preguntas.return_value = None  
        
        questions_data = [{"texto": "¿Qué piensas de nuestro servicio?"}]
        response = self.client.post('/surveys/1/questions', json=questions_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "Preguntas agregadas correctamente"})
        mock_agregar_preguntas.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.post('/surveys/2/questions', json=questions_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})
        
        #2
    @patch('db_mongo_service.MongoDatabaseService.listar_preguntas')
    def test_get_questions(self, mock_listar_preguntas):
        questions_mock = [{'question': 'What is your favorite color?'}]
        mock_listar_preguntas.return_value = questions_mock
        response = self.client.get('/surveys/1/questions')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, questions_mock)
        mock_listar_preguntas.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.get('/surveys/2/questions')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})
    #3
    @patch('db_mongo_service.MongoDatabaseService.actualizar_pregunta')
    def test_put_question(self, mock_actualizar_pregunta):
        """Test updating a specific question in a survey."""
        mock_actualizar_pregunta.return_value = {}
        question_data = {"content": "What is your updated question?"}
        response = self.client.put('/surveys/1/questions/100', json=question_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Pregunta actualizada"})
        mock_actualizar_pregunta.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.put('/surveys/2/questions/100', json=question_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})
        mock_actualizar_pregunta.return_value = {"message": "Pregunta no encontrada"}
        response = self.client.put('/surveys/1/questions/101', json=question_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Pregunta no encontrada"})   
    #4
    @patch('db_mongo_service.MongoDatabaseService.eliminar_pregunta')
    def test_delete_question(self, mock_eliminar_pregunta):
        """Test deleting a specific question in a survey."""
        mock_eliminar_pregunta.return_value = {}
        response = self.client.delete('/surveys/1/questions/100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Pregunta eliminada"})
        mock_eliminar_pregunta.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.delete('/surveys/2/questions/100')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})
        mock_eliminar_pregunta.return_value = {"message": "Pregunta no encontrada"}
        response = self.client.delete('/surveys/1/questions/101')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Pregunta no encontrada"}) 
    #5

    # -----------------------Respuesta de Encuestas--------------------------
    @patch('db_mongo_service.MongoDatabaseService.enviar_respuestas')
    def test_post_response(self, mock_enviar_respuestas):
        """Prueba el envío de respuestas a una encuesta por parte de un encuestado."""
        mock_enviar_respuestas.return_value = {"message": "Respuestas guardadas correctamente"}
        respuestas_data = [{"pregunta": "¿Cómo estás?", "respuesta": "Bien"}]
        response = self.client.post('/surveys/1/responses', json=respuestas_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Respuestas guardadas correctamente"})
        mock_enviar_respuestas.return_value = {"message": "Encuesta no encontrada"}
        response = self.client.post('/surveys/999/responses', json=respuestas_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})

    @patch('db_mongo_service.MongoDatabaseService.listar_respuestas')
    def test_get_responses(self, mock_listar_respuestas):
        """Prueba la obtención de todas las respuestas de una encuesta específica."""
        mock_listar_respuestas.return_value = [{"pregunta": "¿Cómo estás?", "respuesta": "Bien"}]
        response = self.client.get('/surveys/1/responses')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"pregunta": "¿Cómo estás?", "respuesta": "Bien"}])

    #-----------------------Encuestados-------------------------------------
    @patch('db_postgre_service.PostgreDatabaseService.get_all_respondents')
    def test_list_respondents(self, mock_get_all_respondents):
        """Prueba el endpoint para obtener todos los encuestados."""

        mock_data = [{"id": 1, "name": "John Doe", "email": "john@example.com"}]

        mock_get_all_respondents.return_value = mock_data

        response = self.client.get('/respondents')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_data)
        
    @patch('db_postgre_service.PostgreDatabaseService.insert_respondent')
    def test_register_respondent(self, mock_insert_respondent):
        """Prueba el registro de un nuevo encuestado."""
        mock_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        mock_insert_respondent.return_value = mock_data
        response = self.client.post('/respondents', json={"name": "John Doe", "email": "john@example.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, mock_data)
        response = self.client.post('/respondents', json={"name": "John Doe"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing name or email'})
        mock_insert_respondent.side_effect = Exception("Database error")
        response = self.client.post('/respondents', json={"name": "Jane Doe", "email": "jane@example.com"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {'error': 'Database error'})
           
    @patch('db_postgre_service.PostgreDatabaseService.get_respondent_by_id')
    def test_get_respondent_by_id(self, mock_get_respondent_by_id):
        """Prueba la obtención de detalles de un encuestado específico."""
        mock_respondent = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        mock_get_respondent_by_id.return_value = mock_respondent
        response = self.client.get('/respondents/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_respondent)
        mock_get_respondent_by_id.return_value = None
        response = self.client.get('/respondents/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Respondent not found"})
    
    @patch('db_postgre_service.PostgreDatabaseService.update_respondent')
    def test_update_respondent(self, mock_update_respondent):
        """Prueba la actualización de la información de un encuestado."""
        mock_update_respondent.return_value = True
        updated_data = {"name": "Jane Doe", "email": "jane@example.com"}
        response = self.client.put('/respondents/1', json=updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": "Respondent updated"})
        mock_update_respondent.return_value = False
        response = self.client.put('/respondents/999', json=updated_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Unable to update respondent"})

    @patch('db_postgre_service.PostgreDatabaseService.delete_respondent')
    def test_delete_respondent(self, mock_delete_respondent):
        """Prueba la eliminación de un encuestado de la base de datos."""
        mock_delete_respondent.return_value = True
        response = self.client.delete('/respondents/1')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b'')
        mock_delete_respondent.return_value = False
        response = self.client.delete('/respondents/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Respondent not found"})


if __name__ == '__main__':
    unittest.main()