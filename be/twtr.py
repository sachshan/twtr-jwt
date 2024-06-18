from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, abort
from flask_cors import CORS
#from flask_api import status
import http
from datetime import date, datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse
import pytz
import os
import sys
import time
import uuid
import json
import random
import string
import pathlib
import io
from uuid import UUID
from bson.objectid import ObjectId

# straight mongo access
from pymongo import MongoClient

# security
# pip install flask-bcrypt
# https://pypi.org/project/Bcrypt-Flask/
# https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/
#from flask.ext.bcrypt import Bcrypt
from flask_bcrypt import Bcrypt
from flask import g
import jwt
g = dict()

# mongo
# mongo_client = MongoClient("mongodb://mongo:27017/")
mongo_client = MongoClient("mongodb+srv://sachdeva:2P0m0Yb5FYK7InvM@cluster0.5ngjycd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
class MyMongo(object):
    def __init__(self, db_name):
        self.db_name = db_name
     
    def __enter__(self):
        # 'client' is global created above
        self.db = mongo_client[self.db_name]
        return self.db
 
    def __exit__(self, p1, p2, p3):
        # do not close the global handle!
        #client.close()
        pass
    
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
tweets = dict()      

################
# Security
################
def set_env_var():
    global g
    if 'database_url' not in g:
        g['database_url'] = os.environ.get("DATABASE_URL", 'mongodb://localhost:27017/')
    if 'secret_key' not in g:
        g['secret_key'] = os.environ.get("SECRET_KEY", "my_precious_1869")
    if 'bcrypt_log_rounds' not in g:
        g['bcrypt_log_rounds'] = os.environ.get("BCRYPT_LOG_ROUNDS", 13)
    if 'access_token_expiration' not in g:
        g['access_token_expiration'] = os.environ.get("ACCESS_TOKEN_EXPIRATION", 900)
    if 'refresh_token_expiration' not in g:
        g['refresh_token_expiration'] = os.environ.get("REFRESH_TOKEN_EXPIRATION", 2592000)
    if 'users' not in g:
        users = os.environ.get("USERS", 'Elon Musk,Bill Gates,Jeff Bezos')
        print('users=', users)
        print('g.users=', list(users.split(',')))
        g['users'] = list(users.split(','))
        print('g.users=', g['users'])
    if 'passwords' not in g:
        passwords = os.environ.get("PASSWORDS", 'Tesla,Clippy,Blue Horizon')
        g['passwords'] = list(passwords.split(','))
        print("g['passwords']=", g['passwords'])
        # Once hashed, the value is irreversible. However in the case of 
        # validating logins a simple hashing of candidate password and 
        # subsequent comparison can be done in constant time. This helps 
        # prevent timing attacks.
        #g['password_hashes'] = list(map(lambda p: bcrypt.generate_password_hash(str(p), g['bcrypt_log_rounds']).decode('utf-8'), g['passwords']))
        g['password_hashes'] = []
        for p in g['passwords']:
            g['password_hashes'].append(bcrypt.generate_password_hash(p, 13).decode('utf-8'))
        print("g['password_hashes]=", g['password_hashes'])
        g['userids'] = list(range(0, len(g['users'])))
        print("g['userids]=", g['userids'])

def get_env_var(varname):
    #return g.pop(varname, None)
    global g
    return g[varname]

def encode_token(user_id, token_type):
    if token_type == "access":
        seconds = get_env_var("access_token_expiration")
    else:
        seconds = get_env_var("refresh_token_expiration")

    payload = {
        "exp": datetime.utcnow() + timedelta(seconds=seconds),
        "iat": datetime.utcnow(),
        "sub": user_id,
    }
    return jwt.encode(
        payload, get_env_var("secret_key"), algorithm="HS256"
    )

def decode_token(token):
    #payload = jwt.decode(token, get_env_var("secret_key"))
    payload = jwt.decode(token, get_env_var("secret_key"), algorithms=["HS256"])
    print("decode_token:", payload)
    return payload["sub"]


####################
# Security Endpoints
####################
@app.route("/")
def home(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/tweets<br />
        http://localhost:5000/tweets-week<br />
        http://localhost:5000/tweets-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-tweets<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

@app.route("/doc")
def doc(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/tweets<br />
        http://localhost:5000/tweets-week<br />
        http://localhost:5000/tweets-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-tweets<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

# Returns an encoded userid as jwt access and a refresh tokens. Requires username 
# and password. Refresh token not used. Only meant to be used with token issuer,
# but here the token issuer and the be are one and the same.
@app.route("/login", methods=["POST"])
def login():
    try:
        user = request.json['name']
        password = request.json['password']
        print('user:', user)
        print('password:', password)
        print('users:', get_env_var('users'))
        if not user or not password:
            print('not user or not password!')
            return jsonify(("Authentication is required and has failed!", http.HTTPStatus.UNAUTHORIZED))
        elif not user in get_env_var('users'):
            print('unknown user!')
            return jsonify(("Unknown user!", http.HTTPStatus.UNAUTHORIZED))
        else:
            # presumably we only store password hashes and compare passed pwd
            # with our stored hash. For simplicity, we store the full password
            # and the hash, which we retrieve here
            print('password_hashes:', get_env_var('password_hashes'))
            print("get_env_var('users').index(user):", get_env_var('users').index(user))
            password_hash = get_env_var('password_hashes')[get_env_var('users').index(user)]
            print('password_hash:', password_hash)
            a = datetime.now()
            if not bcrypt.check_password_hash(password_hash, password):
                print('bcrypt.check_password_hash(password_hash, password) returned False!')
                return jsonify(("Authentication is required and has failed!", http.HTTPStatus.UNAUTHORIZEDD))
            b = datetime.now()
            print('check_password took:', b - a)
            # debugging
            #print('password:', password)
            #print('type(password):', type(password))
            #for i in range(3):
            #    password_hash2 = bcrypt.generate_password_hash(password, 13).decode('utf-8')
            #    print('password_hash2:', password_hash2)
            #    if not bcrypt.check_password_hash(password_hash2, password):
            #        print('bcrypt.check_password_hash(password_hash, password) returned False!')
            #        return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))

            # create access and refresh token for the user to save.
            # User needs to pass access token for all secured APIs.
            userid = get_env_var('userids')[get_env_var('users').index(user)]
            access_token = encode_token(userid, "access")
            refresh_token = encode_token(userid, "refresh")
            print('type(access_token):', type(access_token))
            #response_object = {
            #    "access_token": access_token.decode(),
            #    "refresh_token": refresh_token.decode(),
            #}
            response_object = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            #return response_object, 200
            #return response_object
            return jsonify((response_object, http.HTTPStatus.OK))
    except Exception as e:
        print('exception:', e)
        return jsonify(("Authentication is required and has failed!", http.HTTPStatus.UNAUTHORIZED))


# Returns an encoded userid. Requires both tokens. If access token expired 
# returns status.HTTP_401_UNAUTHORIZED, and user needs to fast login. If refresh 
# token expired returns status.HTTP_401_UNAUTHORIZED, and user needs to login
# with username and password. Tokens are usually passed in authorization headers 
# (auth_header = request.headers.get("Authorization")). For simplicity, I just 
# pass access token as an extra parameter in secured API calls.
@app.route("/fastlogin", methods=["POST"])
def fastlogin():
    try:
        access_token = request.json['access-token']
        refresh_token = request.json['refresh-token']

        if not access_token or not refresh_token:
            return jsonify(("Missing token(s)!", http.HTTPStatus.UNAUTHORIZED))
        else:
            try:
                # first, with access token:
                userid = decode_token(access_token)

                if not userid or not userid in get_env_var('userids'):
                    return jsonify(("User unknown, please login with username and password.", http.HTTPStatus.UNAUTHORIZED))

                try:
                    # second, with refresh token
                    userid2 = decode_token(refresh_token)

                    if not userid2 or userid2 != userid:
                        return jsonify(("User unknown, please login with username and password.", http.HTTPStatus.UNAUTHORIZED))

                    # issue a new access token, keep the same refresh token
                    access_token = encode_token(userid, "access")
                    response_object = {
                        "access_token": access_token.decode(),
                        "refresh_token": refresh_token,
                    }
                    return jsonify((response_object, http.HTTPStatus.OK))

                # refresh token failure: Need username/pwd login
                except jwt.ExpiredSignatureError:
                    return jsonify(("Lease expired. Please log in with username and password.", http.HTTPStatus.UNAUTHORIZED))
                
                except jwt.InvalidTokenError:
                    return jsonify(("Invalid token. Please log in with username and password.", http.HTTPStatus.UNAUTHORIZED))

            # access token failure: Need at least fast login
            except jwt.ExpiredSignatureError:
                return jsonify(("Signature expired. Please fast log in.", http.HTTPStatus.UNAUTHORIZED))
            
            except jwt.InvalidTokenError:
                return jsonify(("Invalid token. Please fast log in.", http.HTTPStatus.UNAUTHORIZED))

    except:
        return jsonify(("Missing token or other error. Please log in with username and password.", http.HTTPStatus.UNAUTHORIZED))


def verify_token(token):
    try:
        userid = decode_token(token)
        print("verify_token():", token, userid)
        print("verify_token():", get_env_var('userids'))
        print("verify_token():", userid in get_env_var('userids'))

        if userid is None or not userid in get_env_var('userids'):
            print("verify_token() returning False")
            return False, jsonify(("User unknown!", http.HTTPStatus.UNAUTHORIZED))
        else:
            print("verify_token() returning True")
            return True, userid

    except jwt.ExpiredSignatureError:
        return False, jsonify(("Signature expired. Please log in.", http.HTTPStatus.UNAUTHORIZED))

    except jwt.InvalidTokenError:
        return False, jsonify(("Invalid token. Please log in.", http.HTTPStatus.UNAUTHORIZED))


################
# Apply to mongo
################

def atlas_connect():
    # Node
    # const MongoClient = require('mongodb').MongoClient;
    # const uri = "mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
    # const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
    # client.connect(err => {
    # const collection = client.db("test").collection("devices");
    # // perform actions on the collection object
    # client.close();
    # });

    # Python
    client = pymongo.MongoClient("mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client.test


# database access layer
def insert_one(r):
    start_time = datetime.now()
    with MyMongo('tweets') as db:
        #start_time_db = datetime.now()
        #db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_one() to mongo: ", r)
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.insert_one(r)
            print("inserted _ids: ", result.inserted_id)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_one.")


def update_one(r):
    start_time = datetime.now()
    with MyMongo('tweets') as db:
        #start_time_db = datetime.now()
        #db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...update_one() to mongo: ", r)
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.update_one(
                {"_id" : r['_id']},
                {"$set": r},
                upsert=True)
            printg ("...update_one() to mongo acknowledged:", result.modified_count)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_one.")


def insert_many(r):
    start_time = datetime.now()
    with MyMongo('tweets') as db:
        #start_time_db = datetime.now()
        #db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.insert_many(r.values())
            print("inserted _ids: ", result.inserted_ids)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_many.")


def update_many(r):
    start_time = datetime.now()
    with MyMongo('tweets') as db:
        #start_time_db = datetime.now()
        #db = mongo_client['tweets']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        # much more complicated: use bulkwrite()
        # https://docs.mongodb.com/manual/reference/method/db.collection.bulkWrite/#db.collection.bulkWrite
        ops = []
        records = r
        print("...bulkwrite() to mongo: ", records)
        for one_r in records.values():
            op = dict(
                    replaceOne=dict(
                        filter=dict(
                            _id=one_r['_id']
                            ),
                        replacement=one_r,
                        upsert=True
                    )
            )
            ops.append(op)
        try:
            mongo_collection = db['tweets']
            result = mongo_collection.bulkWrite(ops, ordered=True)
            print("matchedCount: ", result.matchedCount)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_many.")


def tryexcept(requesto, key, default):
    lhs = None
    try:
        lhs = requesto.json[key]
        # except Exception as e:
    except:
        lhs = default
    return lhs

## seconds since midnight
def ssm():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return str((now - midnight).seconds)


##################
# Tweets Endpoints 
##################

# secured with jwt
# endpoint to create new tweet
@app.route("/tweet", methods=["POST"])
def add_tweet():
    user = request.json['user']
    description = request.json['description']
    private = request.json['private']
    pic = request.json['pic']

    # access_token = request.json['access-token']
    # print("access_token:", access_token)
    # permission = verify_token(access_token)
    # if not permission[0]: 
    #     print("tweet submission denied due to invalid token!")
    #     print(permission[1])
    #     return permission[1]
    # else:
    #     print('access token accepted!')

    tweet = dict(user=user, description=description, private=private,
                upvote=0, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                pic=pic, _id=str(ObjectId()))
    tweets[tweet['_id']] = tweet

    insert_one(tweet)
    print('tweet submitted:', tweet)
    return jsonify(tweet)

# endpoint to show all of today's tweets
@app.route("/tweets-day2", methods=["GET"])
def get_tweets_day2():
    todaystweets = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d"), 
                tweets.items())
    )
    return jsonify(todaystweets)

# endpoint to show all tweets 
@app.route("/tweets", methods=["GET"])
def get_tweets2():
    return jsonify(tweets)

# endpoint to show all of this week's tweets (any user)
@app.route("/tweets-week", methods=["GET"])
def get_tweets_week2():
    weekstweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7, 
                tweets.items())
    )
    return jsonify(weekstweets)

