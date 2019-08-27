from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from core.models import CommonBase

import datetime

class Segment(CommonBase):
    segment = models.CharField(max_length=10, unique=True)
    saldo = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    class Meta:
        ordering = ['segment']

    def __str__(self):
        return self.segment

class Customer(CommonBase):
    EMPTY = 10
    WAIT_VALID = 1
    WAIT_APP = 2
    REJECT = 3
    APPROVE = 4

    LIST_STATUS = (
        (EMPTY, None),
        (WAIT_VALID, 'Waiting Validation'),
        (WAIT_APP, 'Waiting Approval'),
        (REJECT, 'Rejected'),
        (APPROVE, 'Approved')
    )

    account_number = models.CharField(max_length=8, unique=True)
    bp = models.CharField(max_length=30, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, blank=True, null=True, related_name='customer_list')
    fbcc = models.ForeignKey('FbccSegment', on_delete=models.CASCADE, blank=True, null=True)
    cur_saldo = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    is_valid = models.BooleanField(default=False)
    no_valid = models.BooleanField(default=False)
    has_target = models.BooleanField(default=False)
    has_validate = models.BooleanField(default=False)
    has_approve = models.BooleanField(default=False)
    last_update = models.DateTimeField(blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=LIST_STATUS, default=EMPTY)
    unlock = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.account_number

    def get_saldo(self):
        return self.customer_saldo.latest('timestamp')

    def get_validation(self):
        return self.bjt_cust_validate.latest('timestamp')

    def get_response_cdm(self):
        if self.has_approve:
            last_valid = self.bjt_cust_validate.latest('timestamp')
            last_approve = last_valid.approval_set.latest('timestamp')
            if last_approve.approve:
                return 'Approved'

        if self.has_validate:
            return 'Waiting Approval'

        if self.has_target:
            return 'Waiting Validate'
        
        last_valid = self.bjt_cust_validate.latest('timestamp')
        if last_valid.validate == 'RE':
            return 'Rejected'


class FbccSegment(CommonBase):
    segment = models.CharField(max_length=20)

    def __str__(self):
        return self.segment


class Circuit(CommonBase):
    sid = models.CharField(max_length=30, unique=True)
    account = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.sid

    def get_suspend_order(self):
        return self.order_set.filter(type_order='SO', publish=True).latest('timestamp')

    def get_last_order(self):
        return self.order_set.filter(publish=True).latest('timestamp')

    def get_permit_bukis(self):
        return self.permin_bukis.filter(closed=False).latest('timestamp')

    def is_active_order(self):
        if self.get_last_order():
            return True and (self.get_last_order().type_order != 'SO')
        return True


class Order(CommonBase):
    TGK = 1
    CONT = 2
    LIST_LABEL = (
        (TGK, 'Tunggakan'),
        (CONT, 'End Contract')
    )
    RESUME = 'RO'
    SUSPEND = 'SO'
    TYPE_LIST = (
        (SUSPEND, 'SUSPEND'),
        (RESUME, 'RESUME')
    )
    order_number = models.CharField(max_length=13, unique=True)
    type_order = models.CharField(max_length=2, choices=TYPE_LIST, default=SUSPEND)
    status = models.CharField(max_length=100, blank=True)
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    order_label = models.PositiveSmallIntegerField(choices=LIST_LABEL, default=1)
    dbcreate_on = models.DateTimeField(default=timezone.now)
    dbcreate_by = models.CharField(max_length=100, blank=True)
    closed = models.BooleanField(default=False)
    is_cancel = models.BooleanField(default=False)
    publish = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.order_number

    def get_sid(self):
        return self.circuit.sid

    def get_account(self):
        return self.circuit.account.account_number

    def get_status_order(self):
        if self.is_cancel:
            return 'CANCELED ORDER'
        return self.status


class BackgTaskUpdate(CommonBase):
    BJT = 'BJT'
    REQSO = 'RSO'
    CONTSO = 'CSO'
    ORSTATUS = 'STA'

    LISTBG = (
        (BJT, 'BJT UPDATE'),
        (REQSO, 'RECORD ORDER'),
        (ORSTATUS, 'STATUS ORDER'),
        (CONTSO, 'SO CONTRACT'),
    )
    typetask = models.CharField(max_length=3, choices=LISTBG)


class CancelOrder(models.Model):
    order_num = models.CharField(max_length=20)

    def __str__(self):
        return self.order_num