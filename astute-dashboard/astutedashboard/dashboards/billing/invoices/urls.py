#
# Copyright 2017 NephoScale
#


from django.conf.urls import url

#from astutedashboard.dashboards.admin.invoices import views
from astutedashboard.dashboards.billing.invoices import views


urlpatterns = [

    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),

    url(
        r'^(?P<id>[^/]+)/modify_billing_invoice/$',
        views.ModifyBillingInvoiceView.as_view(),
        name='modify_billing_invoice'
    ),

    url(
        r'^(?P<id>[^/]+)/billing_invoice_details/$',
        views.BillingInvoiceDetailsView.as_view(),
        name='billing_invoice_details'
    ),

    url(
        r'^search_filter$',
        views.search_filter,
        name='search_filter'
    ),

    url(
        r'^(?P<id>[^/]+)/export_as_dat$',
        views.export_as_dat,
        name='export_as_dat'
    ),

    url(
        r'^(?P<id>[^/]+)/export_as_csv$',
        views.export_as_csv,
        name='export_as_csv'
    ),

]
