"""cdmtel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from cdmsoro.views.views import PermintaanBukisView as BukisView
from cdmsoro.views.views import circuitListView as home_view

from django.contrib.auth.views import LoginView, LogoutView

from masterdata import views  as master_views
from core.forms import LoginForm as CoreLogin

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admingo/', admin.site.urls),
    path('cdm/', include('cdmsoro.urls')),
    path('bjt/', include('collection.urls')),
    path('som/', include('som.urls')),
    path('koreksi/', include('koreksi.urls')),



    path('bulk-update/', master_views.order_bulk_update_view, name='bulk_update'),
    path('daily-record/', master_views.daily_record_view, name='daily'),
    path('acc-record/', master_views.record_account_view, name='acc_record'),
    path('daily-contrak-so/', master_views.daily_record_contrak_so, name='so_contrak'),
]


if not settings.DEBUG:
    urlpatterns +=  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns +=  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)