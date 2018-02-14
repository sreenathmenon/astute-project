#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api

from astutedashboard.common import \
    get_billing_types, \
    get_service_types, \
    get_plans, \
    get_discount_types, \
    get_discounts

#from astutedashboard.dashboards.admin.config import tables
from astutedashboard.dashboards.billing.config import tables

class BillingTypesTab(tabs.TableTab):
    name = _("Billing Types")
    slug = "billing_types_tab"
    table_classes = (tables.BillingTypesTable,)
    template_name = ("billing/config/_table.html")
    preload = False

    def get_billing_types_data(self):
        try:
            data = get_billing_types(self.request)
            return data

        except Exception:
            error_message = _('Unable to get billing types')
            exceptions.handle(self.request, error_message)
            return []


class ServiceTypesTab(tabs.TableTab):
    name = _("Service Types")
    slug = "service_types_tab"
    table_classes = (tables.ServiceTypesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_service_types_data(self):
        try:
            data = get_service_types(self.request)
            return data

        except Exception:
            self._has_more = False
            error_message = _('Unable to get service types')
            exceptions.handle(self.request, error_message)

            return []



class DiscountTypesTab(tabs.TableTab):
    name = _("Discount Types")
    slug = "discount_types_tab"
    table_classes = (tables.DiscountTypesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_discount_types_data(self):
        try:
            data = get_discount_types(self.request)
            return data

        except Exception:
            self._has_more = False
            error_message = _('Unable to get discount types')
            exceptions.handle(self.request, error_message)

            return []


class DiscountsTab(tabs.TableTab):
    name = _("Discounts")
    slug = "discounts_tab"
    table_classes = (tables.DiscountsTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_discounts_data(self):
        try:
            data = get_discounts(self.request)
            return data

        except Exception:
            self._has_more = False
            error_message = _('Unable to get discounts')
            exceptions.handle(self.request, error_message)

            return []


class PlansTab(tabs.TableTab):
    name = _("Plans")
    slug = "plans_tab"
    table_classes = (tables.PlansTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def get_plans_data(self):
        try:
            data = get_plans(self.request, verbose=True)
            for item in data:
                item['rate'] = "%.2f" % (item.get('rate') or 0.0)
                item['setup_fee'] = "%.2f" % (item.get('setup_fee') or 0.00)
            return data

        except Exception:
            self._has_more = False
            error_message = _('Unable to get plans')
            exceptions.handle(self.request, error_message)

            return []


class ConfigTabs(tabs.TabGroup):
    slug = "config_tabs"
    tabs = (
        BillingTypesTab,
        ServiceTypesTab,
        DiscountTypesTab,
        DiscountsTab,
        PlansTab,
    )
    sticky = True
