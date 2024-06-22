import os

from flask import Blueprint, jsonify, request, current_app
from flaskr.redis_be import Redis

map = Blueprint("map", __name__)

redis = Redis(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'))
rc = redis.get_redis_client()

@map.route('/v1/map/user', methods=['POST'])
def postUserLocation():
    data = request.get_json()
    try:
        redis.push_location("person", data['group_key'], data['name'], data['long'], data['lat'])
    except Exception as e:
        current_app.logger.error("Unable to push location: "+str(e))
        return {'message': str(e)}, 404
    return {'message': 'Location added'}, 201


@map.route('/v1/map/<group_key>', methods=['GET'])
def get_group_locations(group_key):
    return jsonify(redis.get_group_locations(group_key))


@map.route('/v1/map/user', methods=['DELETE'])
def deleteUserLocation():
    data = request.get_json()
    try:
        redis.delete_location(data['group_key'], data['name'])
    except:
        current_app.logger.error("Unable to delete user")
        return {'message': 'Unable to delete user'}, 404
    return {'message': 'User deleted'}, 200
