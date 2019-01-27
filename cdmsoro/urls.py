from django.urls import path

from . import views


app_name = 'cdmsoro'
urlpatterns = [
    path('', views.index, name='index'),
    path('request-bukis/', views.PermintaanBukisView.as_view(), name='bukis'),
    path('request-bukis/<int:id>/', views.UpdatePermintaanView.as_view(), name='detail_bukis'),
    path('validasi/', views.UnValidateBukisView.as_view(), name='unvalidate'),
    path('validasi/<int:id>/', views.detailUnvalidateView, name='detail_unvalidate'),
    path('monitor/', views.ValidateInactionView.as_view(), name='bukis_action'),
    path('monitor/<int:id>/', views.detailValidateActionView, name='bukis_action_detail'),
    path('unclose-order/', views.UclosedOrderView.as_view(), name='unclose_order'),
]