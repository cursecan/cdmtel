from django.urls import path

from . import views

app_name = 'collection'
urlpatterns = [
    path('', views.index, name='index'),
    path('entry-data/', views.entryDataView, name='entry_data'),

    path('api/customer/', views.jsonCustomerView, name='api_customer'),
    path('api/customer/dettail/<int:id>/', views.jsonCustomerDetailJtempo, name='api_detail_customer'),
]