from app import db
import datetime
from sqlalchemy.dialects.postgresql import JSON

class Element(db.Model):
    __tablename__ = 'elements'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def __init__(self, data):
        self.data = data
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return '<id {}>'.format(self.id)
