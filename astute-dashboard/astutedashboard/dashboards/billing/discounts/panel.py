#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _

import horizon
from astutedashboard.dashboards.billing import dashboard

class BillingDiscounts(horizon.Panel):
    name = _("Discounts")
    slug = "billing_discounts"

dashboard.M1AstutePanels.register(BillingDiscounts)
