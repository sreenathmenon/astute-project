#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from astutedashboard.common import \
    get_discounts, \
    get_discount, \
    get_discount_mapping, \
    get_projects, \
    get_billing_types, \
    get_billing_type_mapping, \
    get_billing_type_mappings, \
    get_billing_plan_mappings, \
    create_billing_type_mapping, \
    modify_billing_type_mapping, \
    create_discount_mapping, \
    modify_discount_mapping, \
    delete_discount_mapping


apply_type_choices = (
    ('contract_full', 'whole contract'),
    ('contract_first', 'months from contract beginning'),
    ('contract_last', 'months from contract ending'),
    ('contract_selected', 'selected months of contract')
)


class CreateBillingDiscountMappingForm(forms.SelfHandlingForm):

    user_name = forms.ChoiceField(label = _('Account'), choices=[])
    plan_name = forms.ChoiceField(label=_('Plan'), required=False)
    discount_id = forms.ChoiceField(label=_('Discount'), choices=[], required=False)
    apply_type = forms.ChoiceField(label=_('Discount Validity'), choices=apply_type_choices, required=False)
    apply_interval = forms.CharField(label=_('Discount Months (comma separated list for selected months apply interval)'), required=False)
    #apply_amt = forms.FloatField(label=_('Discount Amount (for ovverride discount only)'), required=False)


    def __init__(self, request, *args, **kwargs):
        super(CreateBillingDiscountMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user_name'].choices = [
            (acct['user_id'], acct['user']) for acct in get_billing_type_mappings(request, verbose=True)
        ]
        self.fields['user_name'].choices.insert(0, (0, ''))
        self.fields['discount_id'].choices = [(str(d['id']), d['name']) for d in get_discounts(request)]
        self.fields['plan_name'].validate = lambda v: True


    def clean(self):
        super(CreateBillingDiscountMappingForm, self).clean()

        disc_id = self.request.POST.get('discount_id', None)

        # check if discount params are required
        if not disc_id:
            self.discount = {'type_code': None }
            return

        # save discount data for use in 'handle'
        self.discount = get_discount(self.request, disc_id)

        apply_type = self.request.POST.get('apply_type', None)
        if not apply_type:
            self.add_error('apply_type', 'This field is required')

        if apply_type != 'contract_full' and not self.request.POST.get('apply_interval', None):
            self.add_error('apply_interval', 'This field is required')

        if self.discount['type_code'] == 'override':
            if not self.request.POST.get('apply_amt', None):
                self.add_error('apply_amt', 'This field is required for override discount')


    def handle(self, request, data):
        account_id = data.get('user_name')
        if not account_id:
            exceptions.handle(request, _('Invalid request.'))
            return False

        ref_id = account_id
        map_object = 'user'

        plan_map_id = data.get('plan_name')
        if plan_map_id:
            ref_id = plan_map_id
            map_object = 'user_plan'

        disc_map = {
            'user': account_id,
            'discount_id': data.get('discount_id'),
            'ref_id': ref_id,
            'map_object': map_object,
            'apply_type': data.get('apply_type'),
            'apply_interval': data.get('apply_interval'),
            'apply_amt': data.get('apply_amt')
        }

        create_discount_mapping(request, disc_map)

        return True


class ModifyBillingDiscountMappingForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    user_name = forms.CharField(label=_('Account'))
    plan_name = forms.CharField(label=_('Plan'), required=False)
    discount_id = forms.ChoiceField(label=_('Discount'), choices=[], required=False)
    apply_type = forms.ChoiceField(label=_('Discount Validity'), choices=apply_type_choices, required=False)
    apply_interval = forms.CharField(label=_('Discount Months (comma separated list for selected months apply interval)'), required=False)
    #apply_amt = forms.FloatField(label=_('Discount Amount (for ovverride discount only)'), required=False)


    def __init__(self, request, *args, **kwargs):
        super(ModifyBillingDiscountMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user_name'].widget.attrs['readonly'] = True
        self.fields['plan_name'].widget.attrs['readonly'] = True
        self.fields['discount_id'].choices = [(str(d['id']), d['name']) for d in get_discounts(request)]

    def clean(self):
        super(ModifyBillingDiscountMappingForm, self).clean()

        disc_id = self.request.POST.get('discount_id', None)

        # check if discount params are required
        if not disc_id:
            self.discount = {'type_code': None }
            return

        # save discount data for use in 'handle'
        self.discount = get_discount(self.request, disc_id)

        apply_type = self.request.POST.get('apply_type', None)
        if not apply_type:
            self.add_error('apply_type', 'This field is required')

        if apply_type != 'contract_full' and not self.request.POST.get('apply_interval', None):
            self.add_error('apply_interval', 'This field is required')

        if self.discount['type_code'] == 'override':
            if not self.request.POST.get('apply_amt', None):
                self.add_error('apply_amt', 'This field is required for override discount')


    def handle(self, request, data):
        id = data.get('id', None)
        if not id:
            exceptions.handle(request, _('Invalid request.'))
            return False

        try:
            cur_disc_map = get_discount_mapping(request, id)

            disc_map = {
                'user': cur_disc_map['user'],
                'discount_id': data.get('discount_id') or cur_disc_map['discount_id'],
                'ref_id': cur_disc_map['ref_id'],
                'map_object': cur_disc_map['map_object'],
                'apply_type': data.get('apply_type') or cur_disc_map['apply_type'],
                'apply_interval': data.get('apply_interval') or cur_disc_map['apply_interval'],
                'apply_amt': data.get('apply_amt') or cur_disc_map['apply_amt']
            }

            modify_discount_mapping(request, id, disc_map)

            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify billing type mapping.'))
