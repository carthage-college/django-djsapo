from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404

from djsapo.core.forms import AlertForm
from djtools.utils.mail import send_mail

REQ_ATTR = settings.TEMPLATES[0]['OPTIONS']['debug']


def alert_form(request, pid=None):
    if settings.DEBUG:
        TO_LIST = [settings.SERVER_EMAIL,]
    else:
        TO_LIST = [settings.MY_APP_EMAIL,]
    BCC = settings.MANAGERS

    if request.method=='POST':
        form = AlertForm(
            request.POST, request.FILES, use_required_attribute=REQ_ATTR
        )
        if form.is_valid():
            data = form.save()
            email = settings.DEFAULT_FROM_EMAIL
            if data.email:
                email = data.email
            subject = "[Submit] {} {}".format(data.first_name,data.last_name)
            send_mail(
                request,TO_LIST, subject, email,'alert/email.html', data, BCC
            )
            return HttpResponseRedirect(
                reverse_lazy('alert_success')
            )
    else:
        form = AlertForm()
    return render(
        request, 'alert/form.html',
        {'form': form,}
    )
