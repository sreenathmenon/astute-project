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

from astutedashboard.common import \
    get_discount_types, \
    get_discounts, \
    get_discount_mappings, \
    get_discount_mapping, \
    get_billing_plan_mappings, \
    get_billing_plan_mapping, \
    get_projects, \
    get_plans

'''
from astutedashboard.dashboards.admin.plan_mappings \
    import forms as panel_forms
from astutedashboard.dashboards.admin.plan_mappings \
    import tables as panel_tables
'''
from astutedashboard.dashboards.billing.plan_mappings \
    import forms as panel_forms
from astutedashboard.dashboards.billing.plan_mappings \
    import tables as panel_tables


#
# Billing Plan Mappings views
#

class IndexView(tables.DataTableView):
    table_class = panel_tables.BillingPlanMappingsTable
    template_name = 'billing/plan_mappings/index.html'
    page_title = _("Plan Mappings")

    def get_data(self):
        data = get_billing_plan_mappings(self.request, verbose=True)
        for item in data:
            disc_map = item.get('discount_mapping', None)
            if disc_map:
                item['discount'] = disc_map.get('name', None)
        return data

class CreateBillingPlanMappingView(forms.ModalFormView):
    form_class = panel_forms.CreateBillingPlanMappingForm
    template_name = 'billing/plan_mappings/modal_form.html'
    success_url = reverse_lazy("horizon:billing:billing_plan_mappings:index")
    modal_id = "create_billing_plan_mapping_modal"
    modal_header = _("Create Billing Plan Mapping")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_plan_mappings:create_billing_plan_mapping"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateBillingPlanMappingView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        context['plans'] = get_plans(self.request)
        return context


class ModifyBillingPlanMappingView(forms.ModalFormView):
    form_class = panel_forms.ModifyBillingPlanMappingForm
    template_name = 'billing/plan_mappings/modal_form.html'
    success_url = reverse_lazy("horizon:billing:billing_plan_mappings:index")
    modal_id = "modify_billing_plan_mapping_modal"
    modal_header = _("Modify Billing Plan Mapping")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_plan_mappings:modify_billing_plan_mapping"

    def get_initial(self):
        data = get_billing_plan_mapping(self.request, self.kwargs['id'])
        projects = {}
        for project in get_projects(self.request):
            projects[str(project.id)] = project
        plans = {}
        for plan in get_plans(self.request):
            plans[str(plan['id'])] = plan
        # insert required data
        project = projects.get(str(data['user']))
        data['user_name'] =  project.name if project else '!ERR: ' + data['user']
        plan = plans.get(str(data['plan_id']))
        if plan:
            data['plan_name'] = plan['name']
            data['service_type'] = plan['service_type']
        else:
            data['plan_name'] = '!ERR: plan: ' + str(plan_map['id'])
            data['service_type'] = None

        disc_map = data.get('discount_mapping', None)
        if disc_map:
            data['discount'] = disc_map['discount_id']
            data['apply_type'] = disc_map['apply_type']
            data['apply_interval'] = disc_map['apply_interval']
            data['apply_amt'] = disc_map['apply_amt']
        return data

    def get_context_data(self, **kwargs):
        context = super(ModifyBillingPlanMappingView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context
