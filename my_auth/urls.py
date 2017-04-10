from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login.html$', views.login),
    url(r'^auth.html$', views.auth),
    url(r'^hello.html$', views.hello),
]
