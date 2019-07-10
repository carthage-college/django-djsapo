from django.conf import settings
from django.core.cache import cache
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from djsapo.core.models import GenericChoice, Member
from djsapo.core.forms import AlertForm, DocumentForm
from djsapo.core.utils import get_connection

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


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def people(request, who):
    '''
    Accepts: GET request where "who" = faculty/staff/student
    Returns: all current faculty, staff, or student types
    '''

    if request.method == 'GET':
        sql = """
            SELECT
                lastname, firstname, username
            FROM
                provisioning_vw
            WHERE
                {} is not null
            ORDER BY
                lastname, firstname
        """.format(who)

        key = 'provisioning_vw_{}_api'.format(who)
        peeps = cache.get(key)
        if peeps is None:
            connection = get_connection()
            cursor = connection.cursor()
            objects = cursor.execute(sql)
            peeps = []
            if objects:
                for obj in objects:
                    row = {
                        'lastname': obj[0], 'firstname': obj[1],
                        'email': '{}@carthage.edu'.format(obj[2])
                    }
                    peeps.append(row)
                cache.set(key, peeps, timeout=86400)
        response = render(
            request, 'peeps.html', {'peeps':peeps,},
            content_type='application/json; charset=utf-8'
        )
    else:
        response = HttpResponse("None", content_type='text/plain; charset=utf-8')

    return response


@csrf_exempt
@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def kat_matrix(request):

    if request.is_ajax() and request.method == 'POST':
        cids = request.POST.getlist('cids[]')
        matrix = "<ol>"
        peeps = []
        for c in cids:
            cat = GenericChoice.objects.get(pk=c)
            for m in cat.matrix.all():
                if m.user.id not in peeps:
                    matrix += '<li><input type="checkbox"> {}, {}</li>'.format(m.user.last_name, m.user.first_name)
                peeps.append(m.user.id)
        matrix += "</ol>"
        response = render(
            request, 'matrix.html', {'matrix': mark_safe(matrix),'peeps':peeps}
        )
    else:
        response = HttpResponse(
            "Requires AJAX POST", content_type='text/plain; charset=utf-8'
        )

    return response

