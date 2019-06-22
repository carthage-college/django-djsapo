# -*- coding: utf-8 -*-

from django import forms
from django.forms.widgets import DateTimeInput

from djsapo.core.models import Alert, Annotation, Document, GenericChoice


CONCERN_CHOICES = GenericChoice.objects.filter(
    tags__name__in=['Category']
).filter(active=True).order_by('name')


class AlertForm(forms.ModelForm):

    category = forms.ModelMultipleChoiceField(
        label="Type of Concern",
        queryset=CONCERN_CHOICES, widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    interaction_date = forms.DateTimeField(
        label="Date and time of interaction",
        required=False
        #widget=forms.widgets.DateTimeInput(attrs={'type':'datetime'})
    )

    def __init__(self, *args, **kwargs):
        super(AlertForm, self).__init__(*args, **kwargs)

        choices = [('','---Select all that apply---')]
        for c in CONCERN_CHOICES:
            choices.append((c.id, c.name))
        self.fields['category'].choices = choices

    class Meta:
        model = Alert
        exclude = ('parent','student')
        widgets = {
            'interaction_date': DateTimeInput(attrs={'type': 'datetime-local'}),
        }


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
