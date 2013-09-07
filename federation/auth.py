#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.security import Security, MongoEngineUserDatastore, UserMixin, RoleMixin
from . import app, db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[])

    associations = db.ListField(db.StringField(max_length=255), default=[])
    nom = db.StringField(max_length=255)
    prenom = db.StringField(max_length=255)

    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField()
    current_login_ip = db.StringField()
    login_count = db.IntField()

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)
