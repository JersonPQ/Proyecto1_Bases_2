from pymongo import MongoClient

class MongoDB:
    def __init__(self, host: str = "localhost", port: int = 27017, usernamen: str = "root", password: str = "example") -> None:
        self.client = MongoClient(host=host, port=port, username=usernamen, password=password)
        self.db = self.client["encuestas"]
        self.respuestas_collection = self.db["respuestas"]
        
    # ----------------- Consultas de Encuestas ----------------- #
    #Crear una nueva encuesta
    def crear_encuesta(self, encuesta: dict) -> dict:
        return self.respuestas_collection.insert_one(encuesta)
    
    #Listar todas las encuestas disponibles publicamente
    def listar_encuestas(self) -> list:
        return self.respuestas_collection.find({"publicada": True})
    
    #Muestra los detalles de una encuesta especifica
    def detalles_encuesta(self, id: str) -> dict:
         flag = self.respuestas_collection.find_one({"_id": id})
         if flag:
                return flag
         else:
                return {"message": "Encuesta no encontrada"}
         
    #Actualizar los detalles de una encuesta especifica
    def actualizar_encuesta(self, id: str, encuesta: dict) -> dict:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.update_one({"_id": id}, {"$set": encuesta})
        else:
            return {"message": "Encuesta no encontrada"}
        
    
    #Eliminar una encuesta especifica
    def eliminar_encuesta(self, id: str) -> dict:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.delete_one({"_id": id})
        else:
            return {"message": "Encuesta no encontrada"}
    
    #Publicar una encuesta para hacerla accesible a los usuarios
    def publicar_encuesta(self, id: str) -> dict:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.update_one({"_id": id}, {"$set": {"publicada": True}})
        else:
            return {"message": "Encuesta no encontrada"}
    #----------------- Consultas de Preguntas ----------------- #
    #Agregar preguntas a una encuesta especifica
    def agregar_preguntas(self, id: str, preguntas: list) -> dict:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.update_one({"_id": id}, {"$push": {"preguntas": preguntas}})
        else:
            return {"message": "Encuesta no encontrada"}

    #Listar las preguntas de una encuesta especifica
    def listar_preguntas(self, id: str) -> list:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.find_one({"_id": id}, {"preguntas": 1})
        else:
            return ["message", "Encuesta no encontrada"]
    
    #Actualiza una pregunta especifica
    def actualizar_pregunta(self, id: str, pregunta: dict, id_pregunta: str) -> dict:
        flag1= self.respuestas_collection.find_one({"_id": id})
        flag2= self.respuestas_collection.find_one({"_id": id, "preguntas._id": id_pregunta})
        if flag1:
            if flag2:
                return self.respuestas_collection.update_one({"_id": id, "preguntas._id": id_pregunta}, {"$set": {"preguntas.$": pregunta}})
            else:    
                return {"message": "Pregunta no encontrada"}
        else:
            return {"message": "Encuesta no encontrada"}    
    #Eliminar una pregunta de una encuesta
    def eliminar_pregunta(self, id: str, id_pregunta: str) -> dict:
        flag1= self.respuestas_collection.find_one({"_id": id})
        flag2= self.respuestas_collection.find_one({"_id": id, "preguntas._id": id_pregunta})
        if flag1:
            if flag2:
                return self.respuestas_collection.update_one({"_id": id}, {"$pull": {"preguntas": {"_id": id_pregunta}}})
            else:
                return {"message": "Pregunta no encontrada"}
        else:
            return {"message": "Encuesta no encontrada"}    
    #----------------- Consultas de Respuestas ----------------- #
    #Envia respuestas a una encuesta por parte de un encuestado
    def enviar_respuestas(self, id: str, respuestas: list) -> dict:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.update_one({"_id": id}, {"$push": {"respuestas": respuestas}})
        else:
            return {"message": "Encuesta no encontrada"}    
    #Lista todas las respuestas de una encuesta especifica
    def listar_respuestas(self, id: str) -> list:
        flag= self.respuestas_collection.find_one({"_id": id})
        if flag:
            return self.respuestas_collection.find_one({"_id": id}, {"respuestas": 1})
        else:
            return ["message", "Encuesta no encontrada"]