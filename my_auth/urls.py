from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login', views.login),
    url(r'^auth.html$', views.auth),
   # url(r'^hello.html$', views.send),
    url(r'^login.html$', views.log),
    url(r'^bid.html$', views.bid),
    url(r'^send_bid', views.send_bid),
    url(r'^list/$', views.list),
]
