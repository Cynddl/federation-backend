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
app.config['MONGO_URI'] = os.getenv('MONGOHQ_URI', 'mongodb://dev:dev@localhost/federation')
app.config['MONGODB_SETTINGS'] = {'db': 'federation', 'host': app.config['MONGO_URI']}
app.config['FACEBOOK_AUTH'] = os.getenv('FACEBOOK_AUTH')

app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', '')
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_TRACKABLE'] = True

app.secret_key = os.getenv('SECRET_KEY', '')

app.jinja_env.globals['momentjs'] = momentjs
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


# Add a LaTex env for Jinja2

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

texenv = app.jinja_env.overlay()
texenv.block_start_string = '((*'
texenv.block_end_string = '*))'
texenv.variable_start_string = '((('
texenv.variable_end_string = ')))'
texenv.comment_start_string = '((='
texenv.comment_end_string = '=))'
texenv.filters['escape_tex'] = escape_tex


# Connection to MongoDB
db = MongoEngine(app)


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
assets.register('main_js', main_js)
assets.register('main_css', main_css)


# Import all the views
import federation.views
import federation.auth

# Register a new blueprint for /api
from api import api
app.register_blueprint(api)
