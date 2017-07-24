from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^auth.html$', views.auth),
   # url(r'^hello.html$', views.send),
    url(r'^login.html$', views.log),
    url(r'^logout', views.logout),
    url(r'^bid.html$', views.bid),
    url(r'^bid$', views.bid),
    url(r'^send_bid', views.send_bid),
    url(r'^list/$', views.list),
    url(r'^listing/([0-9a-zA-Z]+)/$',views.listing),
    #url(r'^list/([0-9a-zA-Z]+)/$',list_detail),
    url(r'^hello$', views.hello),
    url(r'^bidding/([0-9a-zA-Z]+)/$',views.bidding),
    url(r'^bid_price',views.bid_price),
    url(r'^test',views.test),
    url(r'^re_auth$',views.re_auth),
    url(r'^send_auth$',views.send_auth),
    url(r'^settlement/([0-9a-zA-Z]+)/$', views.settlement),
]
