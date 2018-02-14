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

'''
from astutedashboard.dashboards.admin.config \
    import forms as config_forms
from astutedashboard.dashboards.admin.config \
    import tables as billing_tables
from astutedashboard.dashboards.admin.config \
    import tabs as config_tabs
'''

from astutedashboard.dashboards.billing.config \
    import forms as config_forms
from astutedashboard.dashboards.billing.config \
    import tables as billing_tables
from astutedashboard.dashboards.billing.config \
    import tabs as config_tabs

from astutedashboard.common import \
    get_billing_type, \
    get_service_type, \
    get_discount, \
    get_plan, \
    PAYG_BILLING_TYPE_ID, \
    RAB_BILLING_TYPE_ID


#
# Billing configuration views
#

class IndexView(tabs.TabbedTableView):
    tab_group_class = config_tabs.ConfigTabs
    template_name = "billing/config/index.html"


#
# Billing Type views
#

class CreateBillingTypeView(forms.ModalFormView):
    form_class = config_forms.CreateBillingTypeForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "create_billing_type_modal"
    modal_header = _("Create Billing Type")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:create_billing_type"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateBillingTypeView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        return context


class ModifyBillingTypeView(forms.ModalFormView):
    form_class = config_forms.ModifyBillingTypeForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "modify_billing_type_modal"
    modal_header = _("Modify Billing Type")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:modify_billing_type"

    def get_initial(self):
        return get_billing_type(self.request, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(ModifyBillingTypeView, self).get_context_data(**kwargs)
        type_id = self.kwargs['id']
        context['submit_url'] = reverse(self.submit_url, args=[type_id])
        return context

#
# Service Type views
#

class CreateServiceTypeView(forms.ModalFormView):
    form_class = config_forms.CreateServiceTypeForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "create_service_type_modal"
    modal_header = _("Create Service Type")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:create_service_type"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateServiceTypeView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        return context


class ModifyServiceTypeView(forms.ModalFormView):
    form_class = config_forms.ModifyServiceTypeForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "modify_service_type_modal"
    modal_header = _("Modify Service Type")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:modify_service_type"

    def get_initial(self):
        return get_service_type(self.request, self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(ModifyServiceTypeView, self).get_context_data(**kwargs)
        type_id = self.kwargs['id']
        context['submit_url'] = reverse(self.submit_url, args=[type_id])
        return context

#
# Discount views
#
class CreateDiscountView(forms.ModalFormView):
    form_class = config_forms.CreateDiscountForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "create_discount_modal"
    modal_header = _("Create Discount")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:create_discount"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreateDiscountView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        return context


class ModifyDiscountView(forms.ModalFormView):
    form_class = config_forms.ModifyDiscountForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "modify_discount_modal"
    modal_header = _("Modify Discount")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:modify_discount"

    def get_initial(self):
        return get_discount(self.request, id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(ModifyDiscountView, self).get_context_data(**kwargs)
        type_id = self.kwargs['id']
        context['submit_url'] = reverse(self.submit_url, args=[type_id])
        return context


#
# Plan views
#
class CreatePlanView(forms.ModalFormView):
    form_class = config_forms.CreatePlanForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "create_plan_modal"
    modal_header = _("Create Billing Plan")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:create_plan"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(CreatePlanView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url)
        return context


class ModifyPlanView(forms.ModalFormView):
    form_class = config_forms.ModifyPlanForm
    template_name = 'billing/config/billing_form.html'
    success_url = reverse_lazy("horizon:billing:billing_config:index")
    modal_id = "modify_plan_modal"
    modal_header = _("Modify Billing Plan")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_config:modify_plan"

    def get_initial(self):
        plan = get_plan(self.request, id=self.kwargs['id'])
        if plan['billing_type'] == RAB_BILLING_TYPE_ID and 'attrs' in plan:
            for attr in plan['attrs']:
                plan['attr_' + attr['name']] = attr['value']
        return plan

    def get_context_data(self, **kwargs):
        context = super(ModifyPlanView, self).get_context_data(**kwargs)
        type_id = self.kwargs['id']
        context['submit_url'] = reverse(self.submit_url, args=[type_id])
        return context

