from django.conf.urls import url

from roadmap import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^organisation/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<organisation_id>[0-9]+)/$', views.organisation, name='organisation'),
    url(r'^organisation/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<organisation_id>[0-9]+)/load/$', views.organisation_load, name='organisation_load'),
    url(r'^mark/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<mark_id>[0-9]+)/$', views.mark, name='mark'),
    url(r'^mark/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<mark_id>[0-9]+)/load/$', views.mark_load, name='mark_load'),
    url(r'^value_save/$', views.value_save, name='value_save'),
    url(r'^report_create/$', views.report_create, name='report_create'),
    url(r'^checkin/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/$', views.checkin, name='checkin'),
    url(r'^checkin/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/load/$', views.checkin_load, name='checkin_load'),
]
