from db_neo4j import Neo4jDataBase

class Neo4jDataBaseService:
    def __init__(self, database: Neo4jDataBase) -> None:
        self.database = database

    #------------------Inserciones------------------------
    def insertUser(self, user):
        return self.database.insertUser(user)
    
    def insertSurvey(self, survey, idSurvey):
        return self.database.insertSurvey(survey, idSurvey)
    
    def insertInsertManyQuestion(self, questions, idSurvey):
        return self.database.insertManyQuestions(questions, idSurvey)
    
    def insertQuestion(self, question, idSurvey):
        return self.database.insertQuestion(question, idSurvey)
    
    def inserAnswer(self, answer, surverId, userId):
        return self.database.insertAnswer(answer, surverId, userId)