#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectMultipleField, HiddenField, PasswordField
from wtforms.validators import Regexp, Required
from wtforms.widgets import html_params, HTMLString

from cgi import escape

from werkzeug.security import generate_password_hash, check_password_hash
from auth import User

from . import db
import arrow


class SelectWithDisable(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected, disabled)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, disabled in field.iter_choices():
            html.append(self.render_option(val, label, selected, disabled))
        html.append(u'</select>')
        return HTMLString(u''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, disabled):
        options = {'value': value}
        if selected:
            options['selected'] = u'selected'
        if disabled:
            options['disabled'] = u'disabled'
        return HTMLString(u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label))))


class SelectFieldWithDisable(SelectMultipleField):
    widget = SelectWithDisable(multiple=True)

    def iter_choices(self):
        for value, label, selected, disabled in self.choices:
            yield (value, label, selected, disabled)

    def pre_validate(self, form, choices=None):
        return True


def make_choices(choices, selected=[], name=None):
    if len(selected) == 0:
        return [(u'', name, True, True)] + [(a, a, False, False) for a in choices]
    else:
        return [(a, a, False, False) for a in choices if a not in selected] + [(s, s, True, False) for s in selected]


class EventForm(Form):
    """ Form to add or edit an event. """
    title = TextField('', [Required()])
    description = TextAreaField()

    datetime_first = HiddenField(validators=[Required()])
    datetime_last = HiddenField(validators=[Required()])

    date_first = TextField('', [Required()])
    date_last = TextField('', [Required()])
    time_first = TextField('', [Required(), Regexp('^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$')], default='16:00')
    time_last = TextField('', [Required(), Regexp('^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$')])

    orgas_choices = [u'BDE', u'ENScène!', u'AS', u'Fédération']
    organisations = SelectFieldWithDisable('organisations', validators=[Required()], choices=make_choices(orgas_choices, name='Organisations'))

    places_choices = [u'Foyer', u'Festive', u'Théâtre Kantor']
    places = SelectFieldWithDisable('lieux', validators=[Required()], choices=make_choices(places_choices, name='Lieux'))

class UserForm(Form):
    """ Form to add or edit a user. """
    email = TextField('Email', [Required()])
    password = PasswordField('Mot de passe')
    nom = TextField('Nom', [Required()])
    prenom = TextField('Prénom', [Required()])

    associations_choices = []
    associations = SelectFieldWithDisable('Associations', choices=make_choices(associations_choices, name='Associations'))

    roles_choices = [u'Administrateur', u'Éditeur', u'CSE-Anonyme', u'CSE-Dossier']
    roles = SelectFieldWithDisable('roles', choices=make_choices(roles_choices, name=u'Rôles'))


class Newsletter(Form):
    """ Form to generate a newsletter. """
    title = TextField()
    message = TextAreaField(default=u'Bonjour à tous,\n\nAu programme de cette newsletter…\n\nLa Com\'')

    datetime_first = HiddenField(validators=[Required()])
    datetime_last = HiddenField(validators=[Required()])

    date_first = TextField('', [Required()])
    date_last = TextField('', [Required()])


class Event(db.Document):
    """ MongoDB scheme for events. """
    title = db.StringField()
    description = db.StringField()

    status = db.StringField(choices=['draft', 'published'])

    datetime_first = db.DateTimeField()
    datetime_last = db.DateTimeField()

    organisations = db.ListField()
    places = db.ListField()

    author = db.ReferenceField('User')

    meta = {'collection': 'events'}

    def update_timezone(self):
        self.datetime_first = arrow.get(self.datetime_first).to('Europe/Paris').datetime
        self.datetime_last = arrow.get(self.datetime_last).to('Europe/Paris').datetime


class DossierCSE(db.Document):
    """ MongoDB scheme for CSE documents. """
    nom = db.StringField()
    prenom = db.StringField()
    email = db.StringField()
    status = db.StringField(choices=['Auditeur', 'Normalien'])
    annee_entree = db.StringField()

    boursier = db.BooleanField()
    boursier_montant = db.FloatField()

    logement_gracieux = db.BooleanField()
    logement_montant = db.FloatField()

    apl = db.BooleanField()
    apl_montant = db.FloatField()

    financement_parents = db.BooleanField()
    financement_parents_montant = db.FloatField()

    financement_autre = db.BooleanField()
    financement_autre_source = db.StringField()
    financement_autre_montant = db.FloatField()
