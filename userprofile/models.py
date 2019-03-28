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
    OFFICER = 'OF'
    MANAGER = 'MG'

    LEVEL_LIST = (
        (OFFICER, 'Officer'),
        (MANAGER, 'Manager')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.CharField(max_length=2, choices=GROUP_LIST, default=CUSTOMER)
    fbcc = models.ForeignKey(FbccSegment, on_delete=models.CASCADE, blank=True, null=True)
    telegram_user = models.CharField(max_length=200, blank=True)
    counter = models.PositiveIntegerField(default=0)
    multiple = models.PositiveSmallIntegerField(default=1)
    level = models.CharField(max_length=2, choices=LEVEL_LIST, default=OFFICER)
    superior = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='worker')

    def __str__(self):
        return self.user.username
        
    def get_fullname(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)