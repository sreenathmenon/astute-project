#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from astutedashboard.common import delete_billing_plan_mapping

class PlanMappingFilterAction(tables.FilterAction):
    name="plan_mapping_filter"
    verbose_name = _("Filter Plans")
    needs_preloading = True

class CreateBillingPlanMapping(tables.LinkAction):
    name = 'create_billing_plan_mapping'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_plan_mappings:create_billing_plan_mapping'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "plan:create_map"),)

class ModifyBillingPlanMapping(tables.LinkAction):
    name = 'modify_billing_plan_mapping'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_plan_mappings:modify_billing_plan_mapping'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "plan:edit_map"),)

'''
class DeleteBillingPlanMapping(tables.DeleteAction):
    name = 'delete_billing_plan_mapping'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_plan_mappings:delete_billing_plan_mapping'
    policy_rules = (("billing", "plan:delete_map"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_billing_plan_mapping(request, id)
        return True
'''

class BillingPlanMappingsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    user = tables.Column('user', verbose_name=_('Account'))
    plan = tables.Column('plan', verbose_name=_('Plan'))
    vm_name = tables.Column('vm_name', verbose_name=_('VM Name'))
    qty =  tables.Column('qty', verbose_name=_('Qty.'))
    created_on =  tables.Column('created_on', verbose_name=_('Created On'))
    contract_period =  tables.Column('contract_period', verbose_name=_('Period'))
    inactive_on =  tables.Column('inactive_on', verbose_name=_('Inactive On'))
    status =  tables.Column('status', verbose_name=_('Status'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'billing_plan_mappings'
        verbose_name = _('Billing Plan Mappings')
        row_actions = (
            ModifyBillingPlanMapping,
            #DeleteBillingPlanMapping
        )
        table_actions = (
            CreateBillingPlanMapping,
            PlanMappingFilterAction
            #DeleteBillingPlanMapping
        )

