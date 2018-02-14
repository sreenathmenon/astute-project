#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

class SubscribedPlansTable(tables.DataTable):
    #id = tables.Column('plan_id', verbose_name=_('Id'))
    name = tables.Column('name', verbose_name=_('Name'), \
        link="horizon:project:customer_subscribed_plans:user_sub_plan_details")
    qty = tables.Column('qty', verbose_name=_('Quantity'))
    date = tables.Column('created_on', verbose_name=_('Start Date'))
    status = tables.Column('status', verbose_name=_('Status'))
    contract = tables.Column('contract_period', verbose_name=_('Contract Period'))
    billing_type = tables.Column('billing_type', verbose_name=_('Billing Type'))
    
    def get_object_id(self, datum):
        return datum['plan_id']

    class Meta(object):
        name = "user_subscribed_plans"
        verbose_name = _("Subscribed Plans")
        row_actions = ()
        table_actions = () 
