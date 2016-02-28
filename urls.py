from django.conf.urls import url

from roadmap import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^organisation/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<organisation_id>[0-9]+)/$', views.organisation, name='organisation'),
    url(r'^organisation/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<organisation_id>[0-9]+)/load/$', views.organisation_load, name='organisation_load'),
    url(r'^organisation/(?P<report_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<organisation_id>[0-9]+)/save/$', views.organisation_save, name='organisation_save'),
]