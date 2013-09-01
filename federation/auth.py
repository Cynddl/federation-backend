#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask.ext.security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin
# from flask.ext.security.utils import encrypt_password
from . import app, db
# from models import User


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)
