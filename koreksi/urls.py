from django.urls import path

from . import views

app_name = 'koreksi'
urlpatterns = [
    path('', views.InputKoreksiListView.as_view(), name='input_koreksi'),
    path('simple-upload/', views.simple_upload, name='simple_upload'),
    path('export/', views.export, name='export'),
]