#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.discounts import views
from astutedashboard.dashboards.billing.discounts import views


urlpatterns = [

    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

    url(
        r'^create_billing_discount/$',
        views.CreateBillingDiscountMappingView.as_view(),
        name='create_billing_discount'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_billing_discount/$',
        views.ModifyBillingDiscountMappingView.as_view(),
        name='modify_billing_discount'
    ),

    url(
        r'^account_plan_mappings$',
        views.account_plan_mappings,
        name='account_plan_mappings'
    ),

]
