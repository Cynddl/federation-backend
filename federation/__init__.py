#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask
# from flask.ext.pymongo import PyMongo
from flask.ext.assets import Environment, Bundle
from flask.ext.mongoengine import MongoEngine

from momentjs import momentjs

import re
from jinja2 import evalcontextfilter, Markup, escape


app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGOHQ_URI', 'mongodb://federation:citrouille@dharma.mongohq.com:10002/fede-ensl')
app.config['MONGODB_SETTINGS'] = {'db': 'federation', 'host': app.config['MONGO_URI']}
app.config['FACEBOOK_AUTH'] = os.getenv('FACEBOOK_AUTH', 'CAACEdEose0cBAOBDTWXIkShrnPuMBi1DaR0rTCZBYUPDrfv7ApZBYThapTlWWbrYkhtui9gzqZB3ZBD5resgYTl9Mh3D43BkzQg0tF5R75fUkAMx7M1P6ZB6KEL1IKcGZCMt9deZAUTdtckkRUm6GEefzOF2ZCMnzaK88goQCZBZB1mQZDZD')

app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = 'secret_code'
app.config['SECURITY_CHANGEABLE'] = True

app.secret_key = 'KU\x05x\x81v\x99\xff\x9a\xfd\xea^\xab\x99\x9e\t\x87\xc5\xf8\x93\x8d\x98\x84\x95'

app.jinja_env.globals['momentjs'] = momentjs
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Connection to MongoDB
# db = MongoEngine(app)


# Add a "nl2br" filter
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


# Generate assets with pySCSS
assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('main.scss', filters='pyscss', output='main.css')
assets.register('css_all', scss)

# Module for date & time inputs
main_js = Bundle('js/pickadate/picker.js',
                 'js/pickadate/picker.time.js',
                 'js/pickadate/picker.date.js',
                 'js/pickadate/translations/fr_FR.js',
                 'js/selectize/selectize.min.js',
                 'js/moment.js',
                 'js/moment-timezone.js',
                 'js/moment.fr.js',
                 'js/main.js',
                 # filters='jsmin',
                 output='pickadate.min.js')
main_css = Bundle('js/pickadate/themes/classic.css',
                  'js/pickadate/themes/classic.time.css',
                  'js/pickadate/themes/classic.date.css',
                  'js/selectize/selectize.css',
                  output='pickadate.min.css')
assets.register('pickadate_js', main_js)
assets.register('pickadate_css', main_css)


# Import all the views
import federation.views
import federation.auth

# Register a new blueprint for /api
from api import api
app.register_blueprint(api)
