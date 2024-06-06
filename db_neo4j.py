from neo4j import GraphDatabase

class Neo4jDataBase:

    def __init__(self, user: str ="db_user", 
                password: str = "db_password", port: int = 7999) -> None:
        self.uri = "neo4j://localhost:" + str(port)
        self.authUser = user
        self.authPassword = password
    
    #-----------Inserciones-----------------------
    #Pasar los datos como diccionarios
    def insertUser (self, user : dict) -> dict:
        with GraphDatabase.driver(uri= self.uri, auth = (self.authUser, self.authPassword)) as driver:
            driver.verify_connectivity()
            driver.execute_query("CREATE (user : User {name:$name, userRol:$userRol})", {"name" : user['name'], "userRol" : user['userRol']})
        driver.close()
    
    def insertSurvey(self, survey: dict) -> None:
        None
        #Hacer lo logica para insertar información de encuesta

    def insertQuestion(self, question: dict) -> dict:
        None
        #Hacer la logica de insertar pregunta
    
    def insertAnswer(self, answer: dict) -> None:
        None #Hacer la logica para insertar respuesta
    
    #-----------Consultas-------------------------