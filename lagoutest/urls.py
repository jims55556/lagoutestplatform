"""lagoutest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from testplatform.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', index),
    url('index/', index),
    url('logout/', logout),
    url(r'/project/', project_index),
    url(r'/project_add/', project_add),
    url(r'/project_update/', project_update),
    url(r'/project_delete/', project_delete),
    url(r'/interface/', interface_index),
    url(r'/interface_add/', interface_add),
    url(r'/interface_delete/', interface_delete),
    url(r'/interface_update/', interface_update),
    url(r'/case/', case_index),
    url(r'/case_add/', case_add),
    url(r'/case_run/', case_run),
    url(r'/register/', register),
    url(r'/login/', login),
    url(r'/sign/', sign_index),
    url(r'/sign_add/', sign_add),
    url(r'/sign_update/', sign_update),
    url(r'/env/', env_index),
    url(r'/env_add/', env_add),
    url(r'/env_update/', env_update),
    url(r'/env_delete/', env_delete),
    url(r'/plan/', plan_index),
    url(r'/plan_add/', plan_add),
    url(r'/plan_run/', plan_run),
    url(r'/report/', report_index),
    url(r'/findata/', findata)
]
