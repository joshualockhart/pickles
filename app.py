from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify, abort
import datetime
import dateutil.parser
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PICKLES_DATA_MAX_LENGTH'] = 10000

app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)

from models import *

MAX_DATA_LENGTH = app.config['PICKLES_DATA_MAX_LENGTH']



"""
================================================
                    ELEMENTS
================================================
TODO:
    add element YES
    get element YES
    modify element YES
    delete element YES
"""

def get_element(element_id):
    e = Element.query.filter_by(id=element_id).first()
    if e == None:
        raise ValueError("No element with id {}".format(element_id))
    return e

def get_elements_between_dates(start_date, end_date):
    elements = Element.query.filter(Element.timestamp.between(start_date, end_date)).all()
    return elements

def modify_element(element_id, data):
    try:
        element = get_element(element_id)
        element.data = data
        db.session.commit()
    except ValueError as ex:
        raise ex

def remove_element(element_id):
    try:
        e = get_element(element_id)
        db.session.delete(e)
        db.session.commit()
    except ValueError as ex:
        raise ex

@app.route('/addelement', methods=['POST'])
def _add_element():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "data" in keys and "sheet_id" in keys and len(keys) == 2:
            add_element(content.get("sheet_id"), content.get("data"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/removeelement', methods=['POST'])
def _remove_element():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            remove_element(content.get("id"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/modifyelement', methods=['POST'])
def _modify_element():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and "data" in keys and len(keys) == 2:
            modify_element(content.get("id"), content.get("data"))
            return 'OK'

    return 'BAD REQUEST'

@app.route('/getelement', methods=['POST'])
def _get_element():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            e = get_element(content.get("id"))
            return jsonify(e.to_json())

        elif "start_date" in keys and "end_date" in keys and len(keys) == 2:
            start_date = dateutil.parser.parse(content.get("start_date"))
            end_date = dateutil.parser.parse(content.get("end_date"))
            elements = get_elements_between_dates(start_date, end_date)
            return jsonify([e.to_json() for e in elements])

    return 'BAD REQUEST'

"""
================================================
                    SHEETS
================================================
TODO:
    add sheet YES
    get sheet:
        given <username> and <sheetname>, check that <username> owns <sheetname>
        given <sheetid> return elements of sheet <sheetid> YES
    modify sheet:
        change sheet name YES
    delete sheet YES

"""

def get_sheet(sheet_id):
    s = Sheet.query.filter_by(id=sheet_id).first()
    if s != None:
        return s
    raise ValueError("No sheet with id = {}".format(sheet_id))

def add_sheet(owner_id, name):
    s = Sheet(name=name)
    u = get_user(owner_id)
    u.add_sheet(s)
    db.session.commit()

def get_elements_of_sheet(sheet_id):
    s = get_sheet(sheet_id)
    if s != None:
        return s.elements
    raise ValueError("No sheet with id = {}".format(sheet_id))

def remove_sheet(sheet_id):
    try:
        sheet = get_element(sheet_id)
        db.session.delete(sheet)
        db.session.commit()
    except ValueError as ex:
        raise ex

def modify_sheet(sheet_id, name):
    try:
        sheet = get_sheet(sheet_id)
        sheet.name = name
        db.session.commit()
    except ValueError as ex:
        raise ex

@app.route('/getelementsofsheet', methods=['POST'])
def _get_elements_of_sheet():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            try:
                elements = get_elements_of_sheet(content.get("id"))
                return jsonify([e.to_json() for e in elements])
            except ValueError as ex:
                return str(ex)
    return 'BAD REQUEST'

@app.route('/addsheet', methods=['POST'])
def _add_sheet():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "name" in keys and "owner_id" in keys and len(keys) == 2:
            try:
                add_sheet(content.get("owner_id"), content.get("name"))
                return 'OK'
            except ValueError as ex:
                return str(ex)
    return 'BAD REQUEST'

@app.route('/removesheet', methods=['POST'])
def _remove_sheet():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            remove_sheet(content.get("id"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/modifysheet', methods=['POST'])
def _modify_sheet():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and "name" in keys and len(keys) == 2:
            modify_element(content.get("id"), content.get("name"))
            return 'OK'

    return 'BAD REQUEST'

"""
================================================
                    USERS
================================================
TODO:
    add user YES
    get user:
        given <username>, check if user exists YES
        given <userid> return sheets belonging to user <userid> YES
    modify user
    delete user YES
"""

def check_user_exists(username):
    u = User.query.filter_by(username=username).first()
    return u != None

def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if user != None:
        return user
    raise ValueError("No user with username '{}'".format(username))

def get_user(user_id):
    u = User.query.filter_by(id=user_id).first()
    if u != None:
        return u
    raise ValueError("No user with id = {}".format(user_id))

def get_sheets_of_user(user_id):
    u = get_user(user_id)
    if u != None:
        return u.sheets
    raise ValueError("No user with id = {}".format(user_id))

def add_user(username):
    if check_user_exists(username):
        raise ValueError("Username '{}' is taken!".format(username))
    else:
        u = User(username=username)
        db.session.add(u)
        db.session.commit()

def remove_user(user_id):
    try:
        user = get_user(user_id)
        db.session.delete(user)
        db.session.commit()
    except ValueError as ex:
        raise ex

def modify_user(user_id, username):
    try:
        user = get_user(user_id)
        user.username = username
        db.session.commit()
    except ValueError as ex:
        raise ex

@app.route('/getuserbyusername', methods=['POST'])
def _get_user_from_username():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "username" in keys and len(keys) == 1:
            try:
                user = get_user_by_username(content.get("username"))
                return jsonify(user.to_json())
            except ValueError as ex:
                abort(404)
    return 'BAD REQUEST'

@app.route('/getsheetsofuser', methods=['POST'])
def _get_sheets_of_user():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            try:
                sheets = get_sheets_of_user(content.get("id"))
                return jsonify([s.to_json() for s in sheets])
            except ValueError as ex:
                return str(ex)
    return 'BAD REQUEST'

@app.route('/adduser', methods=['POST'])
def _add_user():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "username" in keys and len(keys) == 1:
            try:
                add_user(content.get("username"))
                return 'OK'
            except ValueError as ex:
                return str(ex)
    return 'BAD REQUEST'

@app.route('/removeuser', methods=['POST'])
def _remove_user():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            remove_user(content.get("id"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/modifysheet', methods=['POST'])
def _modify_user():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and "username" in keys and len(keys) == 2:
            modify_element(content.get("id"), content.get("username"))
            return 'OK'

    return 'BAD REQUEST'

"""
Then all of the view nonsense
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    elements = []

    if request.method == "POST":
        new_data = request.form['data']
        sheet_id = request.form['sheet_id']
        try:
            add_element(sheet_id, new_data)
        except ValueError as ex:
            errors.append(str(ex))
            return render_template('index.html', errors=errors)

    elements = list(Element.query.all())
    sheets = list(Sheet.query.all())
    users = list(User.query.all())

    return render_template('index.html', errors=errors, elements=elements, sheets=sheets, users=users)

@app.route('/sheet/<sheet_id>', methods=['GET', 'POST'])
def sheet(sheet_id):
    errors = []
    try:
        elements = get_elements_of_sheet(sheet_id)
    except ValueError:
        abort(404)

    return render_template('sheet.html', errors=errors, elements=elements)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
