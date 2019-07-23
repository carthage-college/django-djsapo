from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from djsapo.core.models import Alert, GenericChoice, Member

from djtools.utils.users import in_group
from djtools.utils.convert import str_to_class
from djzbar.decorators.auth import portal_auth_required

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


@portal_auth_required(
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def home(request):
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
def detail(request, aid):
    data = get_object_or_404(Alert, pk=aid)
    user = request.user
    perms = data.permissions(user)
    if not perms['view']:
        raise Http404("You do not have permission to view that alert")

    return render(
        request, 'alert/detail.html', {'data':data,'perms':perms}
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
                    "[Center for Student Success] {}".format(
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


@csrf_exempt
@portal_auth_required(
    group = settings.CSS_GROUP,
    session_var='DJSAPO_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def comments_form(request):
    """
    Ajax POST form to create a new Annotation object for an Alert

    Requires via POST:

    aid (alert ID)
    body
    """

    if request.is_ajax() and request.method == 'POST':
        msg = "Success"
    else:
        msg = "Requires AJAX POST"

    return HttpResponse(msg, content_type='text/plain; charset=utf-8')
