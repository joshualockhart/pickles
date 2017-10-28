from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PICKLES_DATA_MAX_LENGTH'] = 10000

app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)

from models import *

MAX_DATA_LENGTH = app.config['PICKLES_DATA_MAX_LENGTH']

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    if request.method == "POST":
        new_data = request.form['data']
        if len(new_data) <= MAX_DATA_LENGTH:
            e = Element(data=new_data)
            db.session.add(e)
            db.session.commit()
        else:
            errors.append("Data too long: max length is {} characters".format(MAX_DATA_LENGTH))
            return render_template('index.html', errors=errors)

    elements = list(Element.query.all())
    

    return render_template('index.html',errors=errors, elements=elements)

if __name__ == '__main__':
    app.run()

