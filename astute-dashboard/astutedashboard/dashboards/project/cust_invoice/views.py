from django.views import generic

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import tables

from astutedashboard.dashboards.project.cust_invoice \
    import tables as invoice_table
from astutedashboard.common import get_invoices, \
                                   get_invoice, \
                                   get_discounts, \
                                   get_plans, \
                                   get_user_invoices, \
                                   PERCENTS_DISCOUNT_TYPE_ID, \
                                   OVERRIDE_DISCOUNT_TYPE_ID
    
    
class IndexView(tables.DataTableView):
    table_class = invoice_table.UserInvoiceListingTable
    template_name = 'project/cust_invoice/index.html'
    page_title = _("Invoices")

    def get_data(self):
        return get_user_invoices(self.request, verbose=True)

class UserInvoiceDetailsView(generic.TemplateView):
    template_name = 'project/cust_invoice/invoice.html'
    
    def get_context_data(self, **kwargs):
        context = super(UserInvoiceDetailsView, self).get_context_data(**kwargs)
        id = self.kwargs['invoice_id']
        context['invoice'] = get_invoice(self.request, id, verbose=False)
        #context['invoice'] =  get_user_inv_details(self.request, id, verbose=True)

        plans = {}
        for plan in get_plans(self.request):
            plans[plan['id']] = plan
        
        #Same as Admin/Invoice Details View page
        discounts = {}
        for discount in get_discounts(self.request):
            discounts[discount['id']] = discount
            
        for item in context['invoice']['items']:
            item['plan'] = plans.get(item['plan_id'])['name']
            item['bill_start_date'] = item['bill_start_date'].split(' ')[0]
            item['bill_end_date']   = item['bill_end_date'].split(' ')[0]
            disc = discounts.get(item.get('discount_id'))
            if disc:
                if disc['discount_type_code'] == 'percentage':
                    item['discount'] = str(disc.get('amt')) + '%'
                elif disc['discount_type_code'] == 'override':
                    item['discount'] = '$' + str(disc.get('amt'))
                else:
                    item['discount'] = '-'
        return context
