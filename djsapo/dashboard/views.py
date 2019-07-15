from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group, User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

from djsapo.core.models import Alert

from djtools.utils.users import in_group
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
    data = get_object_or_404(Alert, id=aid)
    user = request.user
    perms = data.permissions(user)
    if not perms['view']:
        raise Http404

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
