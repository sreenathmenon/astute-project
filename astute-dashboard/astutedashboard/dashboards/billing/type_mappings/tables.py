#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from astutedashboard.common import delete_billing_type_mapping

class AccountFilterAction(tables.FilterAction):
    name="account_listing_filter"
    verbose_name = _("Filter Accounts")
    needs_preloading = True

class CreateAccount(tables.LinkAction):
    name = 'billing_create_account'
    verbose_name = _('Create Account')
    url = 'horizon:billing:billing_type_mappings:billing_create_account'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:create_map"),)

class UpdateAccount(tables.LinkAction):
    name = 'billing_update_account'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_type_mappings:billing_update_account'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:edit_map"),)


class ModifyVolumeTypeQuotas(tables.LinkAction):
    name = 'modify_volume_type_quotas'
    verbose_name = _('Modify Volume Type Quotas')
    url = 'horizon:billing:billing_type_mappings:modify_volume_type_quotas'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:edit_map"),)

class DeleteBillingTypeMapping(tables.DeleteAction):
    name = 'delete_billing_type_mapping'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_type_mappings:delete_billing_type_mapping'
    policy_rules = (("billing", "billing:delete_map"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_billing_type_mapping(request, id)
        return True

class ResendWelcomeLetter(tables.LinkAction):
    name = 'resend_welcome_letter'
    verbose_name = _('Resend Welcome Letter')
    url = 'horizon:billing:billing_type_mappings:resend_welcome_letter'
    #ajax = True
    #classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:edit_map"),)

class BillingTypeMappingsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    user = tables.Column('user', verbose_name=_('Account'))
    billing_type = tables.Column('billing_type', verbose_name=_('Billing Type'))
    customer_name = tables.Column('customer_name', verbose_name=_('Customer Name'))
    service_id = tables.Column('service_id', verbose_name=_('Service ID'))


    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'billing_type_mappings'
        verbose_name = _('Accounts')
        row_actions = (
            UpdateAccount,
            ModifyVolumeTypeQuotas,
            ResendWelcomeLetter,
            DeleteBillingTypeMapping
        )
        table_actions = (
            CreateAccount,
            DeleteBillingTypeMapping,
            AccountFilterAction
        )

