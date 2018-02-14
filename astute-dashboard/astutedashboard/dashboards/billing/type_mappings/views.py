#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon import workflows

from openstack_dashboard import api

from astutedashboard.common import \
    get_billing_type_mappings, \
    get_billing_type_mapping, \
    get_plans, \
    get_project_volume_type_quotas
'''
from astutedashboard.dashboards.admin.type_mappings \
    import forms as panel_forms
from astutedashboard.dashboards.admin.type_mappings \
    import tables as panel_tables
from astutedashboard.dashboards.admin.type_mappings \
    import workflows as panel_worflows
'''

from astutedashboard.dashboards.billing.type_mappings \
    import forms as panel_forms
from astutedashboard.dashboards.billing.type_mappings \
    import tables as panel_tables
from astutedashboard.dashboards.billing.type_mappings \
    import workflows as panel_worflows

try:
    import simplejson as json
except ImportError:
    import json


#
# Billing Type Mappings views
#

class IndexView(tables.DataTableView):
    table_class = panel_tables.BillingTypeMappingsTable
    template_name = 'billing/type_mappings/index.html'
    page_title = _("Accounts")

    def get_data(self):
        data = get_billing_type_mappings(self.request, verbose=True)
        for item in data:
            disc_map = item.get('discount_mapping', None)
            item['discount'] = disc_map.get('name', None) if disc_map else None
        return data


class CreateAccountView(workflows.WorkflowView):
    workflow_class = panel_worflows.CreateAccountWorkflow
    success_url = reverse_lazy("horizon:billing:billing_type_mappings:index")
    submit_url = "horizon:billing:billing_type_mappings:billing_create_account"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateAccountView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        return context

class UpdateAccountView(workflows.WorkflowView):
    workflow_class = panel_worflows.UpdateAccountWorkflow
    success_url = reverse_lazy("horizon:billing:billing_type_mappings:index")
    submit_url = "horizon:billing:billing_type_mappings:billing_update_account"

    def get_initial(self):
        id = self.kwargs.get('id')
        data = get_billing_type_mapping(self.request, id)
        data.update(data.pop('extra_fields'))
        #project = api.keystone.tenant_get(self.request, data['user'])
        data['project_id'] = data['project'].id
        data['project_name'] = data['project'].name
        return data

    def get_context_data(self, **kwargs):
        context = super(UpdateAccountView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context


class ModifyVolumeTypeQuotasView(forms.ModalFormView):
    form_class = panel_forms.ModifyVolumeTypeQuotasForm
    template_name = 'billing/type_mappings/modal_form.html'
    success_url = reverse_lazy("horizon:billing:billing_type_mappings:index")
    modal_id = "modify_volume_type_quotas_modal"
    modal_header = _("Modify Account Volume Type Quotas")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_type_mappings:modify_volume_type_quotas"

    def get_initial(self):
        account = get_billing_type_mapping(self.request, self.kwargs['id'])
        project_id = account['user']
        data = {
            'project_id': project_id,
            'project_name': account['project'].name,
            'volume_types': get_project_volume_type_quotas(self.request, project_id)
        }
        return data

    def get_context_data(self, **kwargs):
        context = super(ModifyVolumeTypeQuotasView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context

