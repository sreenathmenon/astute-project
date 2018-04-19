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
    get_project, \
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

from openstack_dashboard.api import keystone
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from astutedashboard.common import get_user_letter
from astutedashboard.dashboards.billing.cipher import decrypt
from openstack_dashboard.local.local_settings import CIPHER_KEY
from horizon import exceptions
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

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

class ResendWelcomeLetterView(workflows.WorkflowView):
    #workflow_class = panel_worflows.ResendWelcomeLetterWorkFlow
    success_url = reverse_lazy("horizon:billing:billing_type_mappings:index")
    submit_url = "horizon:billing:billing_type_mappings:resend_welcome_letter"

    def get_initial(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super(ResendWelcomeLetterView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context

# handles request to resend welcome letter
def email(request, *args, **kwargs):

    # Initialise the variables
    WELCOME_EMAIL_TEMPLATE = "billing/type_mappings/welcome_email.html"
    id = kwargs['id']
    account = get_billing_type_mapping(request, id)
    project_id = account['user']
    #details = keystone.tenant_get(request, project_id)
    details = get_project(request, project_id)
    to_addr = account['extra_fields']['authorized_officer_email']

    # send welcome email
    subj = getattr(settings, 'ASTUTE_WELCOME_EMAIL_SUBJ', 'Your new M1 Cloud Application Service')
    sender = getattr(settings, 'ASTUTE_WELCOME_EMAIL_FROM', 'donotreplyCAS@m1.com.sg')
    host = getattr(settings, 'ASTUTE_SMTP_HOST', 'localhost')
    port = getattr(settings, 'ASTUTE_SMTP_PORT', 25)
    user = getattr(settings, 'ASTUTE_SMTP_USER', None)
    pswd = getattr(settings, 'ASTUTE_SMTP_PASS', None)
    content = get_user_letter(request, project_id)[0]['content']
    html = decrypt(CIPHER_KEY, content)

    try:
        panel_worflows.send_mail(
            subject=subj,
            sender=sender,
            to=to_addr,
            body=None,
            html=html,
            smtp_host=host,
            smtp_port=port,
            username=user,
            password=pswd
        )
        messages.success(request, "Successfully sent email")
    except Exception as e:
        from horizon import exceptions
        from django.utils.translation import ugettext_lazy as _
        #raise exceptions.handle(request, _('Error while sending email'))
        #raise exceptions.HorizonException('Unable to create billing type mapping.')
        messages.error(request, 'Error while sending email')
        print "=====================exception=================="
        print e
        print "=====================exception=================="
        #raise exceptions.RecoverableError("Account has been created but error ocured on sending welcome email")
        #pass
        #return HttpResponseRedirect('index/')
    return HttpResponseRedirect(reverse("horizon:billing:billing_type_mappings:index"))
    #return HttpResponseRedirect('index/')
