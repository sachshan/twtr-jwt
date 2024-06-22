import os

from flask import Flask

from .redis_be import Redis

def create_app():
    app = Flask(__name__)

    try:
        redis = Redis(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'))
    except:
        app.logger.error("Unable to connect to Redis")

    @app.route('/healthz', methods=['GET'])
    def get_server_health():
        if redis.get_redis_client().ping():
            return {'message': 'This system works'}, 200
        return {'message': 'Server not working'}, 500

    from flaskr.map.routes import map

    app.register_blueprint(map)
    return app