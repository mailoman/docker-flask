from flask import Blueprint
from flask import jsonify
from flask import render_template, make_response, current_app, session

# from flask.ext.autodoc import Autodoc
from flask.ext.login import current_user
from flask.ext.security import login_required, auth_token_required

from flask_json import as_json

from ..hello import auto
# from app import app
from app.models import *
# from app.hello import auto
from vendor.vm_rs.vm_rs import RsVm
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
vm = Blueprint('vm', __name__)

# auto = Autodoc(app)

@vm.route('/list/<type>')
@auto.doc(groups=['vm', 'private'])
@as_json
@auth_token_required
def list(type=None):
    """
    List of registered nodes

    :param type: str - rs | aws | regular - type of registered node
    :return: JSON
    """

    if type:
        # rs | aws
        if type == 'rs':
            pass
    # nodes=Node.query.all()
    nodes=Node.query.filter(Node.users.contains(current_user)).all()
    # props_by_user = Property.query.filter(Property.users.contains(current_user)).all()

    # d=dict(nodes=nodes, exec_url="/exec/123")
    # r = make_response(jsonify(d), 200)
    # r.mimetype = "application/json"
    # return r
    return dict(nodes=nodes, exec_url="/exec/123"), 200

@vm.route('/start/<type>')
@auto.doc(groups=['vm', 'private'])
@as_json
@auth_token_required
def start(type):
    """
    Start new node

    :param type: str - rs | aws[ | regular?] - type of registered node
    :return:
    """

    nodes = []
    # rs | aws
    if type == 'rs':

        prop_parent = Property.query.filter_by(name='rs').all()
        # props_by_user = Property.query.filter(Property.users.contains(current_user)).limit(100).all()
        print prop_parent, current_user.props

        # for role in current_user.roles:
        #     print role.id
        #     prop_by_roles = Property.query.filter(Property.roles.contains(role)).all()
        #     for prop in prop_by_roles:
        #         print prop

        props = {}

        for p in current_user.props:
            print p.id
            props_filter = ['ssh_keys', 'rs_credentials']
            for name in props_filter:
                if p.parent and p.parent.name == name:
                    if not props.get(name):
                        props[name] = {}
                    props[name][p.name] = p.value

        print props['rs_credentials']
        # with current_app.test_request_context('/'):
            # print current_app.user_datastore
            # u = current_user
        api = RsVm.instance(dict=props['rs_credentials'])
        api.enable_cache_handler(auth_cache_handler)

        print current_app.test_client()
        print api._get_config()
        nodes = api.list_servers().get('servers')

    return dict(nodes=nodes, exec_url="/exec/123"), 200
    # d=dict(nodes=nodes, exec_url="/exec/123")
    # r = make_response(jsonify(d), 200)
    # r.mimetype = "application/json"
    # return r
def auth_cache_handler(self, method, data=None):

    import json

    result = None
    client = current_app.test_client()
    print 'method=%s' % method
    token = "WyIxIiwiMDdiZGQ1NjYxMDQzYjhkYmM2ZWFhMWU0M2NiMDAyYWYiXQ.CaMDBA.JifbpXuE3-hNFD9lURbuthZ43go"

    if method == 'get':
        print 'request for stored cache'

        obj = client.get(
            path='/prop/by/_auth_info',
            content_type='application/json',
            headers={
                'Authentication-Token': token,
                'Content-Type': 'application/json',
            }
        )
        print obj, json.loads(obj.data)

        result = json.loads(obj.data).get('prop').get('value')

    elif method == 'store':
        # token = Serializer(current_app.config['SECRET_KEY']).dumps({'id': current_user.id}).decode('ascii')
        print 'store new auth cache(%s)' % token
        jsdata = dict(
            name='_auth_info',
            value=data,
        )
        # print jsdata
        post = client.post(
            path='/prop/update',
            data=json.dumps(jsdata),
            content_type='application/json',
            headers={
                'Authentication-Token': token,
                'Content-Type': 'application/json',
            }
        )
        print post.response.__dict__
        print post.__dict__
    return result

@vm.route('/doc')
def vm_doc():
    return auto.html(groups=['vm'], title='VM group related Documentation')

