#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.plan_mappings import views
from astutedashboard.dashboards.billing.image_report import views


urlpatterns = [

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^search_filter$', views.search_filter, name='search_filter'),
    url(r'^export_as_csv$', views.export_as_csv, name='export_as_csv'),
]