@app.route("/tweets-results", methods=["GET"])
def get_tweets_results():
    return json.dumps({"results":
        sorted(
            tweets.values(),
            key = lambda t: t['date']
        )
    })


@app.route("/tweets-week-results", methods=["GET"])
def get_tweets_week_results():
    weektweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return json.dumps({"results":
        sorted(
            [filter_tweet(k) for k in weektweets.keys()],
            key = lambda t: t['date']
        )
    })

# endpoint to show all of today's tweets (user-specific)
def filter_tweet(t):
    tweet = tweets[t]
    return dict(date=tweet['date'], description=tweet['description'], 
                private=tweet['private'], user=tweet['user'],
                upvote=tweet['upvote'] if 'upvote' in tweet else 0,
                pic=tweet['pic'])
@app.route("/tweets-user-day", methods=["POST"])
def get_tweets_user_day():
    user = request.json['user']
    todaystweets = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d") and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return jsonify(
        sorted(
            [filter_tweet(k) for k in todaystweets.keys()],
            key = lambda t: t['date']
        )
    )

# endpoint to show all of this week's tweets (user-specific)
@app.route("/tweets-user-week", methods=["POST"])
def get_tweets_user_week():
    user = request.json['user']
    weekstweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(weekstweets)
    return jsonify(
        sorted(
            [filter_tweet(k) for k in weekstweets.keys()],
            key = lambda t: t['date']
        )
    )


