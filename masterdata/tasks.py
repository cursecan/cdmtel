from background_task import background
from django.contrib.auth.models import User
from django.conf import settings
from .models import (
    Order, Customer, Circuit
)

import cx_Oracle

@background(schedule=3)
def bulk_order_update():
    cdmorder_objs = Order.objects.filter(closed=False).values_list('order_number')
    con = cx_Oracle.connect(settings.ORACLE_USER, settings.ORACLE_PASS, settings.ORACLE_SERVICE)
    cur = con.cursor()
    query = """
        SELECT DISTINCT\
        T1.milestone_code AS MILESTONE,\
        T1.service_num AS SID_NUM,\
        T2.order_num AS ORDER_NUM,\
        T2.rev_num AS REV,\
        T4.attrib_05 AS ORDER_SUBTYPE,\
        T5.x_pti1_accnt_nas AS ACCNAS\
        FROM\
            sblprd.s_order_item T1\
        LEFT JOIN sblprd.s_order T2 ON\
            T2.row_id = T1.order_id\
        LEFT JOIN sblprd.s_order_x T4 ON\
            T4.par_row_id = T2.row_id\
        LEFT JOIN sblprd.s_org_ext T5 ON\
            T5.row_id = T2.bill_accnt_id\
        LEFT JOIN SBLPRD.S_USER T9 ON\
            T1.CREATED_BY = T9.ROW_ID\
        WHERE T9.LOGIN IN ('710045', 'CDAS041188', 'CDHH171076', 'ESFM290596')\
        AND T1.service_num IS NOT NULL
    """
    cur.execute(query)
    datas = cur.fetchall()
    cur.close()
    con.close()

    dict_data = dict()
    for data in datas:
        if data[2] not in dict_data:
            dict_data[data[2]] = (data[0], data[3]) # status dan seq
        else :
            if data[3] > dict_data[data[2]][1]:
                try :
                    dict_data[data[2]] = (data[0], data[3])
                except:
                    pass

    for order in cdmorder_objs:
        get_order = dict_data.get(order[0], None)
        if get_order:
            if get_order[0] is not None and get_order[0] != '':
                order_obj = Order.objects.filter(order_number=order[0])
                if get_order[0] == 'FULFILL BILLING COMPLETE':
                    Order.objects.filter(order_number=order[0]).update(
                        status = get_order[0], closed=True
                    )
                else:
                    Order.objects.filter(order_number=order[0]).update(
                        status = get_order[0]
                    )


@background(schedule=1)
def record_data():
    con = cx_Oracle.connect(settings.AMDES_USER, settings.AMDES_PASS, settings.AMDES_SERVICE)
    cur = con.cursor()
    query = """
        SELECT DISTINCT accountnas, li_sid, order_id, li_milestone, order_created_date, \
        CASE \
            WHEN li_createdby_name='SETIAWAN, ANDERI' THEN 'anderi' \
            WHEN li_createdby_name='MAHARANI, FRISA' THEN 'frisa' \
            WHEN li_createdby_name='SABARUDIN, RAHMAT' THEN '710045' \
            ELSE 'hane' \
        END createdby \
        FROM eas_ncrm_agree_order_line@dbl_dwh_sales_aon \
        WHERE order_subtype='Suspend' \
        AND li_createdby_name IN ('MAHARANI, FRISA', 'SETIAWAN, ANDERI', 'SABARUDIN, RAHMAT', 'HASANUDIN, HANE') \
        AND li_sid IS NOT NULL \
        AND ORDER_CREATED_DATE >= TO_DATE('20190101', 'YYYYMMDD') \
        AND LI_SID NOT LIKE '%X%' \
        AND li_milestone IS NOT NULL
    """
    
    cur.execute(query)
    datas = cur.fetchall()
    cur.close()
    con.close()

    for i in datas:
        account, sid, order, status, create_on, create_by = i
        user_obj = User.objects.get(username=create_by)
        try :
            acc_obj, create = Customer.objects.get_or_create(account_number=account)
            sid_obj, create = Circuit.objects.get_or_create(sid=sid, account=acc_obj)
            order_obj, create = Order.objects.get_or_create(order_number=order, circuit=sid_obj, create_by=user_obj)
            order_obj.status = status
            if status == 'FULFILL BILLING COMPLETE':
                order.closed = True
            order_obj.save()
        except :
            pass