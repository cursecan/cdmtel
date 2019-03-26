from django.urls import path

from . import views

app_name = 'collection'
urlpatterns = [
    path('', views.index, name='index'),
    path('segmen/', views.segmentTempView, name='segmen'),
    path('customer/', views.accountTemplView, name='account'),
    path('customer-detail/<int:id>/', views.custCollectDetailView, name='customer_detail'),
    path('entry-data/', views.entryDataView, name='entry_data'),
    path('validation/', views.collectionValidationView, name='validation'),
    path('validation/<int:id>/', views.detailColValidationView, name='detail_validation'),

    path('api/segment-list', views.json_SegmentListView, name='api_segment_list'),
    path('api/segment/', views.json_SegmentCollecView, name='api_segment'),
    path('api/customer-list/', views.json_accountCollecView, name='api_customer_list'),
    path('api/customer/', views.jsonCustomerView, name='api_customer'),
    path('api/customer/dettail/<int:id>/', views.jsonCustomerDetailJtempo, name='api_detail_customer'),
    path('api/customer/upload-doc/<int:id>/', views.jsonUploadDocView, name='customer_upload'),
    path('api/validation-list/<int:id>/', views.json_validation_record_list, name='validation_list_record'),


]