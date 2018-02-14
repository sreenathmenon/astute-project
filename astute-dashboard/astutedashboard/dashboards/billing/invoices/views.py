#
# Copyright 2017 NephoScale
#

from datetime import datetime

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs

from astutedashboard.common import get_invoices, get_invoice, get_billing_type_mappings
'''
from astutedashboard.dashboards.admin.invoices \
    import forms as panel_forms
from astutedashboard.dashboards.admin.invoices \
    import tables as panel_tables
'''
from astutedashboard.dashboards.billing.invoices \
    import forms as panel_forms
from astutedashboard.dashboards.billing.invoices \
    import tables as panel_tables


from astutedashboard.common import \
    get_projects, \
    get_service_types, \
    get_plans, \
    get_billing_plan_mappings, \
    get_discounts, \
    PERCENTS_DISCOUNT_TYPE_ID, \
    OVERRIDE_DISCOUNT_TYPE_ID


#
# Billing Discount Mappings views
#

class IndexView(tables.DataTableView):
    table_class = panel_tables.BillingInvoicesTable
    template_name = 'billing/invoices/index.html'
    page_title = _("Invoices")

    def get_data(self):
        account = self.request.session.get('admin_billing_invoices_filter_account')
        period_from = self.request.session.get('admin_billing_invoices_filter_period_from')
        period_to = self.request.session.get('admin_billing_invoices_filter_period_to')
    	return get_invoices(self.request,
            account=account,
            period_from=period_from,
            period_to=period_to,
            verbose=True)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['accounts'] = get_billing_type_mappings(self.request, verbose=True)
        context['admin_billing_invoices_filter_endpoint'] = 'search_filter'
        context['admin_billing_invoices_filter_account'] = self.request.session.get('admin_billing_invoices_filter_account') or ''
        context['admin_billing_invoices_filter_period_from'] = self.request.session.get('admin_billing_invoices_filter_period_from') or ''
        context['admin_billing_invoices_filter_period_to'] = self.request.session.get('admin_billing_invoices_filter_period_to') or ''
        return context

