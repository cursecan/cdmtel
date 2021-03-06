from django.db import models

from core.models import CommonBase
from masterdata.models import Customer


class InputKoreksi(CommonBase):
    WAIT = 1
    VALID = 2
    INVALID = 3
    LIST_STATE = (
        (WAIT, 'Waiting Validation'),
        (VALID, 'Valid'),
        (INVALID, 'Invalid'),
    ) 
    segmen = models.CharField(max_length=6)
    sbf_account = models.CharField(max_length=8)
    bp_number = models.CharField(max_length=8)
    customer_nm = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    sid = models.CharField(max_length=40)
    bandwidth = models.CharField(max_length=10, verbose_name='Bandwidth', blank=True)
    periode = models.CharField(max_length=6)
    amount = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=2)
    sudah_input_ncx = models.BooleanField(default=False)
    last_order = models.CharField(max_length=15, blank=True)
    type_last_order = models.CharField(max_length=2, blank=True)
    status_order = models.CharField(max_length=50, blank=True)
    abonemen = models.PositiveIntegerField(default=0)
    per_last_biling = models.CharField(max_length=6, blank=True)
    state = models.PositiveSmallIntegerField(choices=LIST_STATE, default=WAIT, editable=False)
    validate = models.BooleanField(default=False)
    error_text = models.CharField(max_length=255, blank=True)
    customer_obj = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='koreksi', blank=True, null=True)
    layanan = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = [
            '-timestamp'
        ]

    # def save(self, *args, **kwargs):

    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.sid 


class DocumentImportTemplate(models.Model):
    title = models.CharField(max_length=50)
    doc = models.FileField(upload_to='document/template/')
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return self.title