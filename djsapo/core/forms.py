# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput
from django.contrib.admin.widgets import AdminDateWidget
from djauth.managers import LDAPManager
from djsapo.core.models import Alert
from djsapo.core.models import Annotation
from djsapo.core.models import Document
from djsapo.core.models import GenericChoice
from djtools.fields.time import KungfuTimeField

CONCERN_CHOICES = GenericChoice.objects.filter(
    tags__name__in=['Category']
).filter(active=True).order_by('rank')


class AlertForm(forms.ModelForm):

    student = forms.CharField(
        label = "Student",
        help_text="Search by last name or email address.",
    )
    category = forms.ModelMultipleChoiceField(
        label="Type of concern",
        queryset=CONCERN_CHOICES, widget=forms.CheckboxSelectMultiple(),
        help_text="Select all that apply.",
        required=True
    )
    interaction_date = forms.DateField(
        label="Approximate date of interaction"
    )

    def __init__(self, *args, **kwargs):
        super(AlertForm, self).__init__(*args, **kwargs)

        choices = [('','---Select all that apply---')]
        for c in CONCERN_CHOICES:
            choices.append((c.id, c.name))
        self.fields['category'].choices = choices

    class Meta:
        model = Alert
        exclude = ('parent', 'status', 'created_by')

    def clean_student(self):
        cd = self.cleaned_data
        email = cd.get('student')
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                try:
                    # initialise the LDAP manager
                    eldap = LDAPManager()
                    result_data = eldap.search(email, field='mail')
                    groups = eldap.get_groups(result_data)
                    user = eldap.dj_create(result_data, groups=groups)
                except:
                    self.add_error('student', "That is not a valid college ID")
            cd['student'] = user

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
