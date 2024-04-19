from unittest.mock import patch
import os
from dotenv import load_dotenv
import unittest
from flask import Flask, jsonify, request
from db_postgre_service import PostgreDatabaseService
from db_mongo_service import MongoDatabaseService
from flask import Flask
from db_mongo_service import MongoDBService
import os
load_dotenv() 

from pymongo import MongoClient


        
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY='your_secret_key',
        DATABASE=os.getenv('POSTGRES_DB_NAME', 'fallback_db_name'),
        DB_HOST=os.getenv('POSTGRES_DB_HOST', 'fallback_host'),
        DB_USER=os.getenv('POSTGRES_DB_USER', 'fallback_user'),
        DB_PASSWORD=os.getenv('POSTGRES_DB_PASSWORD', 'fallback_password'),
        DB_PORT=os.getenv('POSTGRES_DB_PORT', 5432),
        
        MONGO_DB_USER=os.getenv('MONGO_DB_USER', 'root'),
        MONGO_DB_PASSWORD=os.getenv('MONGO_DB_PASSWORD', 'example'),
        MONGO_DB_HOST=os.getenv('MONGO_DB_HOST', 'localhost'),
        MONGO_DB_PORT=int(os.getenv('MONGO_DB_PORT', 27017)),
        MONGO_DB_NAME=os.getenv('MONGO_DB_NAME', 'encuestas')
    )
    mongo_db_service = MongoDBService(
        host=app.config['MONGO_DB_HOST'],
        port=app.config['MONGO_DB_PORT'],
        usernamen=app.config['MONGO_DB_USER'],
        password=app.config['MONGO_DB_PASSWORD'],
        database_name=app.config['MONGO_DB_NAME']
    )
    app.mongo_db_service = mongo_db_service
    postgre_db_service = PostgreDatabaseService(database=app.config['DATABASE'])
    app.postgre_db_service = postgre_db_service
        
        
        
        
    #-----------------------Respuesta de Encuestas--------------------------
    @app.route('/surveys/<int:id>/responses', methods=['POST'])
    def post_response(id):
        encuesta = id
        respuestas = request.json
        return mongo_db_service.enviar_respuestas(encuesta, respuestas)
    #-----------------------Encuestados-------------------------------------
    @app.route('/respondents', methods=['GET'])
    def list_respondents():
        # Aquí se debería implementar la lógica de obtención de encuestados
        # Por ahora, simulamos que la función ya devuelve algunos datos
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

   

    return app

class TestApp(unittest.TestCase):
    def setUp(self):
        """Configurar la aplicación para pruebas."""
        self.app = create_app()
        self.client = self.app.test_client()

    #-----------------------Respuesta de Encuestas--------------------------
    @patch('db_mongo_service.MongoDBService.enviar_respuestas')
    def test_post_response(self, mock_enviar_respuestas):
        """Prueba el envío de respuestas a una encuesta por parte de un encuestado."""

        # Configura el mock para simular una operación exitosa
        mock_enviar_respuestas.return_value = {"message": "Respuestas guardadas correctamente"}

        # Datos de prueba
        respuestas_data = [{"pregunta": "¿Cómo estás?", "respuesta": "Bien"}]

        # Llamamos al endpoint con un ID de encuesta que existe
        response = self.client.post('/surveys/1/responses', json=respuestas_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Respuestas guardadas correctamente"})

        # Configura el mock para simular que la encuesta no se encuentra
        mock_enviar_respuestas.return_value = {"message": "Encuesta no encontrada"}

        # Llamamos al endpoint con un ID de encuesta que no existe
        response = self.client.post('/surveys/999/responses', json=respuestas_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"message": "Encuesta no encontrada"})

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

        # Datos correctos
        response = self.client.post('/respondents', json={"name": "John Doe", "email": "john@example.com"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, mock_data)

        # Datos faltantes
        response = self.client.post('/respondents', json={"name": "John Doe"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'Missing name or email'})

        # Manejo de excepción
        mock_insert_respondent.side_effect = Exception("Database error")
        response = self.client.post('/respondents', json={"name": "Jane Doe", "email": "jane@example.com"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {'error': 'Database error'})
        
        
    @patch('db_postgre_service.PostgreDatabaseService.get_respondent_by_id')
    def test_get_respondent_by_id(self, mock_get_respondent_by_id):
        """Prueba la obtención de detalles de un encuestado específico."""

        # Configura el mock para simular que se encuentra un encuestado
        mock_respondent = {"id": 1, "name": "John Doe", "email": "john@example.com"}
        mock_get_respondent_by_id.return_value = mock_respondent

        # Realiza la llamada al endpoint con un ID que existe
        response = self.client.get('/respondents/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_respondent)

        # Configura el mock para simular que no se encuentra el encuestado
        mock_get_respondent_by_id.return_value = None

        # Realiza la llamada al endpoint con un ID que no existe
        response = self.client.get('/respondents/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Respondent not found"})
    
    @patch('db_postgre_service.PostgreDatabaseService.update_respondent')
    def test_update_respondent(self, mock_update_respondent):
        """Prueba la actualización de la información de un encuestado."""

        # Configura el mock para simular una actualización exitosa
        mock_update_respondent.return_value = True
        updated_data = {"name": "Jane Doe", "email": "jane@example.com"}

        # Llamamos al endpoint con un ID que existe
        response = self.client.put('/respondents/1', json=updated_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"success": "Respondent updated"})

        # Configura el mock para simular un fracaso en la actualización
        mock_update_respondent.return_value = False

        # Llamamos al endpoint con un ID que no existe
        response = self.client.put('/respondents/999', json=updated_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Unable to update respondent"})


    @patch('db_postgre_service.PostgreDatabaseService.delete_respondent')
    def test_delete_respondent(self, mock_delete_respondent):
        """Prueba la eliminación de un encuestado de la base de datos."""

        # Configura el mock para simular una eliminación exitosa
        mock_delete_respondent.return_value = True

        # Llamamos al endpoint con un ID que existe
        response = self.client.delete('/respondents/1')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b'')

        # Configura el mock para simular que el encuestado no se encuentra
        mock_delete_respondent.return_value = False

        # Llamamos al endpoint con un ID que no existe
        response = self.client.delete('/respondents/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Respondent not found"})

if __name__ == '__main__':
    unittest.main()
