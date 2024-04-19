from db_postgre import PostgreDatabase

class PostgreDatabaseService:
    def __init__(self, database: PostgreDatabase) -> None:
        self.database = database

    # ---------------Auth Users--------------------
    def insertUser(self, user):
        return self.database.insert_user(user)

    def getUser(self, userName, userPassword):
        return self.database.getUser({"name" : userName, "password" : userPassword})

    def getUsers(self):
        return self.database.getUsers()
    
    def getUserId(self, userId):
        return self.database.getUserId(userId)
    
    def updateUser(self, userId, data):
        return self.database.updateUser(userId, data)

    def deleteUser(self, userId):
        return self.database.deleteUser(userId)

    # ---------------Encuestados (Respondents)--------------------
    def insert_respondent(self, respondent_data):
        return self.database.insert_respondent(respondent_data)

    def get_all_respondents(self):
        return self.database.get_all_respondents()
    
    def get_respondent_by_id(self, respondent_id):
        return self.database.get_respondent_by_id(respondent_id)

    def update_respondent(self, respondent_id, respondent_data):
        return self.database.update_respondent(respondent_id, respondent_data)

    def delete_respondent(self, respondent_id):
        return self.database.delete_respondent(respondent_id)
    
    
