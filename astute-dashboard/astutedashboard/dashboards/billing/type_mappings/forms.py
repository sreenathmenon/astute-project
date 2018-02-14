#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api
from openstack_dashboard.api import base
from openstack_dashboard.api import cinder
from openstack_dashboard.api import keystone
from openstack_dashboard.api import nova

from astutedashboard.common import \
    get_projects, \
    get_billing_types, \
    get_billing_type_mapping, \
    create_billing_type_mapping, \
    modify_billing_type_mapping, \
    modify_project_volume_type_quotas

#
# helper routines
#

# generate projects list
def gen_projects(request):
    data = []
    for project in get_projects(request):
        data.append((project.id, project.name))
    return data

def get_project_name(request, id):
    id = str(id)
    for project in get_projects(request):
        if project.id == id:
            return project.name
    return None

# generate billing types list
def gen_billing_types(request):
    data = []
    for item in get_billing_types(request):
        data.append((item['id'], _(item['name'])))
    return data


class CreateBillingTypeMappingForm(forms.SelfHandlingForm):

    user = forms.ChoiceField(label=_('Project (Account)'), choices=[])
    billing_type = forms.ChoiceField(label=_('Billing Type'), choices=[])

    def __init__(self, request, *args, **kwargs):
        super(CreateBillingTypeMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user'].choices = gen_projects(request)
        self.fields['billing_type'].choices = gen_billing_types(request)

    def handle(self, request, data):
        try:
            data['extra_fields'] = {}
            create_billing_type_mapping(request, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create billing type mapping.'))


status_choices = (('active', 'active'), ('suspended', 'suspended'), ('terminated', 'terminated'))

class ModifyBillingTypeMappingForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    user = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    user_name = forms.CharField(label=_('Account'))
    billing_type = forms.ChoiceField(label=_('Billing Type'), choices=[])

    def __init__(self, request, *args, **kwargs):
        super(ModifyBillingTypeMappingForm, self).__init__(request, *args, **kwargs)
        self.fields['user_name'].widget.attrs['readonly'] = True
        self.fields['user_name'].widget.attrs['value'] = get_project_name(request, self.initial['user'])
        self.fields['billing_type'].choices = gen_billing_types(request)

    def handle(self, request, data):
        id = data.pop('id', None)
        if not id:
            exceptions.handle(request, _('Invalid request.'))
            return False
        try:
            user_id = str(data.pop('user'))
            data['extra_fields'] = {}

            modify_billing_type_mapping(request, id, data)

            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify billing type mapping.'))



class ModifyVolumeTypeQuotasForm(forms.SelfHandlingForm):

    project_id = forms.CharField(label=_("Project ID"), widget=forms.HiddenInput())
    project_name = forms.CharField(label=_('Account'), required=False)

    def __init__(self, request, *args, **kwargs):
        super(ModifyVolumeTypeQuotasForm, self).__init__(request, *args, **kwargs)

        self.fields['project_name'].widget.attrs['readonly'] = 'readonly'

        for volume_type, quota in self.initial['volume_types'].items():
            self.fields[volume_type] = forms.IntegerField(
                label=volume_type + ' (GB)',
                min_value=-1
            )
            self.fields[volume_type].widget.attrs['value'] = quota

    def handle(self, request, data):
        project_id = data.pop('project_id', None)
        data.pop('project_name', None)

        if not project_id:
            exceptions.handle(request, _('Invalid request.'))
            return False

        quotas = {}
        for volume_type, quota in data.items():
            quotas['gigabytes_' + volume_type] = quota

        try:
            modify_project_volume_type_quotas(request, project_id, quotas)
            return True
        except:
            exceptions.handle(request, _('Unable to modify account volume type quotas. Please contact support.'))

