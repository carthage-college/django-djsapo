from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from djsapo.core.models import Member
from djsapo.core.forms import AlertForm, DocumentForm

from djzbar.decorators.auth import portal_auth_required
from djtools.utils.mail import send_mail

REQ_ATTR = settings.REQUIRED_ATTRIBUTE


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def alert_form(request, pid=None):

    if request.method=='POST':
        user = request.user
        form = AlertForm(request.POST, use_required_attribute=REQ_ATTR)
        form_doc = DocumentForm(
            request.POST, request.FILES, use_required_attribute=REQ_ATTR
        )
        if form.is_valid() and form_doc.is_valid():
            alert = form.save(commit=False)
            #user = User.objects.get(pk=alert.student)
            student = User.objects.get(pk=request.POST.get('student'))
            alert.student = student
            alert.created_by = user
            alert.updated_by = user
            alert.save()
            # m2m save for GenericChoice relationships
            form.save_m2m()
            doc = form_doc.save(commit=False)
            doc.alert = alert
            doc.created_by = user
            doc.save()

            to_list = [settings.SERVER_EMAIL,]
            bcc = [settings.MANAGERS,]
            frum = settings.CSS_EMAIL

            if not settings.DEBUG:
                bcc.append(settings.CSS_EMAIL)
                to_list = [user.email,]
            subject = "[Early Alert] {} {}".format(
                alert.student.first_name, alert.student.last_name
            )
            send_mail(
                request, to_list, subject, frum, 'alert/email.html', alert, bcc
            )
            return HttpResponseRedirect(
                reverse_lazy('alert_success')
            )
    else:
        form = AlertForm(use_required_attribute=REQ_ATTR)
        form_doc = DocumentForm(use_required_attribute=REQ_ATTR)
    return render(
        request, 'alert/form.html', {'form': form,'form_doc':form_doc,}
    )
