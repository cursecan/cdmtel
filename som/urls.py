from django.urls import path

from . import views

app_name = 'som'
urlpatterns = [
    path('', views.index, name='index'),
    path('persume-books/', views.unclosePerminBukisView, name='unlose_persume'),
    path('persume-book/<int:id>/', views.unclosePerminDetail, name='unclose_detail'),
    path('manual-books/', views.manualBukisListView, name='manual_unclosed'),
    path('books/', views.recordBukisListView, name='bukis_books'),

    path('api/docs/<int:id>/', views.documentUploadView, name='doc_list'),
]