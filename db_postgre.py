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
