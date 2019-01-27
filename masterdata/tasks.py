from background_task import background
from .models import Order

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
