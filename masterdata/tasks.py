from background_task import background
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, F, Value as V
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import (
    Order, Customer, Circuit, Segment, FbccSegment, BackgTaskUpdate
)
from collection.models import Saldo

import cx_Oracle

@background(schedule=3)
def bulk_order_update():
    cdmorder_objs = Order.objects.filter(closed=False).values_list('order_number')
    try :
        con = cx_Oracle.connect(settings.ORACLE_USER, settings.ORACLE_PASS, settings.ORACLE_SERVICE)
        cur = con.cursor()
        query = """
            SELECT DISTINCT \
            T1.milestone_code AS MILESTONE, \
            T1.service_num AS SID_NUM, \
            T2.order_num AS ORDER_NUM, \
            T2.rev_num AS REV, \
            T4.attrib_05 AS ORDER_SUBTYPE, \
            T5.x_pti1_accnt_nas AS ACCNAS, \
            T2.created, t2.status_cd \
            FROM \
                sblprd.s_order_item T1 \
            LEFT JOIN sblprd.s_order T2 ON \
                T2.row_id = T1.order_id \
            LEFT JOIN sblprd.s_order_x T4 ON \
                T4.par_row_id = T2.row_id \
            LEFT JOIN sblprd.s_org_ext T5 ON \
                T5.row_id = T2.bill_accnt_id \
            LEFT JOIN SBLPRD.S_USER T9 ON \
                T1.CREATED_BY = T9.ROW_ID \
            WHERE T9.LOGIN IN ('710045', 'CDAS041188', 'CDHH171076', 'ESFM290596', '900039') \
            AND T2.status_cd NOT IN ('Failed', 'Abandoned', 'Cancelled') \
            AND T2.created >= to_date('20190101','YYYYMMDD') \
            AND T1.service_num IS NOT NULL
        """
        cur.execute(query)
        datas = cur.fetchall()
        cur.close()
        con.close()

        dict_data = dict()
        for data in datas:
            # data from table
            # ['milestone', 'sid', 'order_num', 'rev', 'order_subtype', 'accnas', created_on, order_status]
            if data[2] not in dict_data:
                dict_data[data[2]] = (data[0], data[3], data[6], data[7]) # miles, seq, tgl, status_order
            else :
                if data[3] > dict_data[data[2]][1]:
                    try :
                        dict_data[data[2]] = (data[0], data[3], data[6], data[7])
                    except:
                        pass

        for order in cdmorder_objs:
            # unclose order list
            get_order = dict_data.get(order[0], None)
            if get_order:
                order_obj = Order.objects.filter(order_number=order[0], closed=False)
                if order_obj.exists():
                    if get_order[0] is not None and get_order[0] != '':
                        if get_order[0] == 'FULFILL BILLING COMPLETE':
                            order_obj.update(
                                status = get_order[0], dbcreate_on=get_order[2],
                                closed=True
                            )
                        else:
                            order_obj.update(
                                status = get_order[0], dbcreate_on=get_order[2]
                            )
                    else:
                        order_obj.update(
                            status = get_order[3], dbcreate_on=get_order[2]
                        )
                    
        
        BackgTaskUpdate.objects.create(typetask='STA')
    except:
        pass


@background(schedule=1)
def record_data():
    try:
        con = cx_Oracle.connect(settings.AMDES_USER, settings.AMDES_PASS, settings.AMDES_SERVICE)
        cur = con.cursor()
        query = """
            SELECT DISTINCT accountnas, li_sid, order_id, li_milestone, order_created_date, li_createdby_name \
            FROM eas_ncrm_agree_order_line@dbl_dwh_sales_aon \
            WHERE order_subtype='Suspend' \
            AND li_createdby_name IN ('CHALIL, MUNAWAR', 'MAHARANI, FRISA', 'SETIAWAN, ANDERI', 'SABARUDIN, RAHMAT', 'HASANUDIN, HANE') \
            AND ORDER_CREATED_DATE >= TO_DATE('20190101', 'YYYYMMDD') \
            AND LI_SID IS NOT NULL
        """
        
        cur.execute(query)
        datas = cur.fetchall()
        cur.close()
        con.close()

        for i in datas:
            account, sid, order, status, create_on, create_by = i
            try :
                acc_obj, create = Customer.objects.get_or_create(account_number=account)
                sid_obj, create = Circuit.objects.get_or_create(sid=sid, account=acc_obj)
                order_obj, create = Order.objects.get_or_create(order_number=order, circuit=sid_obj)
                order_obj.status = status if status else 'PENDING' 
                order_obj.dbcreate_by = create_by
                order_obj.dbcreate_on = create_on
                if status == 'FULFILL BILLING COMPLETE':
                    order_obj.closed = True
                order_obj.save()
            except :
                pass

        BackgTaskUpdate.objects.create(typetask='RSO')
    except:
        pass


