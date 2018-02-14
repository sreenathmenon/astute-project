from django.views import generic

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import tables
from horizon import messages

from astutedashboard.common import get_plan, get_user_sub_plans, get_avbl_user_plans, get_user_billing_type

from astutedashboard.dashboards.project.available_plans \
    import tables as avbl_plan_tables
    
from astutedashboard.dashboards.project.available_plans \
    import forms as avbl_plan_forms
    
    
class IndexView(generic.TemplateView):
    table_class = avbl_plan_tables.AvailablePlansTable
    template_name = 'project/available_plans/index.html'
    page_title = _("Available Plans")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        billing_details = get_user_billing_type(self.request)
        
        #At-least all users must be having payg plan by default
        #Also a user will be having only 1 active billing plan at a time
        if not billing_details:
            billing_code = 'NA'
        else:
            billing_code = billing_details[0]['type_code']
        
        context['user_billing_code'] = billing_code
        context['plans'] = get_avbl_user_plans(self.request)
        return context

class UserAvblPlanDetailsView(generic.TemplateView):
    template_name  = 'project/available_plans/plan.html'
    
    def get_context_data(self, **kwargs):
        context = super(UserAvblPlanDetailsView, self).get_context_data(**kwargs)
        id = self.kwargs['id']
        context['plan_details'] = get_plan(self.request, id)
        return context
    
class PlanActivationByUserView(forms.ModalFormView):
    form_class = avbl_plan_forms.PlanActivationByUserForm
    template_name ='project/available_plans/modal_form.html'
    success_url = reverse_lazy("horizon:project:customer_subscribed_plans:index")
    modal_id = "plan_activation_user_modal"
    modal_header =_("Activate Plan")
    submit_label = _("Activate")
    success_message = _('Plan Activation was successful.')
    failure_message = _('Unable to activate the plan.')
    submit_url = "horizon:project:customer_available_plans:activate_user_plan"

    def get_initial(self):
        return get_plan(self.request, self.kwargs['id'])
       
    """
    def get_success_url(self):
        return reverse("horizon:project:customer_subscribed_plans:index")
    """
    def get_context_data(self, **kwargs):
        context = super(PlanActivationByUserView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context


