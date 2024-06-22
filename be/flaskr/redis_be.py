import os

import redis

class Redis:
    def __init__(self, REDIS_HOST, REDIS_PORT):
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        except:
            raise Exception("Unable to connect to Redis")
        
    
    def get_redis_client(self):
        return self.redis_client
    

    def push_location(self, key_type, group_key, user_name, long, lat):
        try:
            self.redis_client.sadd(group_key, user_name)
            self.redis_client.geoadd(key_type, [long, lat, user_name])
        except:
            raise Exception("Unable to push location")
    

    def get_group_locations(self, group_key):
        location_directory = []
        for user_name in self.redis_client.smembers(group_key):
            location_directory.append({"user_name": user_name, "location": self.redis_client.geopos("person", user_name)[-1]})
        return location_directory
    

    def delete_location(self, group_key, user_name):
        try:
            self.redis_client.srem(group_key, user_name)
            self.redis_client.zrem("person", user_name)
        except:
            raise Exception("Unable to delete user")
