#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

class UserPlanActivate(tables.LinkAction):
    name = 'user_plan_activate'
    verbose_name = _('Activate')
    url = 'horizon:project:customer_available_plans:activate_user_plan'
    ajax = True
    classes = ('ajax-modal',)

class AvailablePlansTable(tables.DataTable):
    # id= tables.Column('id', verbose_name=_('Id'))
    name = tables.Column('name', verbose_name=_('Name'), \
        link="horizon:project:customer_available_plans:user_avbl_plan_details")
    service_name = tables.Column('service_name', verbose_name=_('Service Name'))
    rate = tables.Column('rate', verbose_name=_('Rate'))
    setup_fee = tables.Column('setup_fee', verbose_name=_('Setup Fee'))
    #billing_type = tables.Column('billing_type', verbose_name=_('Billing Type'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = "user_available_plans"
        verbose_name = _("Available Plans")
        row_actions = (UserPlanActivate,)
        table_actions = ()
