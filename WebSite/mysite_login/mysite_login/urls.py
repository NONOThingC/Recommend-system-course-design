"""mysite_login URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from login import views
from django.conf.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'login/', views.login),
    path('',views.index1),
    path(r'register/', views.register),
    path(r'logout/', views.logout),
    path(r'message/', views.message),
    path(r'change/', views.change),
    path(r'captcha',include('captcha.urls')),
    path(r'contact.html', views.contact),
    path(r'places.html/<flag>/<type>', views.places),
    path(r'index.html', views.index1,name='index'),
    path(r'register.html', views.register1),
    path(r'change.html', views.change1),
    path(r'search_result.html/<flag>/<moviename>', views.search_result),
    path(r'home.html/<flag>',views.home),
    path(r'admin_home.html/<flag>',views.admin_home),
    path(r'delete_comment.html/<moviename>/<id>',views.delete_comment),
    # path(r'mysite/',include(('mysite_login.urls',"mysite_login"),namespace='mysite_login')),
]
