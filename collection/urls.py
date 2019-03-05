from django.urls import path

from . import views

app_name = 'collection'
urlpatterns = [
    path('', views.index, name='index'),
    path('customer-detail/<int:id>/', views.custCollectDetailView, name='customer_detail'),
    path('entry-data/', views.entryDataView, name='entry_data'),
    path('validation/', views.collectionValidationView, name='validation'),
    path('validation/<int:id>/', views.detailColValidationView, name='detail_validation'),

    path('api/customer/', views.jsonCustomerView, name='api_customer'),
    path('api/customer/dettail/<int:id>/', views.jsonCustomerDetailJtempo, name='api_detail_customer'),
    path('api/customer/upload-doc/<int:id>/', views.jsonUploadDocView, name='customer_upload'),

]