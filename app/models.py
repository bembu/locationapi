from app import db, app
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

from werkzeug.security import generate_password_hash, \
     check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nickname = db.Column(db.String(64), index=True)
    note = db.Column(db.String(160), index=True)

    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(100))  # is the length always 66?

    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    ## for json serialization ##
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    ## for password hashing ##
    def set_pw_hash(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_pw_hash(self, password):
        return check_password_hash(self.pw_hash, password)

    ## functions for authentication ##
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
