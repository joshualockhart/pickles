from app import db
import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    sheets = db.relationship('Sheet', backref='sheetowner', lazy=True)
    def add_sheet(self, sheet):
        if isinstance(sheet, Sheet):
            self.sheets.append(sheet)
        else:
            raise TypeError("Attempted to add non-sheet, non-string object as a user's sheet!")

    def __repr__(self):
        return "[User] <id : {}>,  <username : {}>, <sheets: {}>".format(self.id, self.username, self.sheets)

    def to_json(self):
        return {"id":self.id, "username":self.username}

class Sheet(db.Model):
    __tablename__ = 'sheets'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    elements = db.relationship('Element', backref='elementowner', lazy=True)

    def add_element(self, element):
        if isinstance(element, Element):
            self.elements.append(element)
        else:
            raise TypeError("Attempted to add non-element object as an element of a sheet!")

    def __repr__(self):
        return "[Sheet] <id : {}>,  <name : {}>, <elements : {}>".format(self.id, self.name, self.elements)

    def to_json(self):
        return {"id":self.id, "owner_id":self.owner_id, "name":self.name}

class Element(db.Model):
    __tablename__ = 'elements'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    sheet_id = db.Column(db.Integer, db.ForeignKey('sheets.id'))

    def __init__(self, data):
        self.data = data
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return '[Element] <id : {}>, <data : {}>, <timestamp : {}'.format(self.id, self.data, str(self.timestamp))

    def to_json(self):
        return {"id":self.id, "data":self.data, "timestamp":self.timestamp.isoformat()}
