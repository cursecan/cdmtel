from django.db import models
from django.contrib.auth.models import User

from core.models import CommonBase
from masterdata.models import (
    Circuit, Order, Customer
)
 

class PermintaanResume(CommonBase):
    REJECT = 1
    APPROVE = 2
    WAITING = 3
    LIST_STATUS = (
        (REJECT, 'Rejected'),
        (APPROVE, 'Approved'),
        (WAITING, 'Process Validation')
    )
    pic = models.CharField(max_length=100)
    message = models.TextField(max_length=500, blank=True)
    sid = models.ForeignKey(Circuit, on_delete=models.CASCADE, related_name='permin_bukis')
    suspend = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='suspend_order')
    resume = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='resume_order')
    validate = models.BooleanField(default=False)
    executor = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    manual_bukis = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=LIST_STATUS, default=WAITING)
    closed = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False)


    class Meta:
        ordering = ['-update', '-status']

    def __str__(self):
        return str(self.sid)

    def get_validation(self):
        return self.validation_set.filter(closed=False).latest('timestamp')

    def is_approved(self):
        return self.get_validation().action == 'APP'

    def has_telegram(self):
        if self.pic[0] == '@':
            return self.pic[1:]
        return None

    def get_error_msg(self):
        if self.manual_bukis:
            return self.manualorder.message
        return None


class ManualOrderSoro(CommonBase):
    ISOLIR = 'SO'
    RESUME = 'RO'
    ORDERTYPE_LIST = (
        (ISOLIR, 'ISOLIR'),
        (RESUME, 'RESUME')
    )
    order_number = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    sid = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=2, choices=ORDERTYPE_LIST)
    keterangan = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['-timestamp']


class ManualOrder(CommonBase):
    permintaan_resume = models.OneToOneField(PermintaanResume, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)


class UpdatePermintaan(CommonBase):
    permintaan_resume = models.ForeignKey(PermintaanResume, on_delete=models.CASCADE, related_name='update_permin_bukis')
    message = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return str(self.permintaan_resume)

    class Meta:
        ordering = [
            'timestamp'
        ]


class Avident(models.Model):
    leader = models.ForeignKey(PermintaanResume, on_delete=models.CASCADE)
    document = models.FileField(max_length=200 ,upload_to='file/avident/')


class Validation(CommonBase):
    APPROVE = 'APP'
    DECLINE = 'DEC'
    ACTION_LIST = (
        (APPROVE, 'APPROVED'),
        (DECLINE, 'REJECTED')
    )
    message = models.TextField(max_length=500, default='Approved!')
    action = models.CharField(max_length=3, choices=ACTION_LIST, default=DECLINE)
    permintaan_resume = models.ForeignKey(PermintaanResume, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.permintaan_resume)


    class Meta:
        ordering = [
            '-timestamp'
        ]