from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum, Subquery, OuterRef, Value as V, DecimalField
from django.db.models.functions import Coalesce 
from django.contrib import messages
from django.utils import timezone

import datetime
import pendulum

from masterdata.models import (
    Customer, Segment
)

from .models import ColTarget

from .forms import (
    CustomerColFormet, AvidenttargetColForm
)


def accountCollecView(request):
    page = request.GET.get('page', None)
    q = request.GET.get('search', None)
    segmen = request.GET.get('seg', None)
    period = request.GET.get('period', timezone.now().date())

    customer_objs = Customer.objects.filter(cur_saldo__gt=0)
    segmen_objs = Segment.objects.values('segment')

    if segmen:
        customer_objs = customer_objs.filter(
            segment__segment=segmen
        )

    if q:
        customer_objs = customer_objs.filter(
            Q(account_number__contains=q) | Q(customer_name__icontains=q)
        )

    customer_objs = customer_objs.annotate(
        s_tagih = F('cur_saldo') - Coalesce(
            Sum('coltarget_customer__amount', filter=Q(coltarget_customer__due_date__gt=period)), V(0)
        ),
        b_tagih = Coalesce(
            Sum('coltarget_customer__amount', filter=Q(coltarget_customer__due_date__lte=period)), V(0)
        )
    )

    customer_resume = customer_objs.aggregate(
        total_tagih = Sum('s_tagih'),
        piutang = Sum('cur_saldo'),
    )

    paginator = Paginator(customer_objs, 20)
    try :
        customer_list = paginator.page(page)
    except PageNotAnInteger:
        customer_list = paginator.page(1)
    except EmptyPage:
        customer_list = paginator.page(paginator.num_pages)

    content = {
        'segment_list': segmen_objs,
        'customer_list': customer_list,
        'customer_resume': customer_resume,
        'q': q,
        'segmen': segmen,
    }
    return render(request, 'collection/pg-account-colection.html', content)


def segmentCollecView(request):
    period = []
    cur_date = timezone.now().date()
    cdate = pendulum.date(cur_date.year, cur_date.month, 1)
    for i in range(6):
        period.append(cdate)
        cdate = cdate.add(months=1)

    cust = Customer.objects.filter(
        segment = OuterRef('pk')
    ).order_by().values('segment')

    cust_sum = cust.annotate(
        t = Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0) & Q(coltarget_customer__due_date__gte=period[0])),
        V(0)
    ).values('t')

    segment_objs = Segment.objects.exclude(segment='TDS').annotate(
        s_saldo = Coalesce(Sum('customer_list__cur_saldo', filter=Q(customer_list__cur_saldo__gt=0)), V(0)),
        t_1 = F('s_saldo') - Subquery(
                cust_sum
            ),
        # t_2 = F('s_saldo') - Subquery(
        #         Customer.objects.select_related('coltarget_customer').filter(
        #             segment=OuterRef('pk')
        #         ).annotate(
        #             t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0) & Q(coltarget_customer__due_date__gte=period[1])), V(0))
        #         ).values('t')[:1], output_field=DecimalField()
        #     ),
        # t_3 = F('s_saldo') - Subquery(
        #         Customer.objects.select_related('coltarget_customer').filter(
        #             segment=OuterRef('pk')
        #         ).annotate(
        #             t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0) & Q(coltarget_customer__due_date__gte=period[2])), V(0))
        #         ).values('t')[:1], output_field=DecimalField()
        #     ),
        # t_4 = F('s_saldo') - Subquery(
        #         Customer.objects.filter(
        #             segment=OuterRef('pk'), coltarget_customer__due_date__gte=period[3]
        #         ).annotate(
        #             t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0)), V(0))
        #         ).values('t')[:1], output_field=DecimalField()
        #     ),
        # t_5 = F('s_saldo') - Subquery(
        #         Customer.objects.filter(
        #             segment=OuterRef('pk'), coltarget_customer__due_date__gte=period[4]
        #         ).annotate(
        #             t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0)), V(0))
        #         ).values('t')[:1], output_field=DecimalField()
        #     ),
        # t_6 = F('s_saldo') - Subquery(
        #         Customer.objects.filter(
        #             segment=OuterRef('pk'), coltarget_customer__due_date__gte=period[5]
        #         ).annotate(
        #             t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0)), V(0))
        #         ).values('t')[:1], output_field=DecimalField()
        #     ),
        ).values('segment', 's_saldo', 't_1')

    content = {
        'period': period,
        'segment_list': segment_objs
    }
    return render(request, 'collection/pg-segmnet-col.html', content)

