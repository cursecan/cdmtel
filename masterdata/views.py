from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count

from .models import Order
from .tasks import (
    bulk_order_update, record_data
)

def order_bulk_update_view(request):
    order_obj = Order.objects.filter(closed=False)
    if order_obj.exists():
        bulk_order_update()
        
    return JsonResponse({'process_order': order_obj.count()})


def daily_record_view(request):
    record_data()
    return JsonResponse({'daily_record': '1'})
