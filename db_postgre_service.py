from db_postgre import PostgreDatabase

class PostgreDatabaseService:
    def __init__(self, database: PostgreDatabase) -> None:
        self.database = database

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
    
    
