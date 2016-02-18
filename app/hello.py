#!flask/bin/python
import os

import click

from flask import render_template, make_response
from flask import jsonify
from flask import Flask, request

from flask.ext.autodoc import Autodoc
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required

from flask_cli import FlaskCLI
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask_wtf.csrf import CsrfProtect

import flask_admin as admin

# from views import vm
# app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__, instance_relative_config=True)

# json encoding
# from json import AlchemyEncoder
# app.json_encoder = AlchemyEncoder
json = FlaskJSON(app)

auto = Autodoc(app)

FlaskCLI(app)

# Load the default configuration
app.config.from_object('app.config.default')

# Load the local home configuration
# app.config.from_object('app.config.local-home')
app.config.from_envvar('MSVM_APPLICATION_SETTINGS')

db = SQLAlchemy(app)

csrf = CsrfProtect(app)

from app.models import *
# print db
# print app.config
# db.create_all()
# bind=db.engine

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create admin
admin = admin.Admin(app, name='Example: SQLAlchemy', template_mode='bootstrap3')

# Add views
admin.add_view(UserAdmin(User, db.session))

from views import vm, prop

app.register_blueprint(vm.vm, url_prefix='/vm')
app.register_blueprint(prop.prop, url_prefix='/prop')


# # Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    # user_datastore.create_user(email='admin@webz.asia', password='123')
    db.session.commit()


@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo('Init the db')

    db.create_all()

def is_disabled_protect(request):
    print request.path
    # if request.
    return request.path in ['/auth/token', '/login', '/prop/add']

@app.before_request
def check_csrf():
    if not is_disabled_protect(request):
        csrf.protect()

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/install/<vmname>')
@auto.doc(groups=['node', 'public'])
def install(vmname):
    """
    Request from VM for install bash script contents

    :param vmname: str - VM hostname
    :return: text script response
    """
    r = make_response(render_template('install.sh', vmname=vmname, MSVM_URL=app.config['MSVM_URL']), 200)
    return r

@app.route('/ping/<vmname>')
@auto.doc(groups=['node', 'public'])
@as_json
def ping(vmname):
    """
    Request from VM to check status

    :param vmname: str - VM hostname
    :return: JSON response
    """
    # data = jsonify(dict(vmname=vmname))
    # r = Response(response=data, status=200, mimetype="application/json")

    # r = make_response(jsonify(dict(vmname=vmname, exec_url="/exec/123")), 200)
    # r.mimetype = "application/json"
    # return r
    return dict(vmname=vmname, exec_url="/exec/123"), 200

@app.route('/exec/<script_name>')
@auto.doc(groups=['node', 'public'])
def exec_script(script_name):
    """
    Request from VM to execute script by script_name loaded in response
    :param script_name: str -
    :return: text script response
    """
    s = Flask.template_folder + "/exec/" + script_name
    print s
    if os.path.exists(s):
        print "FOUND!"
    r = make_response(render_template("exec/" + script_name, script_name=script_name, MSVM_URL=app.config['MSVM_URL']), 200)
    return r

@app.route('/auth/token', methods=['POST'])
def get_auth_token():
    # data = jsonify(dict(vmname=vmname))
    # r = Response(response=data, status=200, mimetype="application/json")
    # auth = security.try_login()
    print app.login_manager.a
    r = make_response(jsonify(dict(vmname='vmname', exec_url="/exec/123")), 200)
    r.mimetype = "application/json"
    return r

@app.route('/doc')
@app.route('/doc/public')
def public_doc():
    return auto.html(groups=['public'], title='Public Documentation')


@app.route('/doc/private')
def private_doc():
    return auto.html(groups=['private'], title='Private Documentation')

@app.route('/doc/node')
def node_doc():
    return auto.html(groups=['vm'], title='Node manager specific Documentation')

# if __name__ == '__main__':
#     if __package__ is None:
#         os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     app.run(host='0.0.0.0')
