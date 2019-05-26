from background_task import background
from django.conf import settings
from django.template.loader import render_to_string

from userprofile.models import Profile

from cdmsoro.models import (
    PermintaanResume, ManualOrder, Validation
)

from masterdata.models import Order
import requests, json


@background(schedule=3)
def notify_new_request(req_id, channel):
    instance = PermintaanResume.objects.get(pk=req_id)
    url = "https://api.telegram.org/bot{}/".format(settings.TELEGRAM_KEY)
    
    payload = {
        "chat_id": channel,
        "parse_mode": "HTML",
        "text": "[+ Validasi] %s %s.\n<a href='http://10.35.31.78/som/persume-book/%d/'>Link</a>" %(instance.sid.sid, instance.executor.profile.telegram_user, instance.id)
    }

    try:
        requests.post(url=url+'sendMessage', data=payload, timeout=15)
    except:
        pass

@background(schedule=3)
def notifi_validation_req(req_id):
    instance = PermintaanResume.objects.get(pk=req_id)
    url = "https://api.telegram.org/bot{}/".format(settings.TELEGRAM_KEY)
    receiver_id = settings.REMOT_TELEHOST

    payload = {
        "chat_id": receiver_id,
        "parse_mode": "HTML",
        "text": "[+ RO] Mohon bukis %s %s.\n<a href='http://10.35.31.78/cdm/monitor/%d/'>Link</a>" %(instance.sid.sid, instance.executor.profile.telegram_user, instance.id)
    }

    try:
        requests.post(url=url+'sendMessage', data=payload, timeout=15)
    except:
        pass


@background(schedule=1)
def sending_telegram(data_id, token, send_to):
    order_obj = Order.objects.get(pk=data_id)
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(token)
    msg = 'Dear team SORO, mohon bantuan order berikut karena masih belum complete'
    payload = {
        'chat_id': send_to,
        'text': render_to_string('cdmsoro/v2/includes/sending-telegram.html', {'order': order_obj, 'msg':msg}),
        'parse_mode': 'HTML'
    }
    try :
        r = requests.post(url, data=payload, timeout=15)
    except:
        pass



@background(schedule=1)
def sending_to_pic(data_id, token, send_to):
    obj = PermintaanResume.objects.get(pk=data_id)
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(token)
    msg = 'Request <b>Approved</b>\nTelah bukis layanan oleh permintaan {},\nSID : {}\nSO : {}\nRO : {}.'.format(
        obj.pic,
        obj.sid.sid,
        obj.suspend.order_number,
        obj.resume.order_number,
    )
    
    payload = {
        'chat_id': send_to,
        'text': msg,
        'parse_mode': 'HTML'
    }
    try :
        r = requests.post(url, data=payload, timeout=15)
    except:
        pass

@background(schedule=1)
def sending_notif_manual_ro(data_id, token, send_to):
    obj = ManualOrder.objects.get(pk=data_id)
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(token)
    msg = 'Request <b>Approved</b>\nTelah bukis manual oleh permintaan {},\nSID : {}\nSO : {}\nRO : {}\nKet. : {}.'.format(
        obj.permintaan_resume.pic,
        obj.permintaan_resume.sid.sid,
        obj.permintaan_resume.suspend.order_number,
        'MANUAL RO OCS/FFM',
        obj.message
    )
    payload = {
        'chat_id': send_to,
        'text': msg,
        'parse_mode': 'HTML'
    }
    try :
        r = requests.post(url, data=payload, timeout=15)
    except:
        pass


@background(schedule=1)
def reject_notification(data_id, send_to):
    obj = Validation.objects.get(pk=data_id)
    url = 'https://api.telegram.org/bot{}/sendMessage'.format(settings.TELEGRAM_KEY)
    msg = 'Request <b>{}</b>\nSID : {}\nFollow link <a href="http://10.35.31.78/?q={}">here</a>\n{}'.format(
        obj.get_action_display().title(),
        obj.permintaan_resume.sid.sid,
        obj.permintaan_resume.sid.sid,
        obj.permintaan_resume.pic,
    )
    payload = {
        'chat_id': send_to,
        'text': msg,
        'parse_mode': 'HTML'
    }
    try :
        r = requests.post(url, data=payload, timeout=15)
    except:
        pass