@app.route("/tweets-user-week-results", methods=["GET"])
def get_tweets_user_week_results():
    user = request.json['user']
    weektweets = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                tweets.items())
    )
    #return jsonify(todaystweets)
    return json.dumps({"results":
        sorted(
            [filter_tweet(k) for k in weektweets.keys()],
            key = lambda t: t['date']
        )
    })


# endpoint to get tweet detail by id
@app.route("/tweet/<id>", methods=["GET"])
def tweet_detail(id):
    return jsonify(tweets[id])


##################
# Apply from mongo
##################
def applyRecordLevelUpdates():
    return None

def applyCollectionLevelUpdates():
    global tweets
    with MyMongo('tweets') as db:
        #db = mongo_client['tweets']
        mongo_collection = db['tweets']

        cursor = mongo_collection.find({})
        records = list(cursor)

        howmany = len(records)
        print('found ' + str(howmany) + ' tweets!')
        sorted_records = sorted(records, key=lambda t: datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S'))
        #return json.dumps({"results": sorted_records })

        for tweet in sorted_records:
            tweets[tweet['_id']] = tweet


################################################
# Mock
################################################

# add new tweet, for testing
@app.route("/dbg-tweet", methods=["GET"])
def dbg_tweet():
    with app.test_client() as c:
        json_data = []
        name = ''.join(random.choices(string.ascii_lowercase, k=7))
        description = ''.join(random.choices(string.ascii_lowercase, k=50))
        print("posting..")
        rv = c.post('/tweet', json={
            'user': name, 'description': description,
            'private': False, 'pic': None
        })
    return rv.get_json()


# endpoint to mock tweets
@app.route("/mock-tweets", methods=["GET"])
def mock_tweets():

    # first, clear all collections
    global tweets
    tweets.clear()

    # create new data
    json_data_all = []
    with app.test_client() as c:
        
        # tweets: 30
        print("@@@ mock-tweets(): tweets..")
        json_data_all.append("@@@ tweets")            
        for i in range(30):
            description = []
            private = random.choice([True, False])
            for j in range(20):
                w = ''.join(random.choices(string.ascii_lowercase, k=random.randint(0,7)))
                description.append(w)
            description = ' '.join(description)
            u = ''.join(random.choices(string.ascii_lowercase, k=7))
            img_gender = random.choice(['women', 'men'])
            img_index = random.choice(range(100))
            img_url = 'https://randomuser.me/api/portraits/' + img_gender + '/' + str(img_index) + '.jpg'
            rv = c.post('/tweet', json={
                'user': u, 'private': private,
                'description': description, 'pic': img_url
            })
            #json_data.append(rv.get_json())
        json_data_all.append(tweets)

    # done!
    print("@@@ mock-tweets(): done!")
    return jsonify(json_data_all)


##################
# ADMINISTRATION #
##################

initialized = False
def initialize():
    global initialized
    if not initialized:
        set_env_var()
        applyCollectionLevelUpdates()
        initialized = True

# This runs once before the first single request
# Used to bootstrap our collections
#@app.before_first_request
#def before_first_request_func():
#    set_env_var()
#    applyCollectionLevelUpdates()

@app.before_request
def before_request_func():
    initialize()
    applyRecordLevelUpdates()



############################
# INFO on containerization #
############################

# To containerize a flask app:
# https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
