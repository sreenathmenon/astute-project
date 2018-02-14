#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _
from horizon import tables

class InvoiceFilterAction(tables.FilterAction):

    #Defining the filter_type, filter_choices etc 
    
    filter_type = "query"
    """
    filter_type = "server"
    filter_choices = (('select', _('Select'), True),
                      ('inv_code', _("Code ="), True),
                      ('amt_paid', _("Total ="), True),)
    """
    name = "filter_cust_invoices"


class UserInvoiceListingTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    inv_code = tables.Column('inv_code', verbose_name=_('Code'), \
        link="horizon:project:customer_invoices:customer_invoice_details")
    user = tables.Column('user', verbose_name=_('Account'))
    inv_date = tables.Column('inv_date', verbose_name=_('Invoice Date'))
    inv_from = tables.Column('inv_from', verbose_name=_('From Date'))
    inv_to = tables.Column('inv_to', verbose_name=_('To Date'))
    total_amt = tables.Column('total_amt', verbose_name=_('Total ($)'))
    balance_amt = tables.Column('balance_amt', verbose_name=_('Balance ($)'))
    amt_paid = tables.Column('amt_paid', verbose_name=_('Paid ($)'))
    #last_updated = tables.Column('last_updated', verbose_name=_('Last Updated'))
    #notes = tables.Column('notes', verbose_name=_('Notes'))
    status = tables.Column('status', verbose_name=_('Status'))
    policy_rules = (("identity", "identity:list_projects"),
                    ("identity", "identity:list_user_projects"))
        
    def get_object_id(self, datum):
        return datum['id']

    class Meta(object):
        name = 'customer_invoices'
        verbose_name = _('Invoices')
        row_actions = ()
        table_actions = (InvoiceFilterAction,)
