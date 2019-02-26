from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.decorators import login_required

from cdmsoro.models import PermintaanResume
from cdmsoro.forms import (
    BukisValidationForm, ManualOrderForm
)
from masterdata.forms import (
    ResumeOrderForm, ResumeOrderForm_v2
)
from masterdata.models import Order
from cdmsoro.tasks import sending_telegram
from cdmsoro.tasks import sending_to_pic

@login_required()
def index(request):
    page = request.GET.get('page', 1)
    per_bukis_objs = PermintaanResume.objects.filter(
        resume__isnull=True, validate=False
    )
    paginator = Paginator(per_bukis_objs, 10)

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


@login_required()
def permintaan_bukis_list_view(request):
    page = request.GET.get('page', 1)
    per_bukis_objs = PermintaanResume.objects.filter(resume__isnull=True, manual_bukis=False)
    paginator = Paginator(per_bukis_objs, 10)

    try:
        per_page_bukis = paginator.page(page)
    except PageNotAnInteger:
        per_page_bukis = paginator.page(1)
    except EmptyPage:
        per_page_bukis = paginator.page(paginator.num_pages)

    content = {
        'bukis_list': per_page_bukis
    }
    return render(request, 'cdmsoro/v2/pg-index2.html', content)

@login_required()
def per_bukis_detail_view(request, id):
    per_bukis = get_object_or_404(PermintaanResume, pk=id, resume__isnull=True)
    form = BukisValidationForm(request.POST or None)
    resume_form = ResumeOrderForm(per_bukis.sid.sid, request.POST or None, initial={'circuit': per_bukis.sid})
    manual_form = ManualOrderForm(id, request.POST or None, initial={'permintaan_resume': per_bukis})
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.permintaan_resume = per_bukis
            instance.save()
            return redirect('cdmsoro:per_bukis_list')

        if resume_form.is_valid() and per_bukis.is_approved():
            instance = resume_form.save(commit=False)
            instance.type_order = 'RO'
            instance.create_by = request.user
            instance.save()
            PermintaanResume.objects.filter(pk=id).update(resume=instance)
            sending_to_pic(id, settings.TELEGRAM_KEY, settings.REMOT_TELEHOST)
            return redirect('cdmsoro:per_bukis_list')

        if manual_form.is_valid():
            manual_form.save()
            return redirect('cdmsoro:per_bukis_list')

    content = {
        'per_bukis': per_bukis,
        'form': form,
        'bukis_form': resume_form,
        'manual_form': manual_form,
    }

    return render(request, 'cdmsoro/v2/pg-detail-per-bukis.html', content)

@login_required()
def uncomplete_order_list_view(request):
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
    return render(request, 'cdmsoro/v2/pg-uncomplete-order.html', content)


@login_required()
def manual_bukis_list(request):
    page = request.GET.get('page', 1)
    search = request.GET.get('search', None)
    per_bukis = PermintaanResume.objects.filter(manual_bukis=True)
    if search:
        per_bukis = per_bukis.filter(sid__sid=search)

    paginator = Paginator(per_bukis, 10)
    try :
        bukis_list = paginator.page(page)
    except PageNotAnInteger:
        bukis_list = paginator.page(1)
    except EmptyPage:
        bukis_list = paginator.page(paginator.num_pages)

    content = {
        'bukis_list': bukis_list
    }
    return render(request, 'cdmsoro/v2/pg-manual-bukis-list.html', content)

@login_required()
def detail_manual_bukis_view(request, id):
    per_bukis = get_object_or_404(PermintaanResume, pk=id, manual_bukis=True)
    resume_form = ResumeOrderForm(per_bukis.sid.sid, request.POST or None, initial={'circuit': per_bukis.sid})
    if request.method == 'POST':
        if resume_form.is_valid() and per_bukis.is_approved():
            instance = resume_form.save(commit=False)
            instance.type_order = 'RO'
            instance.create_by = request.user
            instance.save()
            PermintaanResume.objects.filter(pk=id).update(resume=instance)
            sending_to_pic(id, settings.TELEGRAM_KEY, settings.REMOT_TELEHOST)
            return redirect('cdmsoro:per_bukis_list')
    content = {
        'per_bukis': per_bukis,
        'bukis_form': resume_form,
    }

    return render(request, 'cdmsoro/v2/pg-detail-manual-bukis.html', content)





















@login_required()
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


@login_required()
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