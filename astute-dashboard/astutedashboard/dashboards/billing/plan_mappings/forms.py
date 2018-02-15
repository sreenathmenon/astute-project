#
# Copyright 2017 NephoScale
#

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from astutedashboard.common import \
    get_projects, \
    get_plans, \
    get_billing_type_mappings, \
    get_billing_plan_mapping, \
    create_billing_plan_mapping, \
    modify_billing_plan_mapping

# IaaS service type id
IAAS_SERVICE_TYPE_ID = 1

#
# helper routines
#

# generate projects list
def gen_projects(request):
    data = []
    for project in get_projects(request):
        data.append((project.id, project.name))
    return data

def gen_accounts(request):
    data = []
    projects = {}
    for type_map in get_billing_type_mappings(request, verbose=True):
        data.append((type_map['user_id'], type_map['user']))
    return data


class CreateBillingPlanMappingForm(forms.SelfHandlingForm):

    user = forms.ChoiceField(label=_('Account'), choices=[])
    contract_period = forms.IntegerField(label=_('Contract Period (in months)'), min_value=1)

    def __init__(self, request, *args, **kwargs):
        super(CreateBillingPlanMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user'].choices = gen_accounts(request)

    def clean(self):
        super(CreateBillingPlanMappingForm, self).clean()
        has_selected_plan = False
        for item in self.request.POST:
            field = item.split('::')
            if len(field) == 3 and field[0] == 'plan':
                value = int(self.request.POST[item])
                if value > 0:
                    has_selected_plan = True
                    break
        if not has_selected_plan:
            raise ValidationError('At least one plan must be selected')


    def handle(self, request, data):
        try:
            plans = {}
            # handle plan mappings
            for item in request.POST:
                field = item.split('::')
                if len(field) == 3 and field[0] == 'plan':
                    value = int(request.POST[item])
                    if value > 0:
                        plans[field[1]] = value
            data['plans'] = plans
            create_billing_plan_mapping(request, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create billing plan mapping.'))


status_choices = (('active', 'active'), ('suspended', 'suspended'), ('terminated', 'terminated'))

class ModifyBillingPlanMappingForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    user = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    user_name = forms.CharField(label=_('Account'))
    plan_name = forms.CharField(label=_('Plan'))
    contract_period = forms.IntegerField(label=_('Contract Period (in months)'), min_value=1)
    qty = forms.IntegerField(label=_('Quantity'), min_value=1)
    status = forms.ChoiceField(label=_('Status'), choices=status_choices)

    def __init__(self, request, *args, **kwargs):
        super(ModifyBillingPlanMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user_name'].widget.attrs['readonly'] = True
        self.fields['plan_name'].widget.attrs['readonly'] = True
        # handle qty field
        if self.initial.get('service_type') == IAAS_SERVICE_TYPE_ID:
            del self.fields['qty']

    def handle(self, request, data):
        id = data.pop('id', None)
        if not id:
            exceptions.handle(request, _('Invalid request.'))
            return False

        try:
            cur_plan_map = get_billing_plan_mapping(request, id)

            #Only following 2 values are accepted for updation
            billing_plan_data = {}
            billing_plan_data['status'] = data.pop('status', None)
            billing_plan_data['contract_period'] = data.pop('contract_period', None)
            modify_billing_plan_mapping(request, id, billing_plan_data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify billing plan mapping.'))

