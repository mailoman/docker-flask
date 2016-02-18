from flask import Blueprint
from flask import request

from flask.ext.security import login_required, auth_token_required
from flask.ext.login import current_user

from flask_json import as_json

from ..hello import auto
from app.models import *
from vendor.vm_rs.vm_rs import RsVm

prop = Blueprint('prop', __name__)

@prop.route('/list')
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def list():
    """
    Get list of properties for current user

    :return: JSON
    """

    result = {}
    status = 404

    # nodes=Property.query.all()
    props_by_user = Property.query.filter(Property.users.contains(current_user)).all()
    if props_by_user:
        result['props'] = props_by_user
        status = 200

    return result, status


@prop.route('/<int:id>')
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def get(id):
    """
    Get Property by ID

    :param id: int - primary ID
    :return: JSON
    """

    result = {}
    status = 404
    print id
    # nodes=Property.query.all()
    obj = Property.query.filter_by(id=id).filter(Property.users.contains(current_user)).first()
    if obj:
        result['prop'] = obj
        status = 200

    return result, status

@prop.route('/by/<name>')
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def get_by_name(name):
    """
    Get Property by name

    :param name: str - name
    :return: JSON
    """

    result = {}
    status = 404
    print id
    # nodes=Property.query.all()
    obj = Property.query.filter_by(name=name).filter(Property.users.contains(current_user)).first()
    if obj:
        result['prop'] = obj
        status = 200

    return result, status


@prop.route('/add', methods=['POST'], defaults={'obj_type': 'user'})
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def add_default(obj_type):
    """
    Add property to object specified by type & posted json data:

    ``{"name": "<str>", "value": "<str>"}``

    :param obj_type: str - user | node - object type to link with added propertie, "user" - default
    :return: JSON
    """

    return add()

@prop.route('/add/<obj_type>', methods=['POST'])
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def add_by_type(obj_type='user'):
    """
    Add property to object specified by type & posted json data:

    ``{"name": "<str>", "value": "<str>"}``

    :param obj_type: str - user | node - object type to link with added propertie, "user" - default
    :return: JSON
    """

    return add(obj_type)


def add(obj_type='user'):
    result = {}
    status = 404

    data = request.get_json(force=True)
    print 'add json data:'
    print data
    p = Property()
    if not data:
        return result, status
    p.update(data)

    obj_id = obj = None
    # obj_id = data.get('obj_id') # supposed to be available only for specific users/roles

    if obj_type == 'user':
        # supposed to be available only for specific users/roles
        # if obj_id:
        #     obj = User.get(obj_id)
        # else:
        obj = current_user
        if obj:
            p.users.append(obj)

    if obj_type == 'node':
        # rs | aws
        node_type = 'rs'
        prop_parent = Property.query.filter_by(name=node_type).first()
        p.parent = prop_parent

        if obj_id:
            obj = Node.get(obj_id)
        # else:
        #     obj = Node.query.filter_by(name=node_type).all()
        if obj:
            p.nodes.append(obj)

    if obj and p:
        db.session.add(p)
        db.session.commit()
        result['prop'] = p
        status = 201

    #
    # if type == 'rs':
    #
    #     prop_parent = Property.query.filter_by(name='rs').all()
    #     print prop_parent, current_user.roles, current_user.roles[0].id
    #
    #     # for role in current_user.roles:
    #     #     print role.id
    #     #     prop_by_roles = Property.query.filter(Property.roles.contains(role)).all()
    #     #     for prop in prop_by_roles:
    #     #         print prop
    #
    #     props = {}
    #
    #     for p in current_user.props:
    #         print p.id
    #         props_filter = ['ssh_keys', 'rs_credentials']
    #         for name in props_filter:
    #             if p.parent.name == name:
    #                 if not props.get(name):
    #                     props[name] = {}
    #                 props[name][p.name] = p.value
    #
    #     print current_app, session
    #     # with current_app.test_request_context('/'):
    #         # print current_app.user_datastore
    #         # u = current_user
    #     api = RsVm.instance(dict=props['rs_credentials'])
    #     api.enable_db_cache('DB?')
    #     print current_app.test_client()
    #     print api._get_config()
    #     print api.list_servers()

    return result, status

@prop.route('/update/<string:obj_type>', methods=['POST'])
@auto.doc(groups=['prop', 'private'])
@as_json
@auth_token_required
def update_by_name_type(obj_type='user'):
    """
    Update Property by name provided by posted json data:

    ``{"name": "<str>", "value": "<str>"}``

    :param obj_type: str - user | node - object type to link with added propertie, "user" - default
    :return: JSON
    """
    result = {}
    status = 404

    data = request.get_json(force=True)
    print 'add json data:'
    print data

    if not data or not data.get('name'):
        return result, status

    name = data.get('name')
    p = obj_id = obj = None

    if obj_type == 'user':
        # supposed to be available only for specific users/roles
        #  if obj_id:
        #     obj = User.get(obj_id)
        # else:
        obj = current_user
        p = Property.query.filter_by(name=name).filter(Property.users.contains(obj)).first()
        p.update(data)

    if obj and p:
        db.session.add(p)
        db.session.commit()
        result['prop'] = p
        status = 200
    else:
        return add(obj_type)

    return result, status


@prop.route('/doc')
def prop_doc():
    return auto.html(groups=['prop'], title='Properties group related Documentation')
