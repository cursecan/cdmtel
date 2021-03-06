from django.urls import path

from . import views

app_name = 'som'
urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.bukisDashboard, name='bukis_dashboard'),
    path('persume-books/', views.unclosePerminBukisView, name='unlose_persume'),
    path('persume-book/<int:id>/', views.unclosePerminDetail, name='unclose_detail'),
    path('manual-books/', views.manualBukisListView, name='manual_unclosed'),
    path('books/', views.recordBukisListView, name='bukis_books'),
    path('report/', views.soroReportView, name='report'),
    path('order-list/', views.OrderView.as_view(), name='order_list'),

    path('ipay/<int:id>/', views.iPaymentView, name='ipayment'),
    path('api/docs/<int:id>/', views.documentUploadView, name='doc_list'),

]