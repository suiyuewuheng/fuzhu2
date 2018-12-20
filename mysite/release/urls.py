from django.conf.urls import url


from .import views,views01

urlpatterns = [
    url(r'^$', views01.first, name='home'),
    url(r'^firsh$',views01.first,name='first'),
    url(r'^index$',views01.index,name='index'),
    url(r'^bs_css/$',views.bs_css,name='bs_css'),
    # url(r'^(?P<qid>[0-9]+)/$',views01.detail,name='detail'),
    # url(r'^sayhello/(?P<student>\w+)/(?P<age>[0-9]+)/$',views01.sayhello,name='sayhello'),
    url(r'^aboutus/$', views01.aboutus, name='aboutus'),
    url(r'^loginpage/$',views01.loginpage,name='loginpage'),
    url(r'^checklogin/$',views01.checklogin,name='checklogin'),
    url(r'^pre_jobmenu/$',views01.pre_jobmenu,name='pre_jobmenu'),
    url(r'^jobmenu/$',views01.jobmenu,name='jobmenu'),
    url(r'^backup/$',views01.backup,name='backup'),
    url(r'^scan/$',views01.scan,name='scan'),
    url(r'^start_release$',views01.start_release,name='start_release'),
    url(r'^hosts/$',views01.hosts,name='hosts'),

]