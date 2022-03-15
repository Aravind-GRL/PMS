"""purchase_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from module import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index',views.index),
    path('add',views.add),
    path('edit_users/<int:id>',views.edit_users),
    path('delete_users/<int:id>',views.edit_users),
    path('',views.main),
    path('user_list',views.user_list),
    path('pr_index',views.project_index),
    path('pu_index',views.purchase_index),
    path('change_status',views.change_status),
    path('update_delivery_date',views.update_delivery_date),
    path('upload_invoice',views.upload_invoice),
    path('login',views.login),
    path('logout',views.logout),
    path('registration',views.registration)
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
