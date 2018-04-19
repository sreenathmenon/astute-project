#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
#from datetime import timedelta, date
import datetime
from django.http import HttpResponse

from astutedashboard.common import \
    get_image_usage_report
    

class IndexView(generic.TemplateView):

    #Path to the template file
    template_name = 'billing/image_report/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['admin_image_report_filter_endpoint'] = 'search_filter'
        context['image_filter_period_from']           = self.request.session.get('image_filter_period_from') or ''
        context['image_filter_period_to']             = self.request.session.get('image_filter_period_to') or ''
        
        usage_data, report_date_list = get_image_usage_report(self.request, 
                                             period_from=context['image_filter_period_from'],
                                             period_to=context['image_filter_period_to'],
                                             verbose=True)
        
        context['report_date_list'] = report_date_list
        context['usage_data']       = usage_data
        return context


def search_filter(request):
    period_from = request.POST.get('period_from') or request.GET.get('period_from')
    period_to   = request.POST.get('period_to') or request.GET.get('period_to')

    if period_from:
        request.session['image_filter_period_from'] = period_from
    else:
        try:
            del request.session['image_filter_period_from']
        except KeyError:
            pass

    if period_to:
        request.session['image_filter_period_to'] = period_to
    else:
        try:
            del request.session['image_filter_period_to']
        except KeyError:
            pass

    # force session save
    request.session.modified = True
    return HttpResponse(200)


#
# export invoices in CSV format
#
def export_as_csv(request):
    #
    # get list of invoice(s) for export
    #
    # export all (filtered) invoices
    period_from = request.session.get('image_filter_period_from') or ''
    period_to = request.session.get('image_filter_period_to') or ''

    today      = datetime.datetime.now()
    print today
    week_ago   = today - datetime.timedelta(days=6)
    print week_ago
    today      = today.strftime('%Y-%m-%d')
    print today
    week_ago   = week_ago.strftime('%Y-%m-%d')
    print week_ago

    #Default condition during initial loading of the report
    if not period_from:
        period_from = str(week_ago)
    if not period_to:
        period_to = str(today)

    usage_data, report_date_list = get_image_usage_report(request,
                                        period_from,
                                        period_to,
                                        verbose=True)

    # prepare required strings
    timestamp  = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    #
    # prepare file content
    #
    content = ""
    # title
    content += "Windows/SQL Image Usage Report: %s\n" % timestamp[0:6]
    content += "Period: %s to %s\n" % (period_from, period_to)
    content += "\n"

    content += 'Windows/SQL Image Name,'
   
    for date in report_date_list:
        content += date + ','

    content += "\n" 
    for key, value in usage_data.items():
        content += "\n"
        content += key
        for k, v in sorted(value.items()):
            content += "," + str(v)

    response = HttpResponse(content, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=M1_Windows_SQL_Usage_Report_%s.csv' % (
        timestamp[:-2],
    )
    return response
    

