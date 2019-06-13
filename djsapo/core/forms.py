# -*- coding: utf-8 -*-

from django import forms

from djsapo.core.models import Alert


class AlertForm(forms.ModelForm):

    class Meta:
        model = Alert
        # either fields or exclude is required
        fields = '__all__'

