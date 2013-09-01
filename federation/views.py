#!/usr/bin/env python
# -*- coding: utf-8 -*-

from federation import app
from flask import render_template, request, redirect
from . import db
from models import Event, EventForm, Newsletter, make_choices

from flask.ext.security import login_required

import arrow
import dateutil.parser
from datetime import datetime, timedelta
from bson.objectid import ObjectId


bariol_icons = ['penguin', 'sir', 'bottle', 'batman', 'dark-vador', 'homer', 'dracula', 'pirate']

icons = {
    u'Spéciales': ['bariol-star', 'bariol-camera', 'bariol-games', 'bariol-mermaid', 'bariol-laptop', 'bariol-scifi', 'bariol-bottle'],
    u'Autres': ['bariol-penguin', 'bariol-sir', 'bariol-batman', 'bariol-dark-vador', 'bariol-homer', 'bariol-dracula', 'bariol-pirate', 'bariol-tintin', 'bariol-lego', 'bariol-halloween', 'bariol-gift', 'bariol-heart'],
    u'Nourriture': ['bariol-cup', 'bariol-tea-cup', 'bariol-hamburger', 'bariol-chicken', 'bariol-beer', 'bariol-hotdog', 'bariol-cupcake', 'bariol-croissant'],
    u'Musique': ['bariol-turntable', 'bariol-sax', 'bariol-trumpet', 'bariol-micro', 'bariol-guitar', 'bariol-headphones'],
}


@app.route('/')
@login_required
def index():
    return render_template('logged.html')


@app.route('/events/edit/<string:id>', methods=['GET', 'POST'])
@app.route('/events/', methods=['GET', 'POST'])
@login_required
def events(id=None):
    if id:
        event = Event.objects.get(pk=id)
        event.update_timezone()
        add_form = EventForm(request.form, obj=event)
        title_aside = u'Éditer l\'événement'
    else:
        event = Event()
        add_form = EventForm()
        title_aside = u'Créer un événement'

    if add_form.organisations.data:
        add_form.organisations.choices = make_choices(add_form.orgas_choices, selected=add_form.organisations.data, name='Organisations')

    if add_form.places.data:
        add_form.places.choices = make_choices(add_form.places_choices, selected=add_form.places.data, name='Lieux')

    if add_form.validate_on_submit():
        event.title = add_form.title.data
        event.description = add_form.description.data
        event.organisations = add_form.organisations.data
        event.places = add_form.places.data
        event.datetime_first = arrow.get(add_form.datetime_first.data).datetime
        event.datetime_last = arrow.get(add_form.datetime_last.data).datetime
        event.update_timezone()

        event.status = 'published' if 'publish' in request.form else 'draft'

        event.save()
        if id:
            return redirect('/events')

    today = arrow.now().date()
    events_published = Event.objects(status='published', datetime_first__gte=today).order_by('datetime_first')
    events_old_published = Event.objects(status='published', datetime_first__lt=today).order_by('-datetime_first')
    events_draft = Event.objects(status='draft').order_by('datetime_first')

    return render_template('events.html', events_draft=events_draft, events_old_published=events_old_published, events_published=events_published, add_form=add_form, title_aside=title_aside, icons=icons)


@app.route('/newsletter', methods=['GET', 'POST'])
@login_required
def newsletter():
    news_form = Newsletter()
    events = []

    if news_form.validate_on_submit():
        date_first = arrow.get(news_form.datetime_first.data).datetime
        date_last = arrow.get(news_form.datetime_last.data).datetime
        events = Event.objects(datetime_first__gte=date_first, datetime_first__lte=date_last, status='published').order_by('date_first')
        print len(events)

    if 'send' in request.form and news_form.validate_on_submit():
        day_range = arrow.Arrow.span_range('day', date_first, date_last)
        day_events = [(d_1, [e for e in events if e['datetime_first'] > d_1.naive and e['datetime_first'] < d_2.naive]) for (d_1, d_2) in day_range]
        day_events = [(d_1, events) for (d_1, events) in day_events if len(events) != 0]
        return render_template('newsletter_mail.html', news_form=news_form, day_first=arrow.get(date_first), day_last=arrow.get(date_last), day_events=day_events, arrow=arrow)
    else:
        return render_template('newsletter.html', news_form=news_form, events=events)


@app.route('/cse')
@login_required
def cse():
    return render_template('logged.html')


@app.route('/admin')
@login_required
def admin():
    return render_template('logged.html')
