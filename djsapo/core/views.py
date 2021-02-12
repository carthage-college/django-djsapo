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
from djimix.people.utils import get_peeps

from djauth.decorators import portal_auth_required
from djtools.utils.users import in_group

from datetime import datetime

import requests
import json

REQ_ATTR = settings.REQUIRED_ATTRIBUTE


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def alert_form(request, pid=None):

    if request.method=='POST':
        user = request.user
        form = AlertForm(request.POST, use_required_attribute=REQ_ATTR)
        form_doc1 = DocumentForm(
            request.POST,
            request.FILES,
            use_required_attribute=REQ_ATTR,
            prefix='doc1',
        )
        form_doc2 = DocumentForm(
            request.POST,
            request.FILES,
            use_required_attribute=REQ_ATTR,
            prefix='doc2',
        )
        form_doc3 = DocumentForm(
            request.POST,
            request.FILES,
            use_required_attribute=REQ_ATTR,
            prefix='doc3',
        )
        status =  (
            form.is_valid() and
            form_doc1.is_valid() and
            form_doc2.is_valid() and
            form_doc3.is_valid()
        )
        if status:
            alert = form.save(commit=False)
            student = User.objects.get(email=request.POST.get('student'))
            alert.student = student
            alert.created_by = user
            alert.updated_by = user
            alert.save()
            # m2m save for GenericChoice relationships
            form.save_m2m()
            # documents
            doc1 = form_doc1.save(commit=False)
            doc1.alert = alert
            doc1.created_by = user
            doc1.updated_by = user
            doc1.save()
            doc2 = form_doc2.save(commit=False)
            doc2.alert = alert
            doc2.created_by = user
            doc2.updated_by = user
            doc2.save()
            doc3 = form_doc3.save(commit=False)
            doc3.alert = alert
            doc3.created_by = user
            doc3.updated_by = user
            doc3.save()
            # redirect to success page
            return HttpResponseRedirect(
                reverse_lazy('alert_success')
            )
    else:
        form = AlertForm(use_required_attribute=REQ_ATTR)
        form_doc1 = DocumentForm(use_required_attribute=REQ_ATTR, prefix='doc1')
        form_doc2 = DocumentForm(use_required_attribute=REQ_ATTR, prefix='doc2')
        form_doc3 = DocumentForm(use_required_attribute=REQ_ATTR, prefix='doc3')
    return render(
        request, 'alert/form.html', {
            'form': form,
            'form_doc1':form_doc1,
            'form_doc2':form_doc2,
            'form_doc3':form_doc3,
            'year': settings.YEAR,
            'term': settings.TERM,
        }
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def people(request, who):
    '''
    Accepts: GET request where "who" = faculty/staff/facstaff/student
    Returns: all current faculty, staff, or student types
    '''

    if request.method == 'GET':
        peeps = get_peeps(who)
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
def clear_cache(request, ctype='blurb'):

    if request.is_ajax() and request.method == 'POST':
        cid = request.POST.get('cid')
        key = 'livewhale_{}_{}'.format(ctype,cid)
        cache.delete(key)
        timestamp = datetime.timestamp(datetime.now())
        earl = '{}/live/{}/{}@JSON?cache={}'.format(
            settings.LIVEWHALE_API_URL,ctype,cid,timestamp
        )
        try:
            response = requests.get(earl, headers={'Cache-Control':'no-cache'})
            text = json.loads(response.text)
            cache.set(key, text)
            content = mark_safe(text['body'])
        except:
            content = ''
    else:
        content = "Requires AJAX POST"

    return HttpResponse(content, content_type='text/plain; charset=utf-8')
