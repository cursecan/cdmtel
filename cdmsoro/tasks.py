from background_task import background
from django.conf import settings

from userprofile.models import Profile

from cdmsoro.models import PermintaanResume
import requests, json


@background(schedule=3)
def notify_new_request(req_id):
    instance = PermintaanResume.objects.get(pk=req_id)
    url = "https://api.telegram.org/bot{}/".format(settings.TELEGRAM_KEY)
    receiver_id = settings.REMOT_TELEHOST
    validator_obj = Profile.objects.filter(group='VD').values_list('telegram_user')
    validators = [i[0] for i in list(validator_obj)]

    payload = {
        "chat_id": receiver_id,
        "parse_mode": "HTML",
        "text": "[+ Validasi] %s %s.\n<a href='http://10.35.31.78/cdmsoro/validasi/%d/'>Link</a>" %(instance.sid.sid, ' '.join(validators), instance.id)
    }

    try:
        requests.post(url=url+'sendMessage', data=payload)
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
        "text": "[+ RO] Mohon bukis %s %s.\n<a href='http://10.35.31.78/cdmsoro/monitor/%d/'>Link</a>" %(instance.sid.sid, instance.executor.profile.telegram_user, instance.id)
    }

    try:
        requests.post(url=url+'sendMessage', data=payload)
    except:
        pass
