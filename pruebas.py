import unittest
from flask import Flask
from unittest.mock import Mock

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
        
        
    
        
        
        
        

if __name__ == '__main__':
    unittest.main()

