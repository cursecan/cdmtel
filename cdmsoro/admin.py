from django.contrib import admin

from .models import (
    PermintaanResume, UpdatePermintaan,
    Validation, Avident
)

@admin.register(PermintaanResume)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass

@admin.register(UpdatePermintaan)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass

@admin.register(Validation)
class PermintaanResumeAdmin(admin.ModelAdmin):
    pass


@admin.register(Avident)
class AvidentAdmin(admin.ModelAdmin):
    pass

        
        
# class PermintaanResume(CommonBase):
#     pic = models.CharField(max_length=15)
#     message = models.TextField(max_length=500, blank=True)
#     sid = models.ForeignKey(Circuit, on_delete=models.CASCADE)
#     suspend = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='suspend_order')
#     resume = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='resume_order')
#     validate = models.BooleanField(default=False)
#     avident = models.FileField(max_length=200 ,upload_to='file/avident/')
#     executor = models.ForeignKey(User, on_delete=models.CASCADE, default=1)


#     class Meta:
#         ordering = ['update', 'timestamp']

#     def __str__(self):
#         return self.sid


# class UpdatePermintaan(CommonBase):
#     permintaan_resume = models.ForeignKey(PermintaanResume, on_delete=models.CASCADE)
#     message = models.TextField(max_length=500, blank=True)
#     avident = models.FileField(max_length=200 ,upload_to='file/avident/')

#     def __str__(self):
#         return self.permintaan_resume


# class Validation(CommonBase):
#     APPROVE = 'APP'
#     DECLINE = 'DEC'
#     ACTION_LIST = (
#         (APPROVE, 'APPROVED'),
#         (DECLINE, 'DECLINED')
#     )
#     message = models.TextField(max_length=500)
#     action = models.CharField(max_length=3, choices=ACTION_LIST, default=DECLINE)
#     permintaan_resume = models.ForeignKey(PermintaanResume, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

#     def __str__(self):
#         return self.permintaan_resume