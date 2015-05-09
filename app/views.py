from flask import Flask, jsonify, abort, g, request
from flask.ext.restful import Api, Resource, reqparse, marshal, fields
#from flask.ext.login import login_user, logout_user, current_user, login_required
from app import api, models, db, lm, app
from sqlalchemy.exc import IntegrityError

# TODO:
# - Do we need to replace the @login_required decorator with a custom one,
#   that checks the token given as a paramter?

def authorized(fn):
    """
    This decorator checks that an authorization token is found
    from the request headers, and fetches a user corresponding the token.

    Usage:

    @authorized
    def secured_root(userid=None):
        pass

    """

    def _wrap(*args, **kwargs):
        # 'Authorization'
        if 'token' not in request.headers:
            # 'token' not found in headers
            abort(401)
            return None

        token = request.headers["token"]
        u = models.User.verify_auth_token(token)

        if u:
            return fn(user=u, *args, **kwargs)

        # wrong token
        abort(401)
        return None

    return _wrap

@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))




# API views here
class UserAPI(Resource):

    def __init__(self):

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = unicode)
        self.reqparse.add_argument('note', type = unicode)
        self.reqparse.add_argument('lat', type = float)
        self.reqparse.add_argument('lon', type = float)
        self.reqparse.add_argument('email', type = unicode)
        self.reqparse.add_argument('password', type = unicode)

        self.allowed_user_fields = {
            'name': fields.String,
            'note': fields.String,
            'lat': fields.Float,
            'lon': fields.Float,
            'id' : fields.Integer
        }


        super(UserAPI, self).__init__()

    @authorized
    def get(self, id=None, user=None):
        """
            Returns user info.

            @param user : current user
            @param id   : id of the queried user

        """

        # TODO: this is for debugging. remove this.
        if not id:
            users = models.User.query.all()
            if users:
                #return jsonify(users = [u.as_dict() for u in users])
                return marshal(users, self.allowed_user_fields), 200
            else:
                return "No users found. Please create a user first.", 404

        u = models.User.query.get(int(id))

        if not u:
            return abort(404)

        #return jsonify(u.as_dict())
        return marshal(u, self.allowed_user_fields), 200

    @authorized
    def put(self, id, user=None):
        """
            Updates the user information
        """

        # TODO: check that the modified user is the same as the logged in user

        args = self.reqparse.parse_args()

        u = models.User.query.get(int(id))

        if not u:
            return abort(404)

        if args['name']:
            u.nickname = args['name']
        if args['note']:
            u.note = args['note']
        if args['lat']:
            u.lat = args['lat']
        if args['lon']:
            u.lon = args['lon']

        #db.session.add(u)
        db.session.commit()

        return u.id, 201


    def post(self):
        """
            Creates a new user with given args.
        """

        args = self.reqparse.parse_args()

        if not (("password" in args) and ("email" in args)):
            return "Password and username required", 400

        try:
            u = models.User(nickname=args['name'], lat=args['lat'], lon=args['lon'], note=args['note'], email=args['email'])
            u.set_pw_hash(args['password'])

            db.session.add(u)
            db.session.commit()
        except IntegrityError:
            return {"message" : "This email address is already registered."}, 409

        return u.id, 201

    @authorized
    def delete(self, id, user=None):
        """
            Deletes the user profile from the database.
        """

        # TODO: check that the user is owner

        u = models.User.query.get(id)
        if u:
            db.session.delete(u)
            db.session.commit()
            return '', 204
        return abort(404)


class LocationAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lat', type = float)
        self.reqparse.add_argument('lon', type = float)

        super(LocationAPI, self).__init__()

    ## TODO: update to user marshal isntead of u.as_dict!

    @authorized
    def get(self, user=None):
        """
            Returns a list of the nearby user id's according to given location
            the distance defaults to 1000 meters . (?dist=1000)

            NOTE: currently just returns all the users in the database :D
        """

        users = models.User.query.all()

        if users:
            return jsonify(locations = [u.as_dict() for u in users])

    @authorized
    def post(self, user=None):
        """
            Updates the signed in user's location.
        """
        if user:
            args = self.reqparse.parse_args()

            if args['lat']:
                user.lat = args['lat']
            if args['lon']:
                user.lat = args['lon']

            db.session.commit()

            return {"status": "Successfully updated location"}, 200


class LoginAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('token', type = unicode)
        self.reqparse.add_argument('email', type = unicode)
        self.reqparse.add_argument('password', type = unicode)

        super(LoginAPI, self).__init__()

    @authorized
    def get(self, user=None):
        # TODO: get the token of the logged in user's ID

        if user:
            token = user.generate_auth_token()
            return {'token': token}, 200
        else:
            return "Error!", 400

    def post(self):

        # This should be done over HTTPS!

        args = self.reqparse.parse_args()

        # try token-based authentication first
        if args["token"]:
            token = args["token"]

            # get the user from the token
            u = models.User.verify_auth_token(token)

            if u:
                return {'token': u.generate_auth_token()}, 200
            else:
                return "Authentication was not successful", 400

        # try email/password authentication
        elif args["email"] and args["password"]:
            email = args["email"]
            password = args["password"]

            u = models.User.query.filter_by(email=email).first()

            if u:
                if  u.check_pw_hash(password):
                    return {'token': u.generate_auth_token()}, 200
                else:
                    return "Authentication was not successful", 400

        return "Not enough parameters given", 400



## API routes here ##
api.add_resource(UserAPI, '/users/<int:id>', '/users/')
#api.add_resource(LocationAPI, '/location/<int:x>/<int:y>', '/location')
api.add_resource(LoginAPI, '/login')