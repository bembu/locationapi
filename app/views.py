from flask import Flask, jsonify, abort
from flask.ext.restful import Api, Resource, reqparse
from app import api, models, db

# API views here
class UserAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = unicode)
        self.reqparse.add_argument('note', type = unicode)
        self.reqparse.add_argument('lat', type = float)
        self.reqparse.add_argument('lon', type = float)
        super(UserAPI, self).__init__()

    def get(self, id):
        """
            Returns user info.
        """

        u = models.User.query.get(int(id))

        if not u:
            return abort(404)

        return jsonify(u.as_dict())


    def put(self, id):
        """
            Updates the user information
        """

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

        print "ARGUMENTS ------------------"
        print args['note']

        u = models.User(nickname=args['name'], lat=args['lat'], lon=args['lon'], note=args['note'])
        db.session.add(u)
        db.session.commit()

        return u.id, 201

    def delete(self, id):
        """
            Deletes the user profile from the database.
        """

        u = models.User.query.get(id)
        if u:
            db.session.delete(u)
            db.session.commit()
            return '', 204
        return abort(404)


class LocationAPI(Resource):

    def get(self):
        """
            Returns a list of the nearby user id's according to given location
            the distance defaults to 1000 meters . (?dist=1000)

            NOTE: currently just returns all the users in the database :D
        """

        users = models.User.query.all()

        if users:
            return jsonify(json_list = [u.as_dict() for u in users])


    def post(self, x, y):
        """
            Updates the signed in user's location.
        """
        pass


class AuthenticationAPI(Resource):
    """
        Handles the user authentication.
    """
    def get(self):
        return {'token': 'X12391239ushda9dajq19qWFQ")#hw2l3ihtw283rhf'}


# API routes here
api.add_resource(UserAPI, '/users/<int:id>', '/users/')
api.add_resource(LocationAPI, '/location/<int:x>/<int:y>', '/location')
api.add_resource(AuthenticationAPI, '/auth')
