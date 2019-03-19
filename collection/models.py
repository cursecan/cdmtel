from django.db import models
from django.contrib.auth.models import User

from masterdata.models import (
    Customer, Segment
)
from core.models import CommonBase

class ColTarget(CommonBase):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='coltarget_customer')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    due_date = models.DateField()
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='coltarget_creator')

    class Meta:
        ordering = ['due_date']
        
    def __str__(self):
        return str(self.customer)


class Saldo(CommonBase):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_saldo')
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.customer)


class ColSegment(CommonBase):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='colsegment')
    period = models.DateField()
    piutang = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    td_tagih = models.DecimalField(max_digits=12, decimal_places=0, default=0)


class AvidenttargetCol(CommonBase):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, related_name='avident_col')
    doc = models.FileField(max_length=200, upload_to='collection/file/')
    message = models.TextField(max_length=500, blank=True)


class Validation(CommonBase):
    REJECT = 'RE'
    APPROVE = 'AP'
    LIST_VALIDATE = (
        (REJECT, 'REJECT'),
        (APPROVE, 'APPROVE')
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bjt_cust_validate', blank=True, null=True)
    validate = models.CharField(max_length=2, choices=LIST_VALIDATE)
    msg = models.TextField(max_length=500)