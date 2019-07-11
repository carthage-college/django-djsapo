# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput
from django.contrib.admin.widgets import AdminDateWidget

from djsapo.core.models import Alert, Annotation, Document, GenericChoice

from djauth.LDAPManager import LDAPManager
from djtools.fields.time import KungfuTimeField

CONCERN_CHOICES = GenericChoice.objects.filter(
    tags__name__in=['Category']
).filter(active=True).order_by('name')


class AlertForm(forms.ModelForm):

    student = forms.CharField(
        label = "Student",
        help_text="Search by last name or email address.",
    )
    category = forms.ModelMultipleChoiceField(
        label="Type of concern",
        queryset=CONCERN_CHOICES, widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    interaction_date = forms.DateField(
        label="Date of interaction",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(AlertForm, self).__init__(*args, **kwargs)

        choices = [('','---Select all that apply---')]
        for c in CONCERN_CHOICES:
            choices.append((c.id, c.name))
        self.fields['category'].choices = choices

    class Meta:
        model = Alert
        exclude = ('parent','status',)

    def clean_interaction_type(self):

        cd = self.cleaned_data
        if cd.get('interaction') == 'Yes' and not cd.get('interaction_type'):
            raise forms.ValidationError("You must provide an interaction type")
        if cd.get('interaction') == 'No':
            cd['interaction_type'] = None

        return cd['interaction_type']

    def clean_interaction_details(self):

        cd = self.cleaned_data
        if cd.get('interaction') == 'Yes' and not cd.get('interaction_details'):
            raise forms.ValidationError("Please provide some details about the interaction")
        if cd.get('interaction') == 'No':
            cd['interaction_details'] = None

        return cd['interaction_details']

    def clean_interaction_date(self):

        cd = self.cleaned_data
        if cd.get('interaction') == 'Yes' and not cd.get('interaction_date'):
            raise forms.ValidationError("You must provide a date for the interaction")
        if cd.get('interaction') == 'No':
            cd['interaction_date'] = None

        return cd['interaction_date']

    def clean_student(self):
        cd = self.cleaned_data
        email = cd.get('student')
        if email:
            try:
                user = User.objects.get(email=email)
                cd['student'] = user
            except:
                try:
                    # initialise the LDAP manager
                    l = LDAPManager()
                    luser = l.search(email, field='mail')
                    user = l.dj_create(luser)
                    cd['student'] = user
                except:
                    self.add_error('student', "That is not a valid college ID")

        return cd['student']


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('name','phile',)

    def clean_phile(self):

        cd = self.cleaned_data
        if cd.get('phile') and not cd.get('name'):
            self.add_error('name', "Please provide a name or description of the file.")

        return cd['phile']


class CommentForm(forms.ModelForm):
    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Provide any additional comments if need be"
    )

    class Meta:
        model = Annotation
        fields = ('body',)
