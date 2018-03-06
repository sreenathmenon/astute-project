#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from astutedashboard.common import delete_discount_mapping

class DiscountMappingFilterAction(tables.FilterAction):
    name="discount_mapping_filter"
    verbose_name = _("Filter Discount Mappings")
    needs_preloading = True

class CreateBillingDiscount(tables.LinkAction):
    name = 'create_billing_discount'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_discounts:create_billing_discount'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "discount:create_map"),)


class ModifyBillingDiscount(tables.LinkAction):
    name = 'modify_billing_discount'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_discounts:modify_billing_discount'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "discount:edit_map"),)


class DeleteBillingDiscount(tables.DeleteAction):
    name = 'delete_billing_discount'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_discounts:delete_billing_discount'
    policy_rules = (("billing", "discount:delete_map"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_discount_mapping(request, id)
        return True

class BillingDiscountsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    user_name = tables.Column('user_name', verbose_name=_('Account'))
    plan_name = tables.Column('plan_name', verbose_name=_('Plan'))
    name = tables.Column('name', verbose_name=_('Name'))
    discount_type = tables.Column('discount_type', verbose_name=_('Type'))
    discount_amt = tables.Column('discount_amt', verbose_name=_('Value'))
    apply_type = tables.Column('apply_type', verbose_name=_('Validity'))
    apply_interval = tables.Column('apply_interval', verbose_name=_('Months'))
    #apply_amt = tables.Column('apply_amt', verbose_name=_('Apply Amount'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'billing_discounts'
        verbose_name = _('Discounts')
        row_actions = (
            ModifyBillingDiscount,
            DeleteBillingDiscount
        )
        table_actions = (
            CreateBillingDiscount,
            DeleteBillingDiscount,
            DiscountMappingFilterAction
        )

