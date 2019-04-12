from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from background_task.tasks import Task
from django.utils import timezone

from .models import Order
from .tasks import (
    bulk_order_update, record_data,
    get_record_account, record_data_contrak
)

import datetime

today = timezone.now()
expired_date = today + datetime.timedelta(weeks=60)

def order_bulk_update_view(request):
    order_obj = Order.objects.filter(closed=False)
    if order_obj.exists():
        bulk_order_update(repeat=10000, repeat_until=expired_date)
        
    return JsonResponse({'process_order': order_obj.count()})


def daily_record_view(request):
    record_data(repeat=10000, repeat_until=expired_date)
    return JsonResponse({'daily_record': '1'})


def daily_record_contrak_so(request):
    record_data_contrak(repeat=10000, repeat_until=expired_date)
    return JsonResponse({'daily_contrak': 1})


def record_account_view(request):
    get_record_account(repeat=10000, repeat_until=expired_date)
    return JsonResponse({'daily_record': '1'})

