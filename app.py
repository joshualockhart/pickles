from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
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

def add_element(new_data):
    if len(new_data) <= MAX_DATA_LENGTH:
        e = Element(data=new_data)
        db.session.add(e)
        db.session.commit()
    else:
        raise ValueError("Data too long: max length is {} characters".format(MAX_DATA_LENGTH))

def get_element(element_id):
    e = Element.query.filter_by(id=element_id).first()
    if e == None:
        raise ValueError("No element with id {}".format(element_id))
    return e

def get_elements_between_dates(start_date, end_date):
    elements = Element.query.filter(Element.timestamp.between(start_date, end_date)).all()
    return elements

def remove_element(element_id):
    try:
        e = get_element(element_id)
        db.session.delete(e)
        db.session.commit()
    except ValueError as ex:
        raise ex

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    if request.method == "POST":
        new_data = request.form['data']
        try:
            add_element(new_data)
        except ValueError as ex:
            errors.append(str(ex))

    else:
        errors.append("Data too long: max length is {} characters".format(MAX_DATA_LENGTH))
        return render_template('index.html', errors=errors)

    elements = list(Element.query.all())

    return render_template('index.html',errors=errors, elements=elements)

@app.route('/add', methods=['POST'])
def add():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "data" in keys and len(keys) == 1:
            add_element(content.get("data"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/remove', methods=['POST'])
def remove():
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            remove_element(content.get("id"))
            return 'OK'
    return 'BAD REQUEST'

@app.route('/get', methods=['POST'])
def get():
    print(request)
    if request.is_json:
        content = request.get_json(silent=True)
        keys = content.keys()
        if "id" in keys and len(keys) == 1:
            e = get_element(content.get("id"))
            return jsonify(e.to_json())

        elif "start_date" in keys and "end_date" in keys and len(keys) == 2:
            start_date = dateutil.parser.parse(content.get("start_date"))
            end_date = dateutil.parser.parse(content.get("end_date"))
            """
            # for now we take times in milliseconds from epoch
            base_datetime = datetime.datetime( 1970, 1, 1 )

            start_delta = datetime.timedelta(milliseconds=content.get("start_date"))
            end_delta = datetime.timedelta(milliseconds=content.get("end_date"))

            start_date = base_datetime + start_delta
            end_date = base_datetime + end_delta
            """
            elements = get_elements_between_dates(start_date, end_date)
            return jsonify([e.to_json() for e in elements])

    return 'BAD REQUEST'

if __name__ == '__main__':
    app.run(host='0.0.0.0')

