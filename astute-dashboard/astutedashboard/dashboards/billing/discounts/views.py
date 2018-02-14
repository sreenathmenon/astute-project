#
# Copyright 2017 NephoScale
#

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

try:
    import simplejson as json
except ImportError:
    import json
except:
    raise

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
    get_projects, \
    get_plans

'''
from astutedashboard.dashboards.admin.discounts \
    import forms as panel_forms
from astutedashboard.dashboards.admin.discounts \
    import tables as panel_tables
'''
from astutedashboard.dashboards.billing.discounts \
    import forms as panel_forms
from astutedashboard.dashboards.billing.discounts \
    import tables as panel_tables

#
# Billing Discount Mappings views
#

apply_intervals = {
    'contract_full': 'whole contract',
    'contract_first': 'months from contract beginning',
    'contract_last': 'months from contract ending',
    'contract_selected': 'selected months of contract'
}


class IndexView(tables.DataTableView):
    table_class = panel_tables.BillingDiscountsTable
    template_name = 'billing/discounts/index.html'
    page_title = _("Discounts")

    def get_data(self):
        data = get_discount_mappings(self.request)
        projects = dict([(str(p.id), p) for p in get_projects(self.request)])
        disc_types = dict([(str(dt['id']), dt) for dt in get_discount_types(self.request)])
        discounts = dict([(str(d['id']), d) for d in get_discounts(self.request)])
        plans = dict([(str(p['id']), p) for p in get_plans(self.request)])
        plan_mappings = dict([(str(pm['id']), pm) for pm in get_billing_plan_mappings(self.request)])
        for item in data:
            project = projects.get(str(item['user']))
            item['user_name'] =  project.name if project else '!ERR: ' + item['user']
            if item['map_object'] == 'user_plan':
              plan_map = plan_mappings.get(item['ref_id'])
              if plan_map:
                  plan = plans.get(str(plan_map['plan_id']))
                  item['plan_name'] = plan['name'] if plan else '!ERR: plan: ' + str(plan_map['id'])
              else:
                  '!ERR: plan mapping: ' + item['ref_id']
            disc = discounts.get(str(item['discount_id']))
            disc_type = disc_types.get(str(item['discount_type_id']))
            item['discount_type'] = disc_type['name'] if disc_type else '!ERR: ' + str(item['discount_type_id'])
            item['discount_amt'] = str(disc['amt']) + '%' if disc else '!ERR: ' + str(item['discount_id'])
            item['apply_type'] = apply_intervals.get(item['apply_type']) or '!ERR: ' + item['apply_type']
            if item['apply_amt']:
                item['discount_amt'] = item['apply_amt']
        return data

class CreateBillingDiscountMappingView(forms.ModalFormView):
    form_class = panel_forms.CreateBillingDiscountMappingForm
    template_name = 'billing/discounts/modal_create_form.html'
    success_url = reverse_lazy("horizon:billing:billing_discounts:index")
    modal_id = "create_billing_discount_modal"
    modal_header = _("Create Billing Discount")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_discounts:create_billing_discount"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateBillingDiscountMappingView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url)
        return context


class ModifyBillingDiscountMappingView(forms.ModalFormView):
    form_class = panel_forms.ModifyBillingDiscountMappingForm
    template_name = 'billing/discounts/modal_form.html'
    success_url = reverse_lazy("horizon:billing:billing_discounts:index")
    modal_id = "modify_billing_discount_modal"
    modal_header = _("Modify Billing Discount")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_discounts:modify_billing_discount"

    def get_initial(self):
        data = get_discount_mapping(self.request, self.kwargs['id'])
        projects = {}
        for project in get_projects(self.request):
            projects[str(project.id)] = project
        plans = {}
        for plan in get_plans(self.request):
            plans[str(plan['id'])] = plan
        plan_mappings = {}
        for plan_map in get_billing_plan_mappings(self.request):
            plan_mappings[str(plan_map['id'])] = plan_map
        # insert required data
        project = projects.get(str(data['user']))
        data['user_id'] = data['user']
        data['user_name'] =  project.name if project else '!ERR: ' + data['user']
        if data['map_object'] == 'user_plan':
            plan_map = plan_mappings.get(data['ref_id'])
            if plan_map:
                data['plan_mapping_id'] = plan_map['id']
                plan = plans.get(str(plan_map['plan_id']))
                data['plan_name'] = plan['name'] if plan else '!ERR: plan: ' + str(plan_map['id'])
            else:
                '!ERR: plan mapping: ' + data['ref_id']
        return data

    def get_context_data(self, **kwargs):
        context = super(ModifyBillingDiscountMappingView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context


# return account plan mappings
def account_plan_mappings(request):
    account_id = request.GET.get('account_id')
    if not account_id:
        return HttpResponse('[]')
    data = [{ 'id': item['id'], 'name': item['plan']} for item in get_billing_plan_mappings(request, project_id=account_id, verbose=True)]
    return HttpResponse(json.dumps(data), content_type='application/json')
