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
    
 

    # ----------------- Inserciones ----------------- #
    
    def insert_user(self, user: dict) -> dict:
        cursor = self.conn.cursor()

        #query
        query = "INSERT INTO users (name, password) VALUES (%s, %s);"

        cursor.execute(query, (user["name"], user["password"]))
        self.conn.commit()

        cursor.close()

        return user



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

  
    
    
