from db_neo4j import Neo4jDataBase

class Neo4jDataBaseService:
    def __init__(self, database: Neo4jDataBase) -> None:
        self.database = database

    #------------------Inserciones------------------------
    def insertUser(self, user):
        return self.database.insertUser(user)