def json_SegmentCollecView(request):
    segment_objs = Segment.objects.exclude(segment='TDS').annotate(
        s_saldo = Coalesce(Sum('customer_list__cur_saldo', filter=Q(customer_list__cur_saldo__gt=0)), V(0)),
        t_tagih = F('s_saldo') - Subquery(
                    Customer.objects.select_related('segment').filter(
                        segment=OuterRef('pk')
                    ).annotate(
                        t = Coalesce(Sum('coltarget_customer__amount', filter=Q(cur_saldo__gt=0) & Q(coltarget_customer__due_date__gte=timezone.now().date())), V(0))
                    ).values('t')[:1], output_field=DecimalField()
                )
    ).values('segment', 's_saldo', 't_tagih')

    seg_list = list(segment_objs)

    data = {
        'chart': {
            'type': 'column'
        },
        'title': {
            'text': 'Piutang & TGK Jatuh Tempo (Curr)'
        },
        'xAxis': {
            'categories': list(map(lambda row: row['segment'], seg_list))
        },
        'series': [{
            'name': 'Jatuh Tempo',
            'data': list(map(lambda row: int(row['t_tagih']), seg_list))
        }, {
            'name': 'Piutang',
            'data': list(map(lambda row: int(row['s_saldo']), seg_list))
        }]
    }

    return JsonResponse(data)


def custCollectDetailView(request, id):
    cust_obj = get_object_or_404(Customer, pk=id)
    col_tar_obj = ColTarget.objects.filter(customer=cust_obj).aggregate(
        t_amount = Coalesce(Sum('amount'), V(0))
    )
    formset = CustomerColFormet(request.POST or None, instance=cust_obj)
    if request.method == 'POST':
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Recording data complete.')
            return redirect('collection:index')
            
    content = {
        'cust_obj': cust_obj,
        'formset': formset,
        'col_target': col_tar_obj,
    }
    return render(request, 'collection/pg-collection-customer-detail.html', content)



def entryDataView(request):
    return render(request, 'collection/pg-entry-data.html')


def jsonCustomerView(request):
    data = dict()
    q = request.GET.get('q', None)
    customer_objs = Customer.objects.order_by('account_number')
    if q:
        customer_objs = customer_objs.filter(
            Q(account_number__icontains=q) | Q(customer_name__icontains=q)
        )
    paginator = Paginator(customer_objs, 10)
    customer_list = paginator.page(1)
    content = {
        'customer_list': customer_list
    }
    data['html'] = render_to_string(
        'collection/includes/partial-customer-list.html',
        content,
        request = request
    )
    return JsonResponse(data)


def jsonCustomerDetailJtempo(request, id):
    customer_obj = get_object_or_404(Customer, pk=id)
    data = dict()
    
    formset = CustomerColFormet(request.POST or None, instance=customer_obj)
    if request.method == 'POST':    
        if formset.is_valid():
            formset.save()

            data['form_is_valid'] = True
            messages.success(request, 'Recording data complete.')

        else :
            data['form_is_valid'] = False

    content = {
        'cust': customer_obj,
        'formset': formset,
    }
    data['html'] = render_to_string(
        'collection/includes/partial-custoemr-detail-jt.html',
        content,
        request= request
    )
    return JsonResponse(data)


def jsonUploadDocView(request, id):
    customer_obj = get_object_or_404(Customer, pk=id)
    data = dict()
    if request.method == 'POST':
        form = AvidenttargetColForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.customer = customer_obj
            instance.save()
            data['is_valid'] = True
        else :
            data['is_valid'] = False

    return JsonResponse(data)


@login_required
def collectionValidationView(request):
    cust_obj = Customer.objects.filter(has_target=True)
    page = request.GET.get('page', None)
    q = request.GET.get('q', None)

    if q:
        cust_obj = cust_obj.filter(
            Q(account_number__contains=q) | Q(customer_name__icontains=q)
        )
    
    paginator = Paginator(cust_obj, 10)
    try :
        cust_list = paginator.page(page)
    except PageNotAnInteger:
        cust_list = paginator.page(1)
    except EmptyPage:
        cust_list = paginator.page(paginator.num_pages)

    content = {
        'customer_list': cust_list
    }
    return render(request, 'collection/pg-collection-validation.html', content)


@login_required
def detailColValidationView(request, id):
    cust_obj = get_object_or_404(Customer, pk=id, has_target=True)
    if request.method == 'POST':
        cust_obj.is_valid = True
        cust_obj.save()

    content = {
        'cust_obj': cust_obj
    }
    return render(request, 'collection/pg-detail-validation.html', content)