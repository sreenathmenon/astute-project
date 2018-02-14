#
# Copyright 2017 NephoScale
#

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from astutedashboard.common import create_billing_plan_mapping

#Fixed contract choices given in doc shared by Telemachus
contract_choices = (('3', '3'), ('6', '6'), ('12', '12'), ('18', '18'), ('24', '24'), ('30', '30'), ('36', '36'))

class PlanActivationByUserForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1 , required=True, widget=forms.TextInput(attrs={'class':'form-control' , 'autocomplete': 'off', 'pattern':'[0-9]+', 'title':'Enter numbers Only '}))
    contract_period = forms.ChoiceField(label=_('Contract Period (in months)'), required=True, choices=contract_choices)

    def handle(self, request, data):
        try:
            plans = {data.get("id", ""): data.get("quantity", "")}
            user_id = self.request.user.tenant_id
            data['plans'] = plans
            data['user']  = user_id
 
 		    #Passing the details and creating a new user plan mapping
            create_billing_plan_mapping(data)
            return True

        except ValidationError:
            raise

        except Exception:
            exceptions.handle(request, _('Unable to activate the selected Plan.'))

