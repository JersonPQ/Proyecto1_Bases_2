from db_mongo import MongoDB

class MongoDatabaseService:
    def __init__(self, database: MongoDB) -> None:
        self.database = database
    
    # ----------------- Consultas Encuestas ----------------- #
    def crear_encuesta(self, encuesta: dict) -> dict:
        return self.database.crear_encuesta(encuesta)
    
    def listar_encuestas(self) -> list:
        return self.database.listar_encuestas()
    
    def detalles_encuesta(self, id: str) -> dict:
        return self.database.detalles_encuesta(id)
    
    def actualizar_encuesta(self, id: str, encuesta: dict) -> dict:
        return self.database.actualizar_encuesta(id, encuesta)
    
    def eliminar_encuesta(self, id: str) -> dict:
        return self.database.eliminar_encuesta(id)
    
    def publicar_encuesta(self, id: str) -> dict:
        return self.database.publicar_encuesta(id)
    
    # ----------------- Consultas Preguntas ----------------- #
    def agregar_preguntas(self, id: str, preguntas: list) -> dict:
        return self.database.agregar_preguntas(id, preguntas)
    
    def listar_preguntas(self, id: str) -> list:
        return self.database.listar_preguntas(id)
    
    def actualizar_pregunta(self, id: str, pregunta: dict, id_pregunta:str) -> dict:
        return self.database.actualizar_pregunta(id, pregunta, id_pregunta)
    
    def eliminar_pregunta(self, id: str, id_pregunta: str) -> dict:
        return self.database.eliminar_pregunta(id, id_pregunta)
    
    # ----------------- Consultas Respuestas ----------------- #
    def enviar_respuestas(self, id: str, respuestas: list) -> dict:
        return self.database.enviar_respuestas(id, respuestas)
    
    def listar_respuestas(self, id: str) -> list:
        return self.database.listar_respuestas(id)