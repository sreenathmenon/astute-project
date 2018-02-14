#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables


class ModifyBillingInvoice(tables.LinkAction):
    name = 'modify_billing_invoice'
    verbose_name = _('Modify')
    url = 'horizon:billing:billing_invoices:modify_billing_invoice'
    ajax = True
    classes = ('ajax-modal',)
    policy_rules = (("billing", "invoice:edit"),)

class ExportInvoiceAsDAT(tables.LinkAction):
    name = 'export_as_dat'
    verbose_name = _('Export as DAT...')
    url = 'horizon:billing:billing_invoices:export_as_dat'
    ajax = True
    classes = ('ajax-modal', 'admin-billing-invoice-export-as-dat')

class ExportInvoiceAsCSV(tables.LinkAction):
    name = 'export_as_csv'
    verbose_name = _('Export as CSV...')
    url = 'horizon:billing:billing_invoices:export_as_csv'
    ajax = True
    classes = ('ajax-modal', 'admin-billing-invoice-export-as-csv')

# format helper
def format_2f(v):
    try:
        return format(v, '.2f')
    except:
        '-'

class BillingInvoicesTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    inv_code = tables.Column('inv_code', verbose_name=_('Code'), \
        link="horizon:billing:billing_invoices:billing_invoice_details")
    user = tables.Column('user', verbose_name=_('Account'))
    service_id = tables.Column('service_id', verbose_name=_('Service Id'))
    inv_date = tables.Column(lambda r: r['inv_date'].split(' ')[0], verbose_name=_('Invoice Date'))
    inv_from = tables.Column(lambda r: r['inv_from'].split(' ')[0], verbose_name=_('From Date'))
    inv_to = tables.Column(lambda r: r['inv_to'].split(' ')[0], verbose_name=_('To Date'))
    total_amt = tables.Column(lambda r: format_2f(r['total_amt']), verbose_name=_('Total ($)'))
    balance_amt = tables.Column(lambda r: format_2f(r['balance_amt']), verbose_name=_('Balance ($)'))
    amt_paid = tables.Column(lambda r: format_2f(r['amt_paid']), verbose_name=_('Paid ($)'))
    last_updated = tables.Column('last_updated', verbose_name=_('Last Updated'))
    notes = tables.Column('notes', verbose_name=_('Notes'))
    status = tables.Column('status', verbose_name=_('Status'))


    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'billing_invoices'
        verbose_name = _('Invoices')
        row_actions = (
            ModifyBillingInvoice,
            ExportInvoiceAsDAT,
            ExportInvoiceAsCSV
        )
        table_actions = ()

