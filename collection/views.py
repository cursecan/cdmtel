from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum, Value as V
from django.db.models.functions import Coalesce 
from django.contrib import messages
from django.utils import timezone

from masterdata.models import Customer

from .forms import (
    CustomerColFormet, AvidenttargetColForm
)


def index(request):
    page = request.GET.get('page', None)
    q = request.GET.get('search', None)
    customer_objs = Customer.objects.annotate(
        s_tagih = Coalesce(
            Sum('coltarget_customer__amount', filter=Q(coltarget_customer__due_date__lte=timezone.now().date())), V(0)
        )
    )
    if q:
        customer_objs = customer_objs.filter(
            Q(account_number__contains=q) | Q(customer_name__icontains=q)
        )

    paginator = Paginator(customer_objs, 10)
    try :
        customer_list = paginator.page(page)
    except PageNotAnInteger:
        customer_list = paginator.page(1)
    except EmptyPage:
        customer_list = paginator.page(paginator.num_pages)

    content = {
        'customer_list': customer_list
    }
    return render(request, 'collection/pg-index.html', content)



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