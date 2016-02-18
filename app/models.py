from flask.ext.security import UserMixin, RoleMixin, login_required
from flask_admin.contrib import sqla

from app.hello import db
# from flask import current_app

users_nodes = db.Table('users_nodes',
    db.Column('node_id', db.Integer(), db.ForeignKey('node.id')),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')))

class Node(db.Model):

    # Columns

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    hostname = db.Column(db.String(128))
    ip = db.Column(db.String(20))
    description = db.Column(db.Text)

    register_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    users = db.relationship('User', secondary=users_nodes,
                            backref=db.backref('users', uselist=False))


roles_props = db.Table('roles_props',
    db.Column('prop_id', db.Integer(), db.ForeignKey('property.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

users_props = db.Table('users_props',
    db.Column('prop_id', db.Integer(), db.ForeignKey('property.id')),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')))


class Property(db.Model):
    # Columns

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    parent = db.relation("Property", remote_side=[id])

    name = db.Column(db.String(128))
    value = db.Column(db.Text)

    roles = db.relationship('Role', secondary=roles_props,
                            backref=db.backref('props_r', uselist=False))
    users = db.relationship('User', secondary=users_props,
                            backref=db.backref('props_u', uselist=False))
    # lazy='dynamic',

    def update(self, data):
        for field in ['name', 'value', 'parent_id']:
            if data.get(field):
                setattr(self, field, data.get(field))

    def __str__(self):
        return '%s - %s(%s)' % (self.id, self.name, self.value)

    def __json__(self):
        return ['id', 'name', 'value', 'parent_id']


class NodeProps(db.Model):
    __tablename__ = 'node_props'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    node = db.relationship("Node", backref=db.backref('props', lazy='dynamic'))

    prop_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    prop = db.relationship("Property", backref=db.backref('nodes', lazy='dynamic'))

    value = db.Column(db.String(256))


# Define security models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __unicode__(self):
        return '%s - %s' % (self.id, self.name)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', uselist=False))
    props = db.relationship('Property', secondary=users_props,
                            backref=db.backref('props', uselist=False))

    def __unicode__(self):
        return '%s - %s' % (self.id, self.email)


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(64))

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='info')

    def __unicode__(self):
        return '%s - %s' % (self.key, self.value)

# Customized User model admin
class UserAdmin(sqla.ModelView):
    inline_models = (UserInfo,)
