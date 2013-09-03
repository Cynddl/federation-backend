#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, request, make_response, jsonify
from functools import wraps, update_wrapper

from models import Event, DossierCSE

from datetime import datetime, date, timedelta
import facebook

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError

# New blueprint for /api
api = Blueprint('api', __name__, url_prefix='/api')
app = current_app

from werkzeug import url_decode

import simplejson as json
from bson.objectid import ObjectId
from collections import Iterable

import arrow


class MongoengineEncoder(json.JSONEncoder):
    """
    Custom JSON encoder implementation for encoding Mongoengine documents.
    """
    def default(self, obj):
        if isinstance(obj, Iterable):
            out = {}
            for key in obj:
                out[key] = getattr(obj, key)
            return out

        elif isinstance(obj, datetime):
            # Always convert to Paris TZ in api
            return arrow.get(obj).to('Europe/Paris').strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, ObjectId):
            return unicode(obj)

        return json.JSONEncoder.default(self, obj)


def support_jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs))
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def get_week_bounds(year=None, week=None):
    """
    Return the first and last monday of a given week of the current year.
    If the 'week'/'year' argument is empty, the current week/week is used.
    """
    today = datetime.now()
    if week is None:
        week = today.isocalendar()[1]
    if year is None:
        year = today.year
    last_monday = datetime.strptime('%i %i 1' % (year, week-1), '%Y %W %w')
    next_monday = datetime.strptime('%i %i 1' % (year, week), '%Y %W %w')
    return last_monday, next_monday


def get_month_bounds(year=None, month=None):
    """
    Return the first and last (rounded to first ms of the next day) days of a given month.
    If no year or no month is given, current year or month are used.
    """
    today = datetime.now()
    if month is None:
        month = today.month
    if year is None:
        year = today.year
    day_first = datetime(year, month, 1)
    day_last = datetime(year, month + 1, 1)
    return day_first, day_last


@api.route('/update-fb')
def update_facebook_vars():
    """
    Perform an update of all events with a Facebook id,
    to update the number of people attending the event.
    """
    graph = facebook.GraphAPI(app.config['FACEBOOK_AUTH'])
    events = Event.objects(facebook_id__exists=True)
    for event in events:
        count = len(graph.get_object(event.facebook_id + '/attending')['data'])
        event.attendees = count
        event.save()
    return '%i event(s) updated.' % len(events)


@api.route('/events/week')
@api.route('/events/week/<int:week>')
@api.route('/events/week/<int:year>/<int:week>')
@support_jsonp
def return_week_events(year=None, week=None):
    """Return all the events of the current week."""
    last_monday, next_monday = get_week_bounds(year, week)
    events = Event.objects(status='published', datetime_first__gte=last_monday, datetime_first__lte=next_monday).order_by('datetime_first')
    return MongoengineEncoder(ensure_ascii=False).encode(list(events.all())).encode('utf-8')


@api.route('/events/month')
@api.route('/events/month/<int:month>')
@api.route('/events/month/<int:year>/<int:month>')
@support_jsonp
def return_month_events(year=None, month=None):
    """Return all the events of the current month."""
    fst_day, lst_day = get_month_bounds(year, month)
    events = Event.objects(status='published', datetime_first__gte=fst_day, datetime_first__lte=lst_day).order_by('datetime_first')
    return MongoengineEncoder(ensure_ascii=False).encode(list(events.all())).encode('utf-8')


@api.route('/cse/demande', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin=['http://federation.ens-lyon.fr'], headers='Origin, X-Requested-With, Content-Type, Accept')
def cse_demande():
    def mk_float(s):
        s = s.strip()
        return float(s) if s else 0

    data = url_decode(request.data)

    data['logement_gracieux'] = data['logement_gracieux'] == 'Oui'
    print data['logement_montant']
    data['logement_montant'] = mk_float(data['logement_montant'])

    data['financement_famille'] = data['financement_famille'] == 'Oui'
    data['financement_famille_montant'] = mk_float(data['financement_famille_montant'])
    data['financement_autre'] = data['financement_autre'] == 'Oui'
    data['financement_autre_montant'] = mk_float(data['financement_autre_montant'])

    data['apl'] = data['apl'] == 'Oui'
    data['apl_montant'] = mk_float(data['apl_montant'])

    data['boursier'] = data['boursier'] == 'Oui'
    data['boursier_montant'] = mk_float(data['boursier_montant'])

    print data.to_dict()
    demande = DossierCSE(**data.to_dict())
    demande.save()

    return jsonify(result='saved')
