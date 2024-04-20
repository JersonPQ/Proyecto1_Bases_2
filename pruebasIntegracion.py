import pytest
from flask import Flask, jsonify, request
from db_mongo_service import MongoDatabaseService
from db_postgre_service import PostgreDatabaseService


user_data = {"name": "testuser", "password": "testpass", "userRol": 1}
survey_data = {
    "titulo": "Encuesta sobre preferencias",
    "preguntas": [
        {"pregunta": "¿Cuál es su color favorito?", "opciones": ["Rojo", "Verde", "Azul"]},
        {"pregunta": "¿Cuál es su animal favorito?", "opciones": ["Perro", "Gato", "Conejo"]}
    ],
    "publicada": False
}

def create_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY='your_secret_key',
    )
    
    @app.route('/auth/register', methods=['POST'])
    def register():
        user = request.get_json()
        return jsonify(user), 201
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        user = request.get_json()
        return jsonify({"token": "dummytoken"}), 200
    
    @app.route('/surveys', methods=['POST'])
    def create_survey():
        survey = request.get_json()
        survey['publicada'] = False
        return jsonify(survey), 201
    
    @app.route('/surveys', methods=['GET'])
    def list_surveys():
        surveys = [survey_data]
        return jsonify(surveys), 200
    return app

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as test_client:
        yield test_client

# Pruebas
def test_user_registration(client):
    response = client.post('/auth/register', json=user_data)
    assert response.status_code == 201
    assert response.get_json()['name'] == user_data['name']

def test_user_login(client):
    response = client.post('/auth/login', json=user_data)
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_create_survey(client):
    response = client.post('/surveys', json=survey_data)
    assert response.status_code == 201
    assert response.get_json()['titulo'] == survey_data['titulo']

def test_list_surveys(client):
    response = client.get('/surveys')
    assert response.status_code == 200
    surveys = response.get_json()
    assert len(surveys) > 0 

