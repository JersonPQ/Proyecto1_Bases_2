from neo4j import GraphDatabase

class Neo4jDataBase:        
        def __init__(self, user: str ="db_user", 
                    password: str = "db_password", port:int = 7687) -> None:
            self.uri = "neo4j://172.24.0.1:" + str(port)
            self.authUser = user
            self.authPassword = password

        #-----------Inserciones-----------------------
        #Pasar los datos como diccionarios
        def insertUser (self, user : dict) -> dict:
            with GraphDatabase.driver(uri= self.uri, auth = (self.authUser, self.authPassword)) as driver:
                driver.verify_connectivity()
                driver.execute_query("CREATE (user : User {name:$name, userRol:$userRol})", {"name" : user['name'], "userRol" : user['userRol']})
            driver.close()
            return user

        def insertSurvey(self, survey: dict, idSurvey) -> None:
            with GraphDatabase.driver(uri=self.uri, auth= (self.authUser, self.authPassword)) as driver:
                driver.verify_connectivity()
                driver.execute_query("CREATE (survey : Survey {idSurvey:$idSurvey, title:$title})", {"idSurvey":idSurvey, "title":survey['titulo']})
            driver.close()
            return self.insertManyQuestions(survey['preguntas'], idSurvey)
            #Hacer lo logica para insertar información de encuesta

        #Voy a pasar la lista de las preguntas para generar los grafos y despues crear las relaciones
        def insertManyQuestions(self, questions:list, idSurvey) -> list:
            for question in questions:
                with GraphDatabase.driver(uri=self.uri, auth=(self.authUser, self.authPassword)) as driver:
                    driver.verify_connectivity()
                    driver.execute_query("CREATE (question : Question {idPregunta:$idPregunta, pregunta:$pregunta})", {"idPregunta" : question['id_pregunta'], "pregunta" : question['pregunta']})
                    driver.execute_query("MATCH (survey : Survey {idSurvey:$idSurvey}) MATCH (question : Question {idPregunta:$idPregunta}) CREATE (survey)-[:PREGUNTA]->(question)", {"idSurvey" : idSurvey, "idPregunta" : question['id_pregunta']})
            driver.close()
            return questions

        def insertQuestion(self, question: dict, idSurvey) -> dict:
            with GraphDatabase.driver(uri=self.uri, auth=(self.authUser, self.authPassword)) as driver:
                driver.verify_connectivity()
                driver.execute_query("CREATE (question : Question {idPregunta:$idPregunta, pregunta:$pregunta})", {"idPregunta" : question['id_pregunta'], "pregunta" : question['pregunta']})
                driver.execute_query("MATCH (survey : Survey {idSurvey:$idSurvey}) MATCH (question : Question {idPregunta:$idPregunta}) CREATE (survey)-[:PREGUNTA]->(question)", {"idSurvey" : idSurvey, "idPregunta" : question['id_pregunta']})
            driver.close()
            return question
            #Hacer la logica de insertar pregunta

        def insertAnswer(self, answer: dict, surveyId, userId):
            with GraphDatabase.driver(uri=self.uri, auth=(self.authUser, self.authPassword)) as driver:
                driver.verify_connectivity()
                driver.execute_query("MATCH (encuesta : Survey {idSurvey:$idSurvey})-[:PREGUNTA]->(pregunta : Question {idPregunta:$idPregunta}) WITH pregunta CREATE (pregunta)-[:Respuesta]->(answer : Answer {respuesta:$respuesta}) WITH answer CREATE (user : User {userId:$userId})-[:Respondio]->(answer)", {"idSurvey":surveyId, "idPregunta" : answer['pregunta_id'], "userId" : userId})
            driver.close()
            return [answer, userId]
            #Hacer la logica para insertar respuesta


        #-----------Consultas-------------------------
