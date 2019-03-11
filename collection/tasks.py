from django.db.models import Q, F, Sum, Subquery, OuterRef, Value as V, DecimalField, ExpressionWrapper
from django.db.models.expressions import RawSQL
from django.db.models.functions import Coalesce 
from django.utils import timezone

from masterdata.models import (
    Customer, Segment
)

from .models import (
    ColTarget, ColSegment
)
import pendulum


def uppdate_resume_segment():
    cur_date = timezone.now().date()
    cdate = pendulum.date(cur_date.year, cur_date.month, 1)
    sm = dict()
    for i in range(6):
        segment_td_tagih = Segment.objects.exclude(segment='TDS').annotate(
            td_tagih = Coalesce(
                Sum('customer_list__coltarget_customer__amount', filter=Q(customer_list__cur_saldo__gt=0) & Q(customer_list__coltarget_customer__due_date__gte=cdate)), V(0)
            )
        ).values('segment', 'td_tagih')

        for s in list(segment_td_tagih):
            segment_obj = Segment.objects.get(segment=s['segment'])
            ColSegment.objects.update_or_create(
                segment = segment_obj,
                period = cdate,
                defaults = {'td_tagih': s['td_tagih'], 'segment': segment_obj, 'period': cdate }
            )
        
        cdate = cdate.add(months=1) 

    segment_saldos = Segment.objects.exclude(segment='TDS').annotate(
        s_saldo = Coalesce(Sum('customer_list__cur_saldo', filter=Q(customer_list__cur_saldo__gt=0)), V(0)),
    ).values('segment', 's_saldo')

    print(list(segment_saldos))

    # for s in list(segment_saldos):
    #     ColSegment.objects.update_or_create(
    #         segment__segment = s['segment'],
    #         defaults = {'piutang': s['s_saldo']}
    #     )
