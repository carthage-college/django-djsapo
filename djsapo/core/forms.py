# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput
from django.contrib.admin.widgets import AdminDateWidget

from djsapo.core.models import Alert, Annotation, Document, GenericChoice

from djauth.LDAPManager import LDAPManager

CONCERN_CHOICES = GenericChoice.objects.filter(
    tags__name__in=['Category']
).filter(active=True).order_by('name')

ACTION_CHOICES = GenericChoice.objects.filter(
    tags__name__in=['Action Taken']
).filter(active=True).order_by('name')


class AlertForm(forms.ModelForm):

    student = forms.CharField(
        label = "Student ID",
    )
    category = forms.ModelMultipleChoiceField(
        label="Type of Concern",
        queryset=CONCERN_CHOICES, widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    action_taken = forms.ModelMultipleChoiceField(
        label="Action Taken",
        queryset=ACTION_CHOICES, widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    interaction_date = forms.DateField(
        label="Date of interaction",
        required=False,
        widget=forms.widgets.DateInput(attrs={'type':'date'})
    )
    interaction_time = forms.DateField(
        label="Time of interaction",
        required=False,
        widget=forms.widgets.DateInput(
            attrs={'type':'time', 'placeholder':'hh:mm:am/pm'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(AlertForm, self).__init__(*args, **kwargs)

        choices = [('','---Select all that apply---')]
        for c in CONCERN_CHOICES:
            choices.append((c.id, c.name))
        self.fields['category'].choices = choices

        choices = [('','---Select all that apply---')]
        for c in ACTION_CHOICES:
            choices.append((c.id, c.name))
        self.fields['action_taken'].choices = choices

    class Meta:
        model = Alert
        exclude = ('parent',)

    def clean(self):
        cd = self.cleaned_data
        sid = cd.get('student')
        if sid:
            try:
                user = User.objects.get(pk=sid)
                cd['student'] = user
            except:
                #try:
                if True:
                    # initialise the LDAP manager
                    l = LDAPManager()
                    luser = l.search(sid)
                    user = l.dj_create(luser)
                    cd['student'] = user
                #except:
                else:
                    self.add_error('student', "That is not a valid college ID")

        return cd


class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = \
          'Name or short description'

    class Meta:
        model = Document
        fields = ('name','phile',)


class CommentForm(forms.ModelForm):
    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Provide any additional comments if need be"
    )

    class Meta:
        model = Annotation
        fields = ('body',)
