from flask import Flask, jsonify, abort, g
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import api, models, db, lm, app

# TODO:
# - Do we need to replace the @login_required decorator with a custom one,
#   that checks the token given as a paramter?

@app.before_request
def before_request():
    g.user = current_user

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
        super(UserAPI, self).__init__()

    @login_required
    def get(self, id=None):
        """
            Returns user info.
        """

        if not id:
            users = models.User.query.all()
            if users:
                return jsonify(users = [u.as_dict() for u in users])
            else:
                return "No users found. Please create a user first.", 404

        u = models.User.query.get(int(id))

        if not u:
            return abort(404)

        return jsonify(u.as_dict())

    @login_required
    def put(self, id):
        """
            Updates the user information
        """

        # TODO: check that the modified user is the same as the logged in user

        args = self.reqparse.parse_args()

        print "ARGUMENTS ------------------"
        print args

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

        u = models.User(nickname=args['name'], lat=args['lat'], lon=args['lon'], note=args['note'])
        db.session.add(u)
        db.session.commit()

        return u.id, 201

    @login_required
    def delete(self, id):
        """
            Deletes the user profile from the database.
        """

        # TODO: check that the user is an admin OR owner

        u = models.User.query.get(id)
        if u:
            db.session.delete(u)
            db.session.commit()
            return '', 204
        return abort(404)


class LocationAPI(Resource):

    @login_required
    def get(self):
        """
            Returns a list of the nearby user id's according to given location
            the distance defaults to 1000 meters . (?dist=1000)

            NOTE: currently just returns all the users in the database :D
        """

        users = models.User.query.all()

        if users:
            return jsonify(locations = [u.as_dict() for u in users])

    @login_required
    def post(self, x, y):
        """
            Updates the signed in user's location.
        """
        pass


class LogoutAPI(Resource):

    def get(self):
        logout_user()
        return "Successfully logged out.", 200

class LoginAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # UNICODE?
        #self.reqparse.add_argument('username', type = unicode)
        #self.reqparse.add_argument('password', type = unicode)
        self.reqparse.add_argument('token', type = unicode)
        super(LoginAPI, self).__init__()

    @login_required
    def get(self):
        # TODO: get the token of the logged in user's ID

        token = models.User.query.get(1).generate_auth_token()
        return {'token': token}, 200

    def post(self):
        #TODO: check for username / password validity

        args = self.reqparse.parse_args()

        #TEMP, replace with password authentication
        token = args["token"]
        user = models.User.verify_auth_token(token)

        if user:
            login_user(user)
            g.user = user
            #TODO: replace the ID
            return models.User.query.get(1).generate_auth_token(), 200

        return "Login was not successful", 400

# API routes here
api.add_resource(UserAPI, '/users/<int:id>', '/users/')
api.add_resource(LocationAPI, '/location/<int:x>/<int:y>', '/location')
api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')
