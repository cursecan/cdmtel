from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchVector

import datetime

from cdmsoro.models import (
    PermintaanResume, Avident,
    Validation
)

from django.contrib.auth.models import User

from masterdata.models import Order
from core.decorators import user_executor, user_validator

from cdmsoro.forms import (
    BukisValidationForm, ManualOrderForm
)
from masterdata.forms import (
    CreateResumeOrderForm, ResumeOrderForm
)

from cdmsoro.tasks import sending_to_pic, sending_notif_manual_ro

import requests


def get_paginator_set(obj, rows, page):
    paginate = Paginator(obj, rows)

    try:
        out_obj = paginate.page(page)
    except PageNotAnInteger:
        out_obj = paginate.page(1)
    except EmptyPage:
        out_obj = paginate.page(paginate.num_pages)

    return out_obj


@login_required
def index(request):
    group = request.user.profile.group
    if group in ['EX', 'EC']:
        return redirect('som:bukis_dashboard')
    
    return redirect('collection:validation')


@login_required
@user_executor
def bukisDashboard(request):
    permin_bukis = PermintaanResume.objects.filter(
        closed=False, suspend__publish=True
    )

    validation_objs = Validation.objects.all()[:5]

    if not request.user.is_superuser:
        permin_bukis = permin_bukis.filter(
            executor=request.user
        )

    permin_bukis_resume = permin_bukis.aggregate(
        waiting = Count('sid', filter=Q(status=3)),
        in_process = Count('sid', filter=Q(status=2) & Q(manual_bukis=False)),
        in_manual = Count('sid', filter=Q(manual_bukis=True))
    )

    content = {
        'per_bukis_resume': permin_bukis_resume,
        'validation': validation_objs
    }

    return render(request, 'som/pg_dashboard_perminbukis.html', content)

@login_required
@user_executor
def unclosePerminBukisView(request):
    
    page = request.GET.get('page', 1)
    q = request.GET.get('q', None)

    permin_bukis_objs = PermintaanResume.objects.filter(
        closed = False, suspend__publish=True
    ).exclude(status=1, timestamp__lte=datetime.datetime.now()-datetime.timedelta(days=10))

    if not request.user.is_superuser:
        permin_bukis_objs = permin_bukis_objs.filter(
            executor=request.user
        )
    
    if q:
        permin_bukis_objs = permin_bukis_objs.annotate(
            search = SearchVector(
                'sid__sid', 'sid__account__account_number',
                'sid__account__bp', 'sid__account__customer_name'
            )
        ).filter(search=q)

    content = {
        'permin_list': get_paginator_set(permin_bukis_objs, 20, page)
    }
    return render(request, 'som/pg_unclose_permin_bukis.html', content)


@login_required
@user_executor
def unclosePerminDetail(request, id):
    permin_obj = get_object_or_404(PermintaanResume, pk=id, closed=False, suspend__publish=True)
    form = BukisValidationForm(request.POST or None)

    perbukis_form = ResumeOrderForm(permin_obj.sid.sid, id, request.POST or None, initial={'circuit': permin_obj.sid})
    manual_form = ManualOrderForm(id, request.POST or None, initial={'permintaan_resume': permin_obj})

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.permintaan_resume = permin_obj
            instance.user = request.user
            instance.save()
            return redirect('som:unclose_detail', id)
        
        if perbukis_form.is_valid():
            instance = perbukis_form.save(commit=False)
            instance.type_order = 'RO'
            instance.create_by = request.user
            instance.order_label = permin_obj.suspend.order_label
            instance.save()
            
            permin_obj.resume = instance
            permin_obj.closed = True
            permin_obj.save()

            channel = '@cdm_notif'
            if permin_obj.suspend.order_label == 1:
                # CDM Channel
                channel = '@cdm_notif'
                
            sending_to_pic(permin_obj.id, settings.TELEGRAM_KEY, channel)

            return redirect('som:unlose_persume')

        if manual_form.is_valid():
            manual_form.save()
            return redirect('som:unlose_persume')


    content = {
        'permin_bukis': permin_obj,
        'form': form,
        'r_form': perbukis_form,
        'm_form': manual_form,
    }
    return render(request, 'som/pg_unclose_permin_detail.html', content)



@login_required
@user_executor
def manualBukisListView(request):
    manual_perbukis = PermintaanResume.objects.filter(
        closed= False, manual_bukis=True, suspend__publish=True
    )
    content = {
        'permin_bukis_list': manual_perbukis
    }

    return render(request, 'som/pg_manual_permin_bukis.html', content)


@login_required
@user_executor
def recordBukisListView(request):
    page = request.GET.get('page', 1)
    q = request.GET.get('q', None)
    sdate = request.GET.get('sdate', None)
    rdate = request.GET.get('rdate', None)

    data = dict()

    permin_bukis_objs = PermintaanResume.objects.filter(
        closed = True, suspend__publish=True
    ).annotate(
        doc_c = Count('avident__document')
    )

    if not request.user.is_superuser:
        permin_bukis_objs = permin_bukis_objs.filter(
            suspend__order_label = 1 if request.user.profile.group == 'EX' else 2
        )

    if sdate:
        data['sdate'] = sdate
        permin_bukis_objs = permin_bukis_objs.filter(
            suspend__dbcreate_on__date__gte=sdate
        )
    if rdate:
        data['rdate'] = rdate
        permin_bukis_objs = permin_bukis_objs.filter(
            resume__dbcreate_on__date__lte=rdate
        )
    
    if q:
        data['q'] = q
        permin_bukis_objs = permin_bukis_objs.annotate(
            search = SearchVector(
                'sid__sid', 'sid__account__account_number',
                'sid__account__bp', 'sid__account__customer_name',
                'resume__status',
            )
        ).filter(search=q)


    content = {
        'data': data,
        'permin_list': get_paginator_set(permin_bukis_objs, 20, page)
    }
    return render(request, 'som/pg_record_closed_bukis.html', content)




def documentUploadView(request, id):
    permin_obj = get_object_or_404(PermintaanResume, pk=id, suspend__publish=True)
    data = dict()
    content = {
        'permin_bukis': permin_obj,
    }

    data['html'] = render_to_string(
        'som/includes/partial-document-upload.html',
        content, request=request
    )
    return JsonResponse(data)



@login_required
def iPaymentView(request, id):
    obj = get_object_or_404(PermintaanResume, pk=id)

    payuser = settings.IPAYMENT_USER
    paypass = settings.IPAYMENT_PASS
    data = None

    s = requests.session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'})

    try :
        # Pre Login
        s.get('http://i-payment.telkom.co.id')

        # Login
        s.get('http://i-payment.telkom.co.id/script/intag_login.php?uid={}&pwd={}'.format(payuser, paypass))

        # Get data
        r = s.get(
            'http://i-payment.telkom.co.id/script/intag_search_trems.php',
            params = {
                'via' : 'TREMS',
                'phone' : obj.sid.account.account_number
            }, timeout=20
        )
        s.close()
        r.raise_for_status()
        data = r.text
    except:
        pass

    return render(request, 'som/ipayment.html', {'ipayment': data})


@login_required
def soroReportView(request):
    user_obj = User.objects.filter(
        profile__group = 'EX', profile__level='OF'
    ).annotate(
        c_order = Count('orderes', filter=Q(orderes__closed=False))
    )

    content = {
        'officer': user_obj,
    }
    return render(request, 'som/pg_soro_report.html', content)