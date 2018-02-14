#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.plan_mappings import views
from astutedashboard.dashboards.billing.plan_mappings import views


urlpatterns = [

    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

		url(
				r'^create_billing_plan_mapping/$',
				views.CreateBillingPlanMappingView.as_view(),
				name='create_billing_plan_mapping'
		),

		url(
				r'^(?P<id>[^/]+)/modify_billing_plan_mapping/$',
				views.ModifyBillingPlanMappingView.as_view(),
				name='modify_billing_plan_mapping'
		),

]
