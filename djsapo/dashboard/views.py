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
from djtools.utils.mail import send_mail
from djauth.LDAPManager import LDAPManager
from djzbar.decorators.auth import portal_auth_required
from djimix.core.utils import get_connection
from djimix.sql.students import VITALS
from djimix.constants import SPORTS

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from operator import attrgetter
from itertools import chain

import json


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
    status = request.POST.get('status')
    # CSS or superuser can access all objects
    if css:
        if status:
            if status == 'All but closed':
                my_alerts = Alert.objects.exclude(status='Closed')
            elif status == 'All':
                my_alerts = Alert.objects.all()
            else:
                my_alerts = Alert.objects.filter(status=status)
        else:
            my_alerts = Alert.objects.exclude(status='Closed')
        alerts = [a for a in my_alerts]
    else:
        if status:
            if status == 'All but closed':
                my_alerts = Alert.objects.filter(created_by=user).exclude(status='Closed')
            elif status == 'All':
                my_alerts = Alert.objects.filter(created_by=user)
            else:
                my_alerts = Alert.objects.filter(created_by=user).filter(status=status)
        else:
            my_alerts = Alert.objects.filter(created_by=user).exclude(status='Closed')

        teams = Member.objects.filter(user__username=user.username)
        if status:
            if status == 'All but closed':
                team_alerts = [member.alert for member in teams if member.alert.status != 'Closed']
            elif status == 'All':
                team_alerts = [member.alert for member in teams]
            else:
                team_alerts = [member.alert for member in teams if member.alert.status == status]
        else:
            team_alerts = [member.alert for member in teams]
        alerts = sorted(
            chain(my_alerts, team_alerts), key=attrgetter('created_at')
        )

    status_choices = Alert.STATUS_CHOICES.copy()
    status_choices.append(('All but closed',"All but closed"))
    status_choices.append(('All',"All"))

    return render(
        request, 'list.html', {
            'alerts':alerts,'css':css,'status_choices':status_choices,
            'status':status
        }
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def detail(request, aid):
    alert = get_object_or_404(Alert, pk=aid)
    history = Alert.objects.filter(student=alert.student).exclude(pk=aid)
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
                    "[Student Outreach System] {}".format(form_data['subject']),
                    request.user.email, 'email_form.html',
                    {'content':form_data['content']}, [settings.ADMINS[0][1],]
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
    data =  {'msg': "Success", 'id':''}
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
        action = post.get('action')
        if mod == "category":
            obj = get_object_or_404(GenericChoice, pk=oid)
            if action == 'add':
                alert.category.add(obj)
            elif action == 'remove':
                alert.category.remove(obj)
            else:
                data['msg'] = "Options: add or remove"
        elif mod == "team":
            try:
                user = User.objects.get(pk=oid)
            except:
                l = LDAPManager()
                luser = l.search(oid)
                user = l.dj_create(luser)
            if user:
                if action == 'add':
                    mail = False
                    if not alert.team.all():
                        alert.status='Assigned'
                        alert.save()
                    try:
                        member = Member.objects.get(user=user, alert=alert)
                        if member.status:
                            data['msg'] = "User is already a team member"
                        else:
                            member.status = True
                            member.save()
                            data['msg'] = "User has been reactivated"
                            data['id'] = member.id
                            mail = True
                    except:
                        member = Member.objects.create(user=user,alert=alert)
                        alert.team.add(member)
                        data['msg'] = "User added to team"
                        data['id'] = member.id
                        mail = True
                    if mail:
                        send_mail(
                            request, [member.user.email],
                            "Assignment to Intervention Team",
                            settings.CSS_FROM_EMAIL, 'alert/email_team_added.html',
                            {'alert':alert,'user':member.user}, [settings.ADMINS[0][1],]
                        )

                elif action == 'remove':
                    member = get_object_or_404(Member, user=user,alert=alert)
                    member.status = False
                    member.case_manager = False
                    member.save()
                else:
                    data['msg'] = "Options: add or remove"
            else:
                    data['msg'] = "User not found"
        elif mod == "comment":
            note = None
            body = post.get('body')
            t = loader.get_template('alert/annotation.inc.html')
            if oid == 0:
                if not alert.notes.all():
                    alert.status='In progress'
                    alert.save()
                note = Annotation.objects.create(
                    alert=alert, created_by=user, updated_by=user,
                    body=post.get('body'), tags="Comments"
                )
                alert.notes.add(note)
                context = {
                    'obj':note,'bgcolor':'bg-warning'
                }
                data['msg'] = t.render(context, request)
            else:
                try:
                    note = Annotation.objects.get(pk=oid)
                    if action == "fetch":
                        data['msg'] = note.body
                    else:
                        note.body=body
                        note.updated_by = user
                        note.save()
                        context = {
                            'obj':note,'bgcolor':'bg-warning'
                        }
                        data['msg'] = t.render(context, request)
                    data['id'] = note.id
                except:
                    data['msg'] = "Follow-up not found"
        elif mod == "alert":
            value = post.get('value')
            name = post.get('name')
            setattr(alert, name, value)
            alert.save()
        else:
            data['msg'] = "Invalid Data Model"
    else:
        data['msg'] = "Requires AJAX POST"

    return HttpResponse(
        json.dumps(data), content_type='application/json; charset=utf-8'
    )



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
    vitals = student['student']
    team = [m.user for m in alert.team.all() if m.status]
    matrix = []
    for c in alert.category.all():
        for m in c.matrix.all():
            if m.user not in matrix and m.user not in team:
                matrix.append(m.user)
    advisor = None
    if vitals:
        try:
            advisor = User.objects.get(pk=vitals.adv_id)
        except:
            l = LDAPManager()
            luser = l.search(vitals.adv_id)
            if luser:
                advisor = l.dj_create(luser)
    if advisor and advisor not in matrix and advisor not in team:
        matrix.append(advisor)
    # obtain all users who are a member of "Coaches" group
    for c in User.objects.filter(groups__name='Coaches'):
        if c not in matrix and c not in team:
            matrix.append(c)
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
            'student':vitals,'sports':student['sports'],'peeps':peeps
        }
    )