class ModifyBillingInvoiceView(forms.ModalFormView):
    form_class = panel_forms.ModifyBillingInvoiceForm
    template_name = 'billing/invoices/modal_form.html'
    success_url = reverse_lazy("horizon:billing:billing_invoices:index")
    modal_id = "modify_billing_invoice_modal"
    modal_header = _("Modify Billing Account")
    submit_label = _("Submit")
    submit_url = "horizon:billing:billing_invoices:modify_billing_invoice"

    def get_initial(self):
        return get_invoice(self.request, self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(ModifyBillingInvoiceView, self).get_context_data(**kwargs)
        id = self.kwargs.get('id')
        context['submit_url'] = reverse(self.submit_url, args=[id])
        return context


class BillingInvoiceDetailsView(generic.TemplateView):
    template_name = 'billing/invoices/invoice.html'

    def get_context_data(self, **kwargs):
        context = super(BillingInvoiceDetailsView, self).get_context_data(**kwargs)
        id = self.kwargs['id']
        context['invoice'] = get_invoice(self.request, id, verbose=True)
        discounts = dict([(d['id'], d) for d in get_discounts(self.request)])
        for item in context['invoice']['items']:
            item['bill_start_date'] = item['bill_start_date'].split(' ')[0]
            item['bill_end_date'] = item['bill_end_date'].split(' ')[0]
            disc = discounts.get(item.get('discount_id'))
            if disc:
                if disc['discount_type_code'] == 'percentage':
                    item['discount'] = str(disc.get('amt')) + '%'
                elif disc['discount_type_code'] == 'override':
                    item['discount'] = '$' + str(disc.get('amt'))
                else:
                    item['discount'] = '-'
        return context


class CsvReportView(generic.View):
    def get(self, request, **response_kwargs):
        render_class = ReportCsvRenderer
        response_kwargs.setdefault("filename", "usage.csv")
        context = {'usage': load_report_data(request)}
        resp = render_class(request=request,
                            template=None,
                            context=context,
                            content_type='csv',
                            **response_kwargs)
        return resp


# invoices filter handler
def search_filter(request):

    account = request.POST.get('account') or request.GET.get('account')
    period_from = request.POST.get('period_from') or request.GET.get('period_from')
    period_to = request.POST.get('period_to') or request.GET.get('period_to')

    # store/purge filter params
    if account:
        request.session['admin_billing_invoices_filter_account'] = account
    else:
        try:
            del request.session['admin_billing_invoices_filter_account']
        except KeyError:
            pass

    if period_from:
        request.session['admin_billing_invoices_filter_period_from'] = period_from
    else:
        try:
            del request.session['admin_billing_invoices_filter_period_from']
        except KeyError:
            pass

    if period_to:
        request.session['admin_billing_invoices_filter_period_to'] = period_to
    else:
        try:
            del request.session['admin_billing_invoices_filter_period_to']
        except KeyError:
            pass

    # force session save
    request.session.modified = True

    return HttpResponse(200)


#
# export invoices in DAT format
#
def export_as_dat(request, id):
    invoices = []
    #
    # get list of invoice(s) for export
    #
    account = request.session.get('admin_billing_invoices_filter_account')
    period_from = request.session.get('admin_billing_invoices_filter_period_from')
    period_to = request.session.get('admin_billing_invoices_filter_period_to')
    if id == '*':
        # export all (filtered) invoices
        invoices = get_invoices(request,
            account=account,
            period_from=period_from,
            period_to=period_to
            )
#yad: delete
#,
#            verbose=True)
    else:
        # export single invoice
        invoices.append(get_invoice(request, id))

    # prepare required data
    accounts = {}
    for account in get_billing_type_mappings(request):
        accounts[account['user']] = account
    plans = {}
    for plan in get_plans(request):
        plans[plan['id']] = plan

    # prepare required strings
    timestamp  = datetime.now().strftime("%Y%m%d%H%M%S")
    seq_number = request.session.get('admin_billing_invoices_export_dat_seq_number') or 0
    if seq_number >= 9999:
        seq_number = 0
    seq_number += 1
    request.session['admin_billing_invoices_export_dat_seq_number'] = seq_number
    request.session.modified = True

    seq_number = "{:0>4}".format(seq_number)

    #
    # prepare file content
    #
    content = ""

    # add header
    content += "{:3}{:14}{:4}{:7}{:16}{:5}{:3}{:8}{:4}\n".format(
        'HDR',
        timestamp,
        '0',
        '0',
        'HDS',
        'V1.0',
        '',
        '',
        ''
    )
    # add detail records
    records_sequence = 0
    for invoice in invoices:
        account = accounts.get(invoice['user'])
        service_id = (account.get('extra_fields') or {}).get('service_id') or ''
        for item in invoice['items']:
            records_sequence += 1
            plan = plans.get(item['plan_id'])
            content += "{:3}{:32}{:21}{:21}{:5}{:5}{:5}{:5}{:5}{:23}{:14}{:8}{:8}{:3}{:2}{:{lenght}}{:{lenght}}{:8}{:8}{:10}{:5}{:1}\n".format(
                'SUB',
                '{:0>12}_{}'.format(invoice['id'], invoice['inv_date'].replace('-', '').replace(' ' , '').replace(':', ''))[:32],
                '6596800000',
                service_id[:21],
#yad: delete
#                invoice['inv_code'][:21],
                '221',
                '5712',
                '10',
                '10',
                '238',
                '6596800000',
                datetime.now().strftime("%Y%m%d%H%M%S"),
#yad: delete
#                timestamp,
                '1',
                str(item['total_amt']*100).split('.')[0][:8],
#yad: delete
#                str(int(float(item['total_amt']) * 100))[:8], # ???
#yad: delete
#                int(float(invoice['total_amt']) * 100), # ???
                '0',
                '20',
                plan and plan.get('description').encode('utf8')[:50],
                plan and plan.get('description').encode('utf8')[:50],
#yad: delete
#                item['description'].encode('utf8'),
#                item['description'].encode('utf8'),
                item['bill_start_date'].split(' ')[0].replace('-', ''),
                item['bill_end_date'].split(' ')[0].replace('-', ''),
#yad: delete
#                invoice['notes'],
#                invoice['notes'],
#                invoice['inv_from'].split(' ')[0].replace('-', ''),
#                invoice['inv_to'].split(' ')[0].replace('-', ''),
                '',
                '',
                '',
                lenght = 50 + len(plan.get('description').encode('utf8')) - len(plan.get('description'))
            )

    # add trailer
    content += "{:3}{:14}{:4}{:7}{:16}{:5}{:8}{:10}{:10}{:42}\n".format(
        'TRL',
        timestamp,
        '0',
        str(records_sequence)[:7],
        'HDS',
        'V1.0',
        seq_number[:8],
        '',
        '',
        ''
    )

    #
    # return data
    #
    response = HttpResponse(content, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=HDS_CHARGINGCDR_%s_%s.dat' % (
        timestamp[:-2],
        seq_number
    )
    return response


#
# export invoices in CSV format
#
def export_as_csv(request, id):
    invoices = []
    #
    # get list of invoice(s) for export
    #
    # export all (filtered) invoices
    account = request.session.get('admin_billing_invoices_filter_account')
    period_from = request.session.get('admin_billing_invoices_filter_period_from')
    period_to = request.session.get('admin_billing_invoices_filter_period_to')
    if id == '*':
        invoices = get_invoices(request,
            account=account,
            period_from=period_from,
            period_to=period_to)
    else:
        # export single invoice
        invoices.append(get_invoice(request, id))

    # prepare required strings
    timestamp  = datetime.now().strftime("%Y%m%d%H%M%S")
    seq_number = request.session.get('admin_billing_invoices_export_csv_seq_number') or 0
    if seq_number >= 9999:
        seq_number = 0
    seq_number += 1
    request.session['admin_billing_invoices_export_csv_seq_number'] = seq_number
    request.session.modified = True

    seq_number = "{:0>4}".format(seq_number)

    # prepare required data
    services = dict([(s['id'], s) for s in get_service_types(request)])
    accounts = dict([(a['user'], a) for a in get_billing_type_mappings(request)])
    plan_maps = dict([(pm['user'], pm) for pm in get_billing_plan_mappings(request)])
    plans = dict([(p['id'], p) for p in get_plans(request)])

    #
    # prepare file content
    #
    content = ""
    # title
    content += "Usage & Billing Report Reference numver: SGM1%s\n" % timestamp[0:6]
    content += "Period: %s to %s\n" % (period_from, period_to)
    content += "\n"
    # table header
    content += ",".join([
        "Customer Account ID",
        "Service ID",
        "Customer Name",
        "Billing Period (From)",
        "Billing Period (To)",
        "Item Code",
        "Product Description",
        "Bill Description",
        "Unit",
        "Quantity",
        "Service Start Date",
        "Service Termination Date",
        "Quantity (after proration) or Usage cut off at 25th",
        "Unit Price according to product catalogue (SGD)",
        "Mothly Total before discount (SGD)",
        "Discount",
        "Billing Amount in M1 bill (SGD)",
        "\n"
    ])
    #content += "\n"
    # table content
    for invoice in invoices:
        content += "\n"
        account = accounts.get(invoice['user'])
        for item in invoice['items']:
            if (item.get('qty') == 0) or (item.get('rate') == 0):
                discount = '0%'
            else:
                discount = str(round(item.get('discount_amt')/(item.get('qty')*item.get('rate'))*100)) + '%'
            plan_map = plan_maps.get(invoice['user'])
            plan = plans.get(item['plan_id'])
#yad: delete
#            plan = plans.get(plan_map and plan_map['plan_id'])
            service = services.get(plan and plan['service_type'])
            content += ",".join([
                '"%s"' % (account and account['extra_fields'].get('crm_account_num') or '#%s' % invoice.get('user')),
                '"%s"' % (account and account['extra_fields'].get('service_id') or '#%s' % invoice.get('user')),
                '"%s"' % (account and account['extra_fields'].get('customer_name') or '#%s' % invoice.get('user')),
                invoice.get('inv_from') or '-' ,
                invoice.get('inv_to') or '-',
                plan and plan.get('code') or '-',
#yad: delete
#                service and service.get('code') or '-',
                '"%s"' % plan and plan.get('description'),
#yad: delete
#                '"%s"' % item.get('description'),
                item.get('description'),
                service and service.get('units') or '-',
                str(item.get('qty')) or '-',
#yad: delete
#                plan_maps and plan_maps.get('created_on') or '-',
#                plan_maps and plan_maps.get('inactive_on') or '-',
                plan_map and plan_map.get('created_on') or '-',
                plan_map and plan_map.get('inactive_on') or '-',
                str(item.get('qty')) or '-',
                '$' + str(item.get('rate')) or '-',
                '$' + str(item.get('qty')*item.get('rate')) or '-',
                discount,
                '$' + str(item.get('total_amt')) or '-',
                '\n'
            ])

    #
    # return data
    #
    response = HttpResponse(content, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=HDS_CHARGINGCDR_%s_%s.csv' % (
        timestamp[:-2],
        seq_number
    )
    return response
