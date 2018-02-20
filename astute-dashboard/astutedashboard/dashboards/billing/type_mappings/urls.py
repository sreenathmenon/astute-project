#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.type_mappings import views
from astutedashboard.dashboards.billing.type_mappings import views


urlpatterns = [

    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

    url(
        r'^billing_create_account/$',
        views.CreateAccountView.as_view(),
        name='billing_create_account'
    ),

    url(
        r'^(?P<id>[^/]+)/billing_update_account/$',
        views.UpdateAccountView.as_view(),
        name='billing_update_account'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_volume_type_quotas/$',
        views.ModifyVolumeTypeQuotasView.as_view(),
        name='modify_volume_type_quotas'
    ),

    url(
        r'^(?P<id>[^/]+)/resend_welcome_letter/$',
        views.email,
        name='resend_welcome_letter'
    ),

]
