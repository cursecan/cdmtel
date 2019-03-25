from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from background_task.tasks import Task
from django.utils import timezone

from .models import Order
from .tasks import (
    bulk_order_update, record_data,
    get_record_account
)

import datetime

today = timezone.now()
expired_date = today + datetime.timedelta(years=1)

def order_bulk_update_view(request):
    order_obj = Order.objects.filter(closed=False)
    if order_obj.exists():
        bulk_order_update(repeat=50000, repeat_until=expired_date)
        
    return JsonResponse({'process_order': order_obj.count()})


def daily_record_view(request):
    record_data(repeat=30000, repeat_until=expired_date)
    return JsonResponse({'daily_record': '1'})


def record_account_view(request):
    get_record_account(repeat=50000, repeat_until=expired_date)
    return JsonResponse({'daily_record': '1'})

