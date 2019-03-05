from django.db import models
from django.contrib.auth.models import User

from masterdata.models import Customer
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


class AvidenttargetCol(CommonBase):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, related_name='avident_col')
    doc = models.FileField(max_length=200, upload_to='collection/file/')
    message = models.TextField(max_length=500, blank=True)