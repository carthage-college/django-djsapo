from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from djsapo.core.forms import AlertForm, CommentForm, DocumentForm
from djtools.utils.mail import send_mail

REQ_ATTR = settings.REQUIRED_ATTRIBUTE


@login_required
def alert_form(request, pid=None):
    if settings.DEBUG:
        TO_LIST = [settings.SERVER_EMAIL,]
    else:
        TO_LIST = [settings.CSS_EMAIL,]
    BCC = settings.MANAGERS

    if request.method=='POST':
        form = AlertForm(request.POST, use_required_attribute=REQ_ATTR)
        form_com = CommentForm(request.POST, use_required_attribute=REQ_ATTR)
        form_doc = DocumentForm(
            request.POST, request.FILES, use_required_attribute=REQ_ATTR
        )
        if form.is_valid() and form_com.is_valid() and form_doc.is_valid():
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
        form = AlertForm(use_required_attribute=REQ_ATTR)
        form_com = CommentForm(use_required_attribute=REQ_ATTR)
        form_doc = DocumentForm(use_required_attribute=REQ_ATTR)
    return render(
        request, 'alert/form.html',
        {'form': form,'form_doc':form_doc,'form_com':form_com}
    )
