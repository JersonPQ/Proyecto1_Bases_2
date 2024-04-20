from redis import Redis

class RedisDB:
    def __init__(self, host: str = "localhost", port: int = 6379) -> None:
        self.client = Redis(host=host, port=port)
    
    # ----------------- Gets de Keys ----------------- #
    def get_key(self, key: str) -> str:
        return self.client.get(key)
    
    # ----------------- Sets de Keys ----------------- #
    def set_key(self, key: str, value: str) -> str:
        return self.client.set(key, value)
    
    # ----------------- Deletes de Keys ----------------- #
    def delete_key(self, key: str) -> int:
        return self.client.delete(key)
    
    # ----------------- Set tiempo de expiracion ----------------- #
    def set_expire(self, key: str, time: int) -> int:
        return self.client.expire(key, time)