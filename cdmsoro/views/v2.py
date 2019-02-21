from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from cdmsoro.models import PermintaanResume
from cdmsoro.forms import BukisValidationForm
from masterdata.forms import (
    ResumeOrderForm, ResumeOrderForm_v2
)
from masterdata.models import Order
from cdmsoro.tasks import sending_telegram

def index(request):
    page = request.GET.get('page', 1)
    per_bukis_objs = PermintaanResume.objects.filter(resume__isnull=True)
    paginator = Paginator(per_bukis_objs, 20)

    try:
        per_page_bukis = paginator.page(page)
    except PageNotAnInteger:
        per_page_bukis = paginator.page(1)
    except EmptyPage:
        per_page_bukis = paginator.page(paginator.num_pages)

    content = {
        'bukis_list': per_page_bukis
    }
    return render(request, 'cdmsoro/v2/pg-index.html', content)


def permin_bukis_detail_view(request, id):
    data = dict()
    per_bukis = get_object_or_404(PermintaanResume, pk=id)
    form = BukisValidationForm(request.POST or None)
    resume_form = ResumeOrderForm(request.POST or None, initial={'circuit': per_bukis.sid})
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.permintaan_resume = per_bukis
            instance.save()

        if resume_form.is_valid() and per_bukis.is_approved():
            instance = resume_form.save(commit=False)
            instance.type_order = 'RO'
            instance.create_by = request.user
            instance.save()
            PermintaanResume.objects.filter(pk=id).update(resume=instance)

    content = {
        'per_bukis': per_bukis,
        'form': form,
        'bukis_form': resume_form
    }

    data['html'] = render_to_string(
        'cdmsoro/v2/includes/partial-permitaan-bukis-detail.html',
        content,
        request = request
    )
    
    return JsonResponse(data)



def uncomplete_order_view(request):
    data = dict()
    page = request.GET.get('page', 1)
    order_objs = Order.objects.filter(closed=False)

    paginator = Paginator(order_objs, 20)
    try:
        perpage_order = paginator.page(page)
    except PageNotAnInteger:
        perpage_order = paginator.page(1)
    except EmptyPage:
        perpage_order = paginator.page(paginator.num_pages)

    content = {
        'order_list': perpage_order
    }
    data['html'] = render_to_string(
        'cdmsoro/v2/includes/partial-uncomplete-order.html',
        content,
        request = request
    )
    return JsonResponse(data)


def lapor_soro(requests, id):
    data = dict()
    order_obj = get_object_or_404(Order, pk=id)
    data['html'] = render_to_string(
        'cdmsoro/v2/includes/lapor-soro.html',
        {'order': order_obj}
    )
    sending_telegram(order_obj.id, settings.TELEGRAM_KEY, -245044203)
    return JsonResponse(data)