from django.db import models

from django.contrib.auth.models import User

from core.models import CommonBase

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
    counter = models.PositiveIntegerField(default=0)
