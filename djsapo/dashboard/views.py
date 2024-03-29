# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models.query import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.urls import reverse_lazy
from djauth.managers import LDAPManager
from djauth.decorators import portal_auth_required
from djimix.constants import SPORTS_ALL
from djimix.core.database import get_connection
from djimix.core.database import xsql
from djimix.people.utils import get_peeps
from djimix.sql.students import ADMISSIONS_REP
from djimix.sql.students import SPORTS
from djimix.sql.students import VITALS
from djsapo.core.forms import CONCERN_CHOICES
from djsapo.core.models import Alert
from djsapo.core.models import Annotation
from djsapo.core.models import GenericChoice
from djsapo.core.models import Member
from djtools.utils.mail import send_mail

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from operator import attrgetter
from itertools import chain

import json
import logging
logger = logging.getLogger('debug_logger')


def _get_dates(request):
    """Obtain the start and end dates."""
    today = date.today()
    date_start = request.POST.get('date_start')
    if not date_start:
        date_start = today - timedelta(days=1)
    else:
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
    date_end = request.POST.get('date_end')
    if not date_end:
        date_end = today + timedelta(days=1)
    else:
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date() + timedelta(days=1)

    return (date_start, date_end)


def _student(alert):
    """Obtain the student data."""
    with get_connection() as connection:
        student = xsql(VITALS(cid=alert.student.id), connection).fetchone()
        obj = xsql(SPORTS(cid=alert.student.id), connection).fetchone()
        sports = []
        if obj and obj.sports:
            athletics = obj.sports.split(',')
            for s in SPORTS_ALL:
                for a in athletics:
                    if a in s:
                        sports.append(s[1])
    return {'student':student, 'sports':sports}

@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """Home page view."""
    user = request.user
    css = user.profile.css()
    status_choices = Alert.STATUS_CHOICES.copy()
    status_choices.append(('All but closed',"All but closed"))
    status_choices.append(('All',"All"))
    date_start = None
    date_end = None
    status = 'All but closed'
    if request.method == 'POST':
        date_start, date_end = _get_dates(request)
        status = str(request.POST.get('status', 'All but closed'))
    return render(
        request,
        'list.html',
        {
            'css': css,
            'status': status,
            'status_choices': status_choices,
            'date_start': date_start,
            'date_end': date_end,
        },
    )

@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home_ajax(request):
    """AJAX response for dashboard home for admins."""
    user = request.user
    css = user.profile.css()
    post = request.POST
    status = post.get('status', 'All but closed')
    # order by
    col = 'created_at'
    dirx = '-'
    order = post.get('order[0][column]')
    search = post.get('search[value]')

    date_start = None
    date_end = None
    if request.POST.get('date_start'):
        date_start, date_end = _get_dates(request)
    if order:
        order = int(order)
        # column names
        columns = Alert.COLUMNS
        # direction
        dirx = post.get('order[0][dir]')
        col = columns.get(order)
    order_by = col if dirx == 'asc' else '-' + col
    # CSS or superuser can access all objects
    if css:
        if status == 'All but closed':
            my_alerts = Alert.objects.exclude(status='Closed')
        elif status == 'All':
            my_alerts = Alert.objects.all()
        else:
            my_alerts = Alert.objects.filter(status=status)
        if date_start and date_end:
            my_alerts = my_alerts.filter(created_at__range=(date_start, date_end))
    else:
        # created by me
        if status == 'All but closed':
            my_alerts = Alert.objects.filter(created_by=user).exclude(
                status='Closed'
            )
        elif status == 'All':
            my_alerts = Alert.objects.filter(created_by=user)
        else:
            my_alerts = Alert.objects.filter(created_by=user).filter(
                status=status
            )

        # team of which i am a current member
        teams = Member.objects.filter(user__username=user.username).exclude(
            status=False,
        )
        if teams:
            if status == 'All but closed':
                team_alerts = Alert.objects.filter(team__user=user).exclude(
                    team__status=False,
                ).exclude(status='Closed')
            elif status == 'All':
                team_alerts = Alert.objects.filter(team__user=user).exclude(
                    team__status=False,
                )
            else:
                team_alerts = Alert.objects.filter(team__user=user).exclude(
                    team__status=False,
                ).filter(status=status)

            my_alerts = my_alerts | team_alerts

    post = request.POST
    # draw counter
    draw = int(post.get('draw', 0))
    # paging first record indicator.
    start = int(post.get('start', 0))
    # number of records that the table can display in the current draw
    length = int(post.get('length', 25))
    # page number, 1-based index
    page = int((start / length) + 1)

    if search:
        my_alerts = my_alerts.filter(
            Q(created_by__last_name__icontains=search)|
            Q(student__last_name__icontains=search)|
            Q(course__icontains=search)|
            Q(relationship__icontains=search)
        )

    records_total = len(my_alerts)
    records_filtered = records_total
    paginator = Paginator(my_alerts.order_by(order_by), length)
    object_list = paginator.get_page(page).object_list
    alerts = []
    for alert in object_list:
        name_student = '<a href="{0}" title="{1}">{2}, {3}</a>'.format(
            reverse('detail', args=[alert.id]),
            alert.student.id,
            alert.student.last_name,
            alert.student.first_name,
        )
        name_creator = '<a href="mailto:{0}">{1}, {2}</a>'.format(
            alert.created_by.email,
            alert.created_by.last_name,
            alert.created_by.first_name,
        )
        alert_dict = {
            'student': name_student,
            'course': alert.course,
            'creator': name_creator,
            'created_at': alert.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'relationship': alert.relationship,
            'category': [cat.name for cat in alert.category.all()],
            'status': alert.status or '',
            'note_latest': alert.latest_note(),
            'note_count': alert.notes.all().count(),
        }
        team = ''
        if css:
            for member in alert.team.all():
                if member.status and member.user.profile.case_manager:
                    team += ('{0}, {1}; '.format(
                        member.user.last_name, member.user.first_name,
                    ))
        alert_dict['case_manager'] = team
        alerts.append(alert_dict)

    return JsonResponse(
        {
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': alerts,
        },
        safe=False,
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def detail(request, aid):
    """Display the Alert detail view."""
    alert = get_object_or_404(Alert, pk=aid)
    history = Alert.objects.filter(student=alert.student).exclude(pk=aid)
    user = request.user
    perms = alert.permissions(user)
    if not perms['view']:
        return HttpResponseRedirect(reverse_lazy('access_denied'))
    else:
        student = _student(alert)

    return render(
        request, 'alert/detail.html', {
            'data':alert,
            'categories': CONCERN_CHOICES,
            'history':history,
            'perms':perms,
            'student':student['student'],
            'sports':student['sports'],
            'year': settings.YEAR,
            'term': settings.TERM,
        }
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def search(request):
    """Search for Alerts."""
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
        request,
        'search.html',
        {'form':form, 'objects':objects, 'error':error},
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def list(request):
    """Complete listing of all objects."""
    user = request.user
    # CSS or superuser can access all objects
    if user.profile.css():
        alerts = Alert.objects.all().order_by('-created_at')
    else:
        alerts = Alert.objects.filter(created_by=user)
    return render(
        request, 'list.html', {'alerts':alerts,}
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def email_form(request, aid, action):
    """Send an email."""
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
                    request,
                    to_list,
                    "[Student Outreach System] {0}".format(form_data['subject']),
                    request.user.email,
                    'email_form.html',
                    {'content': form_data['content']},
                    [settings.ADMINS[0][1]],
                )
                return HttpResponseRedirect(reverse_lazy('email_done'))
            else:
                return render (
                    request,
                    'email_form.html',
                    {'form': form, 'data': form_data, 'p': proposal},
                )
    else:
        form = EmailForm()

    return render(
        request,
        'email_form.html',
        {'form': form, 'data': form_data, 'alert': alert, 'action': action},
    )


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def openxml(request):
    """Export data in openxml format for download."""
    wb = Workbook()
    ws = wb.get_active_sheet()
    data = serializers.serialize('python', Alert.objects.all())
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
        save_virtual_workbook(wb), content_type='application/ms-excel',
    )
    response['Content-Disposition'] = 'attachment;filename={}.xlsx'.format(mod)
    return response


@csrf_exempt
@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def manager(request):
    """Manage object relationships for an Alert and for Alert values."""
    user = request.user
    data =  {'msg': "Success", 'id': ''}
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
        if mod == 'category':
            obj = get_object_or_404(GenericChoice, pk=oid)
            if action == 'add':
                alert.category.add(obj)
            elif action == 'remove':
                alert.category.remove(obj)
            else:
                data['msg'] = "Options: add or remove"
        elif mod == 'team':
            try:
                user = User.objects.get(pk=oid)
            except User.DoesNotExist:
                # chapuza because the LDAP attribute for user ID has a space
                # in the name and we cannot search on it.
                sql = 'SELECT * FROM cvid_rec WHERE cx_id={0}'.format(oid)
                with get_connection() as connection:
                    cvid_rec = xsql(sql, connection).fetchone()
                if cvid_rec:
                    username = cvid_rec.ldap_name.strip()
                    eldap = LDAPManager()
                    result_data = eldap.search(username, field='cn')
                    groups = eldap.get_groups(result_data)
                    user = eldap.dj_create(result_data, groups=groups)
                else:
                    user = None
            if user:
                if action == 'add':
                    mail = False
                    if not alert.team.all() and alert.status != 'In progress':
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
                    except Exception:
                        member = Member.objects.create(user=user,alert=alert)
                        alert.team.add(member)
                        data['msg'] = "User added to team"
                        data['id'] = member.id
                        mail = True
                    if mail:
                        to_list = [member.user.email]
                        bcc = [settings.ADMINS[0][1],]
                        if settings.DEBUG:
                            to_list = bcc
                        send_mail(
                            request,
                            to_list,
                            "Assignment to Outreach Team",
                            settings.CSS_FROM_EMAIL,
                            'alert/email_team_added.html',
                            {'alert': alert, 'user': member.user},
                            bcc,
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
        elif mod == 'comment':
            note = None
            body = post.get('value')
            t = loader.get_template('alert/annotation.inc.html')
            if oid == 0:
                if not alert.notes.all():
                    alert.status='In progress'
                    alert.save()
                note = Annotation.objects.create(
                    alert=alert, created_by=user, updated_by=user, body=body,
                    tags='Comments'
                )
                alert.notes.add(note)
                context = {'obj':note,'bgcolor':'bg-warning'}
                data['msg'] = t.render(context, request)
            else:
                try:
                    note = Annotation.objects.get(pk=oid)
                    if action == 'fetch':
                        data['msg'] = note.body
                    elif action == 'delete':
                        note.delete()
                    else:
                        note.body=body
                        note.updated_by = user
                        note.save()
                        context = {'obj':note,'bgcolor':'bg-warning'}
                        data['msg'] = t.render(context, request)
                    data['id'] = note.id
                except:
                    data['msg'] = "Follow-up not found"
        elif mod == 'concern':
            name = post.get('name')
            data['id'] = aid
            if action == 'fetch':
                data['msg'] = getattr(alert, name)
            else:
                value = post.get('value')
                # 'type of concern' / category is a list and m2m from alert
                if name == 'category':
                    # disassociate the related objects
                    alert.category.clear()
                    # set the current relationships
                    for gid in post.getlist('value[]'):
                        gc = GenericChoice.objects.get(pk=gid)
                        alert.category.add(gc)
                else:
                    setattr(alert, name, value)
                    alert.save()
                if name in ['description','interaction_details']:
                    data['msg'] = '<div class="card-text" id="oid_{}_{}">{}</div>'.format(
                        name, aid, value
                    )
                else:
                    data['msg'] = 'Success'
        else:
            data['msg'] = "Invalid Data Model"
    else:
        data['msg'] = "Requires AJAX POST"

    return HttpResponse(
        json.dumps(data), content_type='application/json; charset=utf-8',
    )


@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def team_manager(request, aid):
    """Manage team members."""
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
    eldap = LDAPManager()
    if vitals:
        try:
            advisor = User.objects.get(pk=vitals.adv_id)
        except User.DoesNotExist:
            result_data = eldap.search(vitals.ldap_name.strip(), field='cn')
            if result_data:
                groups = eldap.get_groups(result_data)
                advisor = eldap.dj_create(result_data, groups=groups)
        if advisor and advisor not in matrix and advisor not in team:
            matrix.append(advisor)

    # check if we should add admissions reps and coaches to the matrix
    admissions = False
    admissions_group = 'Admissions Representative'
    coaches = False
    coaches_group = 'Coaches'
    for c in alert.category.all():
        for g in c.group.all():
            if g.name == admissions_group:
                admissions = True
            if g.name == coaches_group:
                coaches = True

    # add admissions reps to the matrix
    if admissions:
        rep = None
        group = Group.objects.get(name=admissions_group)
        connection = get_connection()
        with connection:
            obj = xsql(ADMISSIONS_REP(cid=alert.student.id), connection).fetchone()
            if obj:
                try:
                    rep = User.objects.get(pk=obj.id)
                except:
                    luser = l.search(obj.id)
                    if luser:
                        rep = l.dj_create(luser)
                if rep:
                    if not rep.groups.filter(name=admissions_group).exists():
                        group.user_set.add(rep)
                    if rep not in matrix and rep not in team:
                        matrix.append(rep)

    # add coaches to the matrix
    if coaches:
        for c in User.objects.filter(groups__name=coaches_group):
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
        request,
        'team.html',
        {
            'data': alert,
            'perms': perms,
            'matrix': matrix,
            'return': True,
            'student': vitals,
            'sports': student['sports'],
            'peeps': peeps,
        },
    )


@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def delete_note(request, oid):
    """Delete a comment form an Alert."""
    note = get_object_or_404(Annotation, pk=oid)
    note.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        "Follow-up was deleted",
        extra_tags='alert-success',
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
