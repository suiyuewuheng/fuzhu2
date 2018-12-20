from django.conf.urls import url
from . import views
urlpatterns=[
url(r'^login$',views.login,name='login'),
url(r'^act/$', views.act, name='act'),
# url(r'^act/$', views.act, name='cg'),
url(r'^content/$', views.content, name='content'),
url(r'^contact/$', views.contact, name='contact'),
url(r'^conthg/$', views.conthg, name='conthg'),
]
