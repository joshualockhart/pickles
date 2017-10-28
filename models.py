from app import db
import datetime

class Element(db.Model):
    __tablename__ = 'elements'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def __init__(self, data):
        self.data = data
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return '[Element] <id : {}>, <data : {}>, <timestamp : {}'.format(self.id, self.data, str(self.timestamp))
