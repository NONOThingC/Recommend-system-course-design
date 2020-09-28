from django.contrib import admin
from django.urls import path
from login import views
from django.conf.urls import include

app_name="login"

urlpatterns = [
    # path(r'mysite/',include('login.urls',namespace='login')),
]