@background(schedule=1)
def record_data_contrak():
    try:
        con = cx_Oracle.connect(settings.AMDES_USER, settings.AMDES_PASS, settings.AMDES_SERVICE)
        cur = con.cursor()
        query = """
            SELECT distinct \
            ACCOUNTNAS, \
            li_sid, \
            order_id, \
            li_milestone, \
            ORDER_CREATED_DATE, li_createdby_name \
            FROM \
            AMDES.NCRM_AGREE_ORDER_LINE \
            WHERE \
            li_sid IS NOT NULL \
            AND order_subtype IN ('Suspend') \
            AND ORDER_CREATEDBY_NAME IN ('Administrator, Siebel') \
            AND CHANGE_REASON_CD IN ('System Request') \
            AND CUST_SEGMEN like 'DES %' \
            AND ORDER_CREATED_DATE > TO_DATE('20190324', 'YYYYMMDD')
        """
        
        cur.execute(query)
        datas = cur.fetchall()
        cur.close()
        con.close()

        for i in datas:
            account, sid, order, status, create_on, create_by = i
            try :
                acc_obj, create = Customer.objects.get_or_create(account_number=account)
                sid_obj, create = Circuit.objects.get_or_create(sid=sid, account=acc_obj)
                order_obj, create = Order.objects.get_or_create(order_number=order, circuit=sid_obj)
                order_obj.status = status if status else 'PENDING' 
                order_obj.order_label = 2
                order_obj.dbcreate_by = create_by
                order_obj.dbcreate_on = create_on
                if status == 'FULFILL BILLING COMPLETE':
                    order_obj.closed = True
                order_obj.save()
            except :
                pass

        BackgTaskUpdate.objects.create(typetask='CSO')
    except:
        pass

@background(schedule=1)
def get_record_account():
    now = timezone.now()
    try :
        con = cx_Oracle.connect(settings.BILCOS_USER, settings.BILCOS_PASS, settings.BILCOS_SERVICE)
        cur = con.cursor()
        query = """
            SELECT \
                a.bp_num, \
                a.akun, \
                b.bpname, \
                a.CBASE_2016, \
                SUM(b.CURRENT_BALANCE) saldo, \
                a.FBCC_SEGMENT \
            FROM \
                z_des_openitem a \
            LEFT JOIN mybrains.trems_np_cyc b ON \
                a.bp_num = b.partner \
            GROUP BY \
                a.bp_num, \
                a.akun, \
                b.bpname,\
                a.CBASE_2016, \
                a.FBCC_SEGMENT
        """
        
        cur.execute(query)
        datas = cur.fetchall()
        cur.close()
        con.close()

        for i in datas:
            bpnum, acc, name, segmen, saldo, fbcc = i
            try :
                if int(acc) < 4000000:
                    acc = '0'+ acc

                seg_obj, create = Segment.objects.get_or_create(segment=segmen)
                fbcc_obj, create = FbccSegment.objects.get_or_create(segment=fbcc)

                cust_obj, create = Customer.objects.update_or_create(
                    account_number = acc,
                    defaults = {
                        'account_number': acc,
                        'bp': bpnum,
                        'customer_name': name,
                        'segment': seg_obj,
                        'fbcc': fbcc_obj,
                        'last_update': now
                    }
                )
                
                Saldo.objects.update_or_create(
                    customer = cust_obj,
                    timestamp__date = now.date(),
                    defaults = {
                        'customer': cust_obj,
                        'amount': saldo
                    } 
                )

            except:
                pass

        # Update For Account Segment
        Customer.objects.exclude(last_update=now).update(
            segment = None
        )

        segment_objs = Segment.objects.annotate(
            s = Coalesce(
                Sum('customer_list__cur_saldo'), V(0)
            )
        ).values('segment', 's')

        for i in segment_objs:
            Segment.objects.update_or_create(
                segment = i['segment'],
                defaults = {'saldo': i['s']}
            )

        BackgTaskUpdate.objects.create(typetask='BJT')

    except:
        pass