import json
from bson import ObjectId
from pymongo import MongoClient

class MongoDB:
    def __init__(self, host: str = "localhost", port: int = 27017, usernamen: str = "root", password: str = "example") -> None:
        self.client = MongoClient(host=host, port=port, username=usernamen, password=password)
        self.db = self.client["encuestas"]
        self.respuestas_collection = self.db["respuestas"]
        
    # ----------------- Consultas de Encuestas ----------------- #
    #Crear una nueva encuesta
    def crear_encuesta(self, encuesta: dict, token: int) -> dict:
        #Agregar id usuario que crea la encuesta
        encuesta["token"] = token
        return self.respuestas_collection.insert_one(encuesta)
    
    #Listar todas las encuestas disponibles publicamente
    def listar_encuestas(self) -> list:
        return self.respuestas_collection.find({"publicada": True})
    
    #Muestra los detalles de una encuesta especifica
    def detalles_encuesta(self, id: str) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            return survey
        else:
            return {"message": "Encuesta no encontrada"}
         
    #Actualizar los detalles de una encuesta especifica
    def actualizar_encuesta(self, id: str, encuesta: dict) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            self.respuestas_collection.update_one({"_id": survey_id}, {"$set": encuesta})
            return {"message": "Encuesta actualizada"}
        else:
            return {"message": "Encuesta no encontrada"}
        
    
    #Eliminar una encuesta especifica
    def eliminar_encuesta(self, id: str) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            self.respuestas_collection.delete_one({"_id": survey_id})
            return {"message": "Encuesta eliminada"}
        else:
            return {"message": "Encuesta no encontrada"}
    
    #Publicar una encuesta para hacerla accesible a los usuarios
    def publicar_encuesta(self, id: str) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            update = self.respuestas_collection.update_one({"_id": survey_id}, {"$set": {"publicada": True}})
            if update.modified_count == 1:
                return {"message": "Encuesta publicada"}
            else:
                return {"message": "Encuesta ya publicada o no encontrada"}
        else:
            return {"message": "Encuesta no encontrada"}
    #----------------- Consultas de Preguntas ----------------- #
    #Agregar preguntas a una encuesta especifica
    def agregar_preguntas(self, id: str, preguntas: list) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            self.respuestas_collection.update_one({"_id": survey_id}, {"$push": {"preguntas": preguntas}})
            return {"message": "Preguntas agregadas"}
        else:
            return {"message": "Encuesta no encontrada"}
       
    #Listar las preguntas de una encuesta especifica
    def listar_preguntas(self, id: str) -> list:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id}, {"preguntas": 1})
        if survey:
            survey['_id'] = str(survey['_id'])
            return survey["preguntas"]
        else:
            return ["message", "Encuesta no encontrada"]
    
    #Actualiza una pregunta especifica
    def actualizar_pregunta(self, id: str, pregunta: dict, id_pregunta: str) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            survey['_id'] = str(survey['_id'])
            for question in survey["preguntas"]:
                if question["id_pregunta"] == id_pregunta:
                    question.update(pregunta)
                    
                    update_result = self.respuestas_collection.update_one({"_id": survey_id}, {"$set": {"preguntas": survey['preguntas']}})
                           
                    if update_result.modified_count == 1:
                        return {"message": "Pregunta actualizada exitosamente"}
                    else:
                        return {"message": "Error al actualizar la pregunta"}
            return {"message": "Pregunta no encontrada"}  
        else:
            return {"message": "Encuesta no encontrada"}
                
       
    #Eliminar una pregunta de una encuesta
    def eliminar_pregunta(self, id: str, id_pregunta: str) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            
            for question in survey["preguntas"]:
                if question["id_pregunta"] == id_pregunta:
                    survey["preguntas"].remove(question)
                    delete_result = self.respuestas_collection.update_one({"_id": survey_id}, {"$set": {"preguntas": survey['preguntas']}})
                    
                    if delete_result.modified_count == 1:
                        return {"message": "Pregunta eliminada exitosamente"}
                    else:
                        return {"message": "Pregunta no eliminada"}
            return {"message": "Pregunta no encontrada"}
        else:
            return {"message": "Encuesta no encontrada"}    
    #----------------- Consultas de Respuestas ----------------- #
    #Envia respuestas a una encuesta por parte de un encuestado
    def enviar_respuestas(self, id: str, respuestas: list) -> dict:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            
            update_result = self.respuestas_collection.update_one(
                {"_id": survey_id},
                {"$push": {"respuestas": {"$each": [respuestas]}}}
            )
            
            if update_result.modified_count == 1:
                return {"message": "Respuestas enviadas exitosamente"}
            else:
                return {"message": "Error al enviar las respuestas"}
        else:
            return {"message": "Encuesta no encontrada"}    
    #Lista todas las respuestas de una encuesta especifica
    def listar_respuestas(self, id: str) -> list:
        survey_id = ObjectId(id)
        survey = self.respuestas_collection.find_one({"_id": survey_id})
        if survey:
            return survey.get("respuestas", [])
        else:
            return ["message", "Encuesta no encontrada"]