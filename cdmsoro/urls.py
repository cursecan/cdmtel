from django.urls import path

from .views import views, v2


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

    path('v2/', v2.index, name='v2_index'),
    path('v2/api/permintaan-bukis-detail/<int:id>/', v2.permin_bukis_detail_view, name='v2_per_bukis'),
    path('v2/api/uncomplete/', v2.uncomplete_order_view, name='v2_uncomplete'),
]