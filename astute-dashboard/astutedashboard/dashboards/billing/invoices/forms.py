
#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from astutedashboard.common import \
		modify_invoice

status_choices = (
	 ('pending', 'pending'),
	 ('processing', 'processing'),
	 ('paid', 'paid'),
	 ('cancelled', 'cancelled'),
)

class ModifyBillingInvoiceForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    balance_amt = forms.FloatField(label=_('Balance'))
    amt_paid = forms.FloatField(label=_('Paid'))
    notes = forms.CharField(label=_('Notes'))
    status = forms.ChoiceField(label=_('Account'), choices=status_choices)

    #def __init__(self, request, *args, **kwargs):
    #super(ModifyBillingInvoiceForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        id = data.pop('id', None)
        if not id:
            exceptions.handle(request, _('Invalid request.'))
            return False

        try:
            modify_invoice(request, id, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify invoice.'))

