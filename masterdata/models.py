from django.db import models
from django.contrib.auth.models import User

from core.models import CommonBase

class Segment(CommonBase):
    segment = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['segment']

    def __str__(self):
        return self.segment

class Customer(CommonBase):
    account_number = models.CharField(max_length=8, unique=True)
    bp = models.CharField(max_length=30, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.account_number



class Circuit(CommonBase):
    sid = models.CharField(max_length=30, unique=True)
    account = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.sid

    def get_suspend_order(self):
        return self.order_set.filter(type_order='SO').latest('timestamp')

    def get_last_order(self):
        return self.order_set.latest('timestamp')    


class Order(CommonBase):
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
    closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.order_number

    def get_sid(self):
        return self.circuit.sid

    def get_account(self):
        return self.circuit.account.account_number