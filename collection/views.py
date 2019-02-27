from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from masterdata.models import Customer

from .forms import (
    CustomerColFormet,
    ColTargetForm,
)

def index(request):
    page = request.GET.get('page', None)
    customer_objs = Customer.objects.all()

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
        customer_objs = customer_objs.filter(account_number__contains=q)
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