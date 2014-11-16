from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nickname = db.Column(db.String(64), index=True)
    note = db.Column(db.String(160), index=True)

    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    # for json serialization
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
