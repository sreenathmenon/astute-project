#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.config import views
from astutedashboard.dashboards.billing.config import views


urlpatterns = [

    # Billing Types config
    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

    url(
        r'^create_billing_type/$',
        views.CreateBillingTypeView.as_view(),
        name='create_billing_type'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_billing_type/$',
        views.ModifyBillingTypeView.as_view(),
        name='modify_billing_type'
    ),

    # Service Types config
    url(
        r'^create_service_type/$',
        views.CreateServiceTypeView.as_view(),
        name='create_service_type'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_service_type/$',
        views.ModifyServiceTypeView.as_view(),
        name='modify_service_type'
    ),

    # Discounts config
    url(
        r'^create_discount/$',
        views.CreateDiscountView.as_view(),
        name='create_discount'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_discount/$',
        views.ModifyDiscountView.as_view(),
        name='modify_discount'
    ),

    # Plans config
    url(
        r'^create_plan/$',
        views.CreatePlanView.as_view(),
        name='create_plan'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_plan/$',
        views.ModifyPlanView.as_view(),
        name='modify_plan'
    ),

]
