from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import SearchVector

from cdmsoro.models import (
    PermintaanResume, Avident,
    Validation
)

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
        return redirect('som:unlose_persume')
    
    return redirect('collection:validation')

@login_required
@user_executor
def unclosePerminBukisView(request):
    request.session.set_expiry(300)
    
    page = request.GET.get('page', 1)
    q = request.GET.get('q', None)

    permin_bukis_objs = PermintaanResume.objects.filter(
        closed = False
    )

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
    permin_obj = get_object_or_404(PermintaanResume, pk=id, closed=False)
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
        closed= False, manual_bukis=True
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

    permin_bukis_objs = PermintaanResume.objects.filter(
        closed = True
    ).annotate(
        doc_c = Count('avident__document')
    )

    if not request.user.is_superuser:
        permin_bukis_objs = permin_bukis_objs.filter(
            suspend__order_label = 1 if request.user.profile.group == 'EX' else 2
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
    return render(request, 'som/pg_record_closed_bukis.html', content)




def documentUploadView(request, id):
    permin_obj = get_object_or_404(PermintaanResume, pk=id)
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