from django.conf import settings
from django.template import loader
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from djsapo.core.models import Alert, Annotation, GenericChoice, Member
from djsapo.core.utils import get_peeps

from djtools.utils.users import in_group
from djzbar.decorators.auth import portal_auth_required
from djimix.core.utils import get_connection
from djimix.sql.students import VITALS
from djimix.constants import SPORTS

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from operator import attrgetter
from itertools import chain


def _student(alert):
    """
    move to core/utils if need be
    """
    connection = get_connection()
    cursor = connection.cursor()
    student = cursor.execute(VITALS(cid=alert.student.id)).fetchone()
    sports = []
    if student:
        athletics = student.sports.split(',')
        for s in SPORTS:
            for a in athletics:
                if a in s:
                    sports.append(s[1])
    return {'student':student, 'sports':sports}


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def home(request):
    user = request.user
    css = in_group(user, settings.CSS_GROUP)
    # CSS or superuser can access all objects
    if css:
        my_alerts = Alert.objects.all().order_by('-created_at')
        alerts = [a for a in my_alerts]
    else:
        my_alerts = Alert.objects.filter(created_by=user).order_by('-created_at')
        teams = Member.objects.filter(user__username="akrusza")
        team_alerts = [member.alert for member in teams]
        alerts = sorted(
            chain(my_alerts, team_alerts), key=attrgetter('created_at')
        )

    return render(request, 'list.html', {'alerts':alerts,'css':css})


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def detail(request, aid):
    alert = get_object_or_404(Alert, pk=aid)
    history = Alert.objects.filter(student=alert.student)
    user = request.user
    perms = alert.permissions(user)
    if not perms['view']:
        raise Http404("You do not have permission to view that alert")
    else:
        student = _student(alert)

    return render(
        request, 'alert/detail.html', {
            'data':alert, 'history':history, 'perms':perms,
            'student':student['student'], 'sports':student['sports']
        }
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def search(request):
    error = None
    form = None
    objects = None
    '''
    if request.method == 'POST':
        form = DateCreatedForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            objects = Transaction.objects.filter(
                created_at__gte=data['created_at']
            ).all()
    else:
        form = DateCreatedForm()
    '''

    return render(
        request, 'search.html', {
            'form':form, 'objects':objects, 'error':error
        }
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def list(request):
    """
    complete listing of all objects
    """

    user = request.user
    css = in_group(user, settings.CSS_GROUP)
    # CSS or superuser can access all objects
    if css:
        alerts = Alert.objects.all().order_by('-created_at')
    else:
        alerts = Alert.objects.filter(created_by=user)
    return render(
        request, 'list.html', {'alerts':alerts,}
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def email_form(request, aid, action):
    '''
    send an email
    '''

    form_data = None
    alert = get_object_or_404(Alert, pk=aid)
    if request.method=='POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            if 'execute' in request.POST:
                if DEBUG:
                    to_list = [MANAGER]
                else:
                    to_list = []
                send_mail (
                    request, to_list,
                    "[Student Outreach System] {}".format(
                        form_data['subject']
                    ), request.user.email, 'email_form.html',
                    {'content':form_data['content']}, BCC
                )
                return HttpResponseRedirect(
                    reverse_lazy('email_done')
                )
            else:
                return render (
                    request, 'email_form.html',
                    {'form':form,'data':form_data,'p':proposal}
                )
    else:
        form = EmailForm()

    return render(
        request, 'email_form.html',
        {'form': form,'data':form_data,'alert':alert,'action':action}
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def openxml(request):

    wb = Workbook()
    ws = wb.get_active_sheet()

    data = serializers.serialize('python', Alert.objects.all() )

    head = False
    headers = []
    for d in data:
        row = []
        for n,v in d['fields'].items():
            headers.append(model._meta.get_field(n).verbose_name.title())
            row.append(v)
        if not head:
            ws.append(headers)
            head = True
        ws.append(row)

    response = HttpResponse(
        save_virtual_workbook(wb), content_type='application/ms-excel'
    )

    response['Content-Disposition'] = 'attachment;filename={}.xlsx'.format(
        mod
    )

    return response


@csrf_exempt
@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def manager(request):
    """
    manage object relationships for an alert and for alert values themselves
    """
    user = request.user
    if request.is_ajax() and request.method == 'POST':
        post = request.POST
        # simple error handling to prevent malicious values
        try:
            oid = int(post.get('oid'))
            aid = int(post.get('aid'))
        except:
            raise Http404("Invalid alert or object ID")
        mod = post.get('mod')
        alert = get_object_or_404(Alert, pk=aid)
        msg = "Success"
        action = post.get('action')
        if mod == "category":
            obj = get_object_or_404(GenericChoice, pk=oid)
            if action == 'add':
                alert.category.add(obj)
            elif action == 'remove':
                alert.category.remove(obj)
            else:
                msg = "Options: add or remove"
        elif mod == "team":
            user = get_object_or_404(User, pk=oid)
            if action == 'add':
                alert.team.add(user)
            elif action == 'remove':
                member = get_object_or_404(Member, user=user,alert=alert)
                member.status = False
                member.case_manager = False
                member.save()
            else:
                msg = "Options: add or remove"
        elif mod == "comment":
            note = Annotation.objects.create(
                alert=alert, created_by=user, body=post.get('body'),
                tags="Comments"
            )
            alert.notes.add(note)
            t = loader.get_template('alert/annotation.inc.html')
            context = {
                'obj':note,'bgcolor':'list-group-item-success'
            }
            msg = t.render(context, request)
        elif mod == "alert":
            value = post.get('value')
            name = post.get('name')
            setattr(alert, name, value)
            alert.save()
        else:
            msg = "Invalid Data Model"
    else:
        msg = "Requires AJAX POST"

    return HttpResponse(msg, content_type='text/plain; charset=utf-8')


@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def team_manager(request, aid):
    """
    manage team members
    """

    alert = get_object_or_404(Alert, pk=aid)
    perms = alert.permissions(request.user)
    student = _student(alert)
    team = [m.user for m in alert.team.all() if m.status]
    matrix = []
    for c in alert.category.all():
        for m in c.matrix.all():
            if m.user not in matrix and m.user not in team:
                matrix.append(m.user)
    peeps = get_peeps('facstaff')
    folks = team + matrix
    # iterate over a copy of peeps and remove duplicates from original peeps
    for p in peeps[:]:
        for f in folks:
            if f.id == p['cid']:
                peeps.remove(p)

    return render(
        request, 'team.html', {
            'data':alert,'perms':perms, 'matrix':matrix,'return':True,
            'student':student['student'], 'sports':student['sports'],
            'peeps':peeps
        }
    )
