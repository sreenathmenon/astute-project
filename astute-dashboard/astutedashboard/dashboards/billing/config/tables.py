#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from astutedashboard.common import \
    delete_billing_type, \
    delete_service_type, \
    delete_discount, \
    delete_plan

#
# Billing Types table
#


class CreateBillingType(tables.LinkAction):
    name = 'create_billing_type'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_config:create_billing_type'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:create_type"),)

class ModifyBillingType(tables.LinkAction):
    name = 'modify_billing_type'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_config:modify_billing_type'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "billing:edit_type"),)

class DeleteBillingType(tables.DeleteAction):
    name = 'delete_billing_type'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_config:delete_billing_type'
    policy_rules = (("billing", "billing:delete_type"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_billing_type(request, id=id)
        return True

class BillingTypesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    code = tables.Column('code', verbose_name=_('Code'))
    status = tables.Column('status', verbose_name=_('Status'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'billing_types'
        verbose_name = _('Billing Types')

        #Commented for disabling the edit and delete options
        '''
        row_actions = (
            ModifyBillingType,
            DeleteBillingType
        )
        '''
        
        #Need to display only the Create option
        '''
        table_actions = (
            CreateBillingType,
            DeleteBillingType
        )
        '''
        table_actions = (
            CreateBillingType,
        )


#
# Service Types table
#

class CreateServiceType(tables.LinkAction):
    name = 'create_service_type'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_config:create_service_type'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "service_type:create"),)

class ModifyServiceType(tables.LinkAction):
    name = 'modify_service_type'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_config:modify_service_type'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "service_type:edit"),)

class DeleteServiceType(tables.DeleteAction):
    name = 'delete_service_type'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_config:delete_service_type'
    policy_rules = (("billing", "service_type:delete"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_service_type(request, id)
        return True

class ServiceTypesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    code = tables.Column('code', verbose_name=_('Code'))
    units = tables.Column('units', verbose_name=_('Units'))
    status = tables.Column('status', verbose_name=_('Status'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'service_types'
        verbose_name = _('Service Types')
        table_actions = ()
        
        #Commented to disable the Edit and Delete options
        '''
        row_actions = (
            ModifyServiceType,
            DeleteServiceType
        )
        '''
      
        #Need to display only the create option
        '''
        table_actions = (
            CreateServiceType,
            DeleteServiceType
        )
        '''

        table_actions = (
            CreateServiceType,
        )

#
# Discount Types table
#

class DiscountTypesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    code = tables.Column('code', verbose_name=_('Code'))
    status = tables.Column('status', verbose_name=_('Status'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'discount_types'
        verbose_name = _('Discount Types')


#
# Discounts table
#

class CreateDiscount(tables.LinkAction):
    name = 'create_discount'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_config:create_discount'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "discount:create"),)

class ModifyDiscount(tables.LinkAction):
    name = 'modify_discount'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_config:modify_discount'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "discount:edit"),)

class DeleteDiscount(tables.DeleteAction):
    name = 'delete_discount'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_config:delete_discount'
    policy_rules = (("billing", "discount:delete"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_discount(request, id=id)
        return True

class DiscountFilterAction(tables.FilterAction):
    name="discount_listing_filter"
    verbose_name = _("Filter Discounts")
    needs_preloading = True

class DiscountsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    code = tables.Column('code', verbose_name=_('Code'))
    create_time = tables.Column('create_time', verbose_name=_('Create Date'))
    expiration_date = tables.Column('expiration_date', verbose_name=_('Exp. Date'))
    amt = tables.Column('amt', verbose_name=_('AMT'))
    discount_type_code = tables.Column('discount_type_code', verbose_name=_('Disc. Type'))
    usage_count = tables.Column('usage_count', verbose_name=_('Usage'))
    is_expired = tables.Column('is_expired', verbose_name=_('Expired'))
    is_default = tables.Column('is_default', verbose_name=_('Default'))
    notes = tables.Column('notes', verbose_name=_('Notes'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'discounts'
        verbose_name = _('Discounts')
        row_actions = (
            ModifyDiscount,
            DeleteDiscount
        )
        table_actions = (
            CreateDiscount,
            DeleteDiscount,
            DiscountFilterAction
        )


#
# Plans table
#

class CreatePlan(tables.LinkAction):
    name = 'create_plan'
    verbose_name = _('Create')
    url = 'horizon:billing:billing_config:create_plan'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "plans:create"),)

class ModifyPlan(tables.LinkAction):
    name = 'modify_plan'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_config:modify_plan'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "plans:edit"),)

class DeletePlan(tables.DeleteAction):
    name = 'delete_plan'
    verbose_name = _('Delete')
    url = 'horizon:billing:billing_config:delete_Plan'
    policy_rules = (("billing", "plans:delete"),)

    action_present = lambda self, n: _('Delete')
    action_past = lambda self, n: _('Deleted')

    def delete(self, request, id):
        delete_plan(request, id)
        return True

class PlansFilterAction(tables.FilterAction):
    name="plan_listing_filter"
    verbose_name = _("Filter Plans")
    needs_preloading = True

class PlansTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    #code = tables.Column('code', verbose_name=_('Code'))
    service_type = tables.Column('service_type', verbose_name=_('Serv. Type'))
    rate = tables.Column('rate', verbose_name=_('Rate'))
    setup_fee = tables.Column('setup_fee', verbose_name=_('Setup Fee'))
    billing_type = tables.Column('billing_type', verbose_name=_('Bill. Type'))
    ref_id = tables.Column('ref_id', verbose_name=_('Flavor'))
    description = tables.Column('description', verbose_name=_('Description'))
    metadata_mark = tables.Column('metadata_mark', verbose_name=_('Image Mark'))
    status = tables.Column('status', verbose_name=_('Status'))

    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'plans'
        verbose_name = _('Plans')
        row_actions = (
            ModifyPlan,
            DeletePlan
        )
        table_actions = (
            CreatePlan,
            DeletePlan,
            PlansFilterAction
        )
