import psycopg2

class PostgreDatabase:
    def __init__(
            self, database: str ="db_name", host: str = "db_host",
            user: str = "db_user", password: str = "db_password", port: int = 5432
    ) -> None:
        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port
        )
    
    # ----------------- Consultas ----------------- #

    def query_prueba(self) -> list:
        cursor = self.conn.cursor()

        #query
        query = "SELECT * FROM users;"

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()

        return data
    
    # ----------------- AUTH ----------------- #
    def getUser(self, user: dict) -> dict:
        cursor = self.conn.cursor()

        #Query
        query = "SELECT name, userRol FROM users WHERE name = %s and password = %s;"

        cursor.execute(query, (user["name"], user["password"]))

        row = cursor.fetchone()
        cursor.close

        if row is None:
            return None
        return {"name" : row[0], "userRol" : row[1] }

    
    # ----------------- Inserciones ----------------- #
    
    def insert_user(self, user: dict) -> dict:
        cursor = self.conn.cursor()

        #query
        query = "INSERT INTO users (name, password, userRol) VALUES (%s, %s, %s);"

        cursor.execute(query, (user['name'], user['password'], user['userRol']))
        self.conn.commit()

        cursor.close()

        return user

    def getUsers(self):
        cursor = self.conn.cursor()

        #Query
        query = "SELECT * FROM users"

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [{"id": row[0], "name": row[1], "password": row[2], "UserRol" : row[3]} for row in rows]
    
    def getUserId(self, userId):
        cursor = self.conn.cursor()

        #Query
        query = "SELECT id, name, password, userRol FROM users WHERE id = %s;"
        cursor.execute(query, (userId,))

        row = cursor.fetchone()
        cursor.close
        if row is None:
            return {"message" : "User not found"} 
        return {"id" : row[0], "name" : row[1], "password" : row[2], "userRol" : row[3] }

    def updateUser(self, userId, data):
        cursor = self.conn.cursor()
        query = "UPDATE users SET name = %s, password = %s WHERE id = %s;"
        cursor.execute(query, (data['name'], data['password'], userId))
        self.conn.commit()
        updated_rows = cursor.rowcount
        cursor.close()
        return updated_rows > 0

    def deleteUser(self, userId):
        cursor = self.conn.cursor()
        query = "DELETE FROM users WHERE id = %s;"
        cursor.execute(query, (userId,))
        self.conn.commit()
        deleted_rows = cursor.rowcount
        cursor.close()
        return deleted_rows > 0
# ------------------ MÉTODOS ENCUESTADOS --------------


    #Insertar encuestado
    def insert_respondent(self, respondent_data):
        cursor = self.conn.cursor()
        query = "INSERT INTO respondents (name, email) VALUES (%s, %s) RETURNING id;"
        cursor.execute(query, (respondent_data['name'], respondent_data['email']))
        respondent_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return {"id": respondent_id, "name": respondent_data['name'], "email": respondent_data['email']}
    
    #Obtener encuestados
    def get_all_respondents(self):
        cursor = self.conn.cursor()
        query = "SELECT id, name, email FROM respondents;"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]

        #Método para Obtener un Encuestado Específico por ID
    def get_respondent_by_id(self, respondent_id):
        cursor = self.conn.cursor()
        query = "SELECT id, name, email FROM respondents WHERE id = %s;"
        cursor.execute(query, (respondent_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        else:
            return None

    #def ACtualizar info de encuesado
    def update_respondent(self, respondent_id, data):
        cursor = self.conn.cursor()
        query = "UPDATE respondents SET name = %s, email = %s WHERE id = %s RETURNING id;"
        cursor.execute(query, (data['name'], data['email'], respondent_id))
        self.conn.commit()
        updated_rows = cursor.rowcount
        cursor.close()
        return updated_rows > 0

    #Eliminar encuestados
    def delete_respondent(self, respondent_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM respondents WHERE id = %s RETURNING id;"
        cursor.execute(query, (respondent_id,))
        self.conn.commit()
        deleted_rows = cursor.rowcount
        cursor.close()
        return deleted_rows > 0

  
    
    
