#!/usr/bin/env python
# -*- coding: utf-8 -*-

from federation import app
from flask import render_template, request, redirect
from models import Event, EventForm, Newsletter, make_choices, UserForm, DossierCSE

from flask.ext.security import login_required, current_user, roles_required, roles_accepted
from flask.ext.security.utils import encrypt_password
from auth import user_datastore

from . import texenv

import arrow

from auth import User

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

        if not event.author:
            event.author = current_user.to_dbref()

        event.datetime_first = arrow.get(add_form.datetime_first.data).datetime
        event.datetime_last = arrow.get(add_form.datetime_last.data).datetime
        event.update_timezone()

        event.status = 'published' if 'publish' in request.form else 'draft'

        event.save()
        if id:
            return redirect('/events')

    today = arrow.now().date()

    # Filter the events for non-admin users
    if not current_user.has_role('Administrateur'):
        filter_role = {'author': current_user.id}
    else:
        filter_role = {}

    events_published = Event.objects(status='published', datetime_first__gte=today, **filter_role).order_by('datetime_first')
    events_old_published = Event.objects(status='published', datetime_first__lt=today, **filter_role).order_by('-datetime_first')
    events_draft = Event.objects(status='draft', **filter_role).order_by('datetime_first')

    return render_template('events.html', events_draft=events_draft, events_old_published=events_old_published, events_published=events_published, add_form=add_form, title_aside=title_aside, icons=icons)


@app.route('/newsletter', methods=['GET', 'POST'])
@roles_accepted('Éditeur', 'Administrateur')
def newsletter():
    news_form = Newsletter()
    events = []

    if news_form.validate_on_submit():
        date_first = arrow.get(news_form.datetime_first.data).datetime
        date_last = arrow.get(news_form.datetime_last.data).datetime
        events = Event.objects(datetime_first__gte=date_first, datetime_first__lte=date_last, status='published').order_by('date_first')

    if 'send' in request.form and news_form.validate_on_submit():
        day_range = arrow.Arrow.span_range('day', date_first, date_last)
        day_events = [(d_1, [e for e in events if e['datetime_first'] > d_1.naive and e['datetime_first'] < d_2.naive]) for (d_1, d_2) in day_range]
        day_events = [(d_1, events) for (d_1, events) in day_events if len(events) != 0]
        return render_template('newsletter_mail.html', news_form=news_form, day_first=arrow.get(date_first), day_last=arrow.get(date_last), day_events=day_events, arrow=arrow)
    else:
        return render_template('newsletter.html', news_form=news_form, events=events)


@app.route('/cse', methods=['GET', 'POST'])
@roles_accepted('CSE-Dossier', 'CSE-Anonyme')
def cse():
    dossiers_cse = DossierCSE.objects()
    role_anonyme = user_datastore.find_role('CSE-Anonyme')
    users_cse_anonyme = [user.prenom + ' ' + user.nom for user in User.objects(roles=role_anonyme)]
    role_dossier = user_datastore.find_role('CSE-Dossier')
    users_cse_dossier = [user.prenom + ' ' + user.nom for user in User.objects(roles=role_dossier)]
    return render_template('cse.html', dossiers_cse=dossiers_cse, users_cse_anonyme=users_cse_anonyme, users_cse_dossier=users_cse_dossier)


@app.route('/admin/edit/<string:id>', methods=['GET', 'POST'])
@app.route('/admin', methods=['GET', 'POST'])
@roles_required('Administrateur')
@login_required
def admin(id=None):
    if id:
        user = User.objects.get(id=id)
        raw_user = user.to_mongo()
        raw_user.pop('roles')
        user_form = UserForm(request.form, roles=[r.name for r in user.roles], **raw_user)
        title_aside = u'Modifier l\'utilisateur'
    else:
        user = User()
        user_form = UserForm()
        title_aside = u'Créer un utilisateur'

    if user_form.associations.data:
        user_form.associations.choices = make_choices(user_form.associations_choices, selected=user_form.associations.data, name='Associations')

    if user_form.roles.data:
        user_form.roles.choices = make_choices(user_form.roles_choices, selected=user_form.roles.data, name=u'Rôles')

    if user_form.validate_on_submit():
        user.email = user_form.email.data
        user.nom = user_form.nom.data
        user.prenom = user_form.prenom.data
        if user_form.password.data:
            user.password = encrypt_password(user_form.password.data)

        roles_list = [user_datastore.find_or_create_role(role_name).to_dbref() for role_name in user_form.roles.data]
        user.roles = roles_list

        user.associations = user_form.associations.data

        user.save()

        if id:
            return redirect('/admin')

    def pretty_dict(_dict, key):
        return ', '.join([getattr(r, key) for r in _dict])

    users = User.objects()
    return render_template('admin.html', users=users, arrow=arrow, user_form=user_form, title_aside=title_aside, pretty_dict=pretty_dict)


@app.route('/public/cse', methods=['GET', 'POST'])
def public_cse():
    if 'email' in request.form and 'id' in request.form:
        try:
            dossier = DossierCSE.objects(email=request.form['email'], pk=request.form['id']).first()
            print request.form['email'], dossier
            return render_template('public/cse_verification.html', dossier=dossier)
        except Exception, e:
            return render_template('public/cse.html', error_message='Les identifiants sont incorrects.')
    else:
        return render_template('public/cse.html')


@app.route('/public/affiche')
def public_affiche():
    from api import get_week_bounds

    date_first, date_last = get_week_bounds()
    events = Event.objects(datetime_first__gte=date_first, datetime_first__lte=date_last, status='published').order_by('date_first')

    print events
    day_range = arrow.Arrow.span_range('day', date_first, date_last)
    day_events = [(d_1, [e for e in events if e['datetime_first'] > d_1.naive and e['datetime_first'] < d_2.naive]) for (d_1, d_2) in day_range]
    day_events = [(d_1, events) for (d_1, events) in day_events]

    template = texenv.get_template('affiche.tex')
    return template.render(day_events=day_events, day_range=day_range, arrow=arrow)
