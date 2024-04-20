from db_redis import RedisDB

class RedisDBService:
    def __init__(self, redis_databse: RedisDB) -> None:
        self.db = redis_databse
    
    # ----------------- Gets de Keys ----------------- #

    def get_key(self, key: str) -> str:
        return self.db.get_key(key)
    
    # ----------------- Sets de Keys ----------------- #
    def set_key(self, key: str, value: str) -> str:
        return self.db.set_key(key, value)
    
    # ----------------- Deletes de Keys ----------------- #
    def delete_key(self, key: str) -> int:
        return self.db.delete_key(key)
    
    # ----------------- Set tiempo de expiracion ----------------- #
    def set_expire(self, key: str, time: int) -> int:
        return self.db.set_expire(key, time)