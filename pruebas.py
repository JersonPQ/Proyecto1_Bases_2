import unittest
from flask import Flask
from unittest.mock import Mock
from db_postgre import *
from db_mongo_service import *
from app import *
import json

app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, World!'

class TestFlaskApi(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()  
        self.app.testing = True  

    def test_home(self):
        response = self.app.get('/')  
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')  
    
    
    #Pruebas unitarias encuestados (respondents)
    def test_insert_respondent(self, mock_insert):
        mock_insert.return_value = {"id": 1, "name": "John Doe", "email": "johndoe@example.com"}
        respondent_data = json.dumps({
            "name": "John Doe",
            "email": "johndoe@example.com"
        })
    
        response = self.app.post('/respondents', data=respondent_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data), {"id": 1, "name": "John Doe", "email": "johndoe@example.com"})
        mock_insert.assert_called_once_with({"name": "John Doe", "email": "johndoe@example.com"})

       
       

if __name__ == '__main__':
    unittest.main()

