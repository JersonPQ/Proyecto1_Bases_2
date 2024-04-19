import datetime
import jwt
import pytz

class Security():

    #Las claves para los tokens
    secret = ["normalKey", "adminKey", "createKey"]
    tz = pytz.timezone("America/Panama")

    @classmethod
    def generateTokem(cls, authUser):
        payload = {
            'iat' : datetime.datetime.now(tz=cls.tz),
            'exp' : datetime.datetime.now(tz=cls.tz) + datetime.timedelta(minutes=15),
            'username' : authUser['name'],
        }
        return jwt.encode(payload, cls.secret[authUser['userRol']], "HS256")
    
    @classmethod
    def verifyToken(cls, headers):
        if headers["token"]:
            encodedToken = headers["token"]
            if(len(encodedToken) > 0):
                try:
                    payload = jwt.decode(encodedToken, cls.secret[int(headers["userType"])], algorithms=["HS256"])
                    return [True, payload["username"]]
                except (jwt.ExpiredSignatureError):
                    return [False, "Token expirado"]
                except (jwt.InvalidSignatureError):
                    return [False, "Token incorrecto"]
        return [False, "No existe el token"]