from django.db import models

from django.contrib.auth.models import User

from core.models import CommonBase
from masterdata.models import FbccSegment

class Profile(CommonBase):
    VALIDATOR = 'VD'
    EXECUTOR = 'EX'
    CUSTOMER = 'CU'

    GROUP_LIST = (
        (VALIDATOR, 'Validator'),
        (EXECUTOR, 'Executor'),
        (CUSTOMER, 'Customer')
    ) 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.CharField(max_length=2, choices=GROUP_LIST, default=CUSTOMER)
    fbcc = models.ForeignKey(FbccSegment, on_delete=models.CASCADE, blank=True, null=True)
    telegram_user = models.CharField(max_length=200, blank=True)
    counter = models.PositiveIntegerField(default=0)

    def get_fullname(self):
        return '{} {}',format(self.user.first_name, self.user.profile.last_name)