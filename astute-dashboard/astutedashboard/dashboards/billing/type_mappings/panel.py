#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _

import horizon
from astutedashboard.dashboards.billing import dashboard

class BillingTypeMappings(horizon.Panel):
    name = _("Accounts")
    slug = "billing_type_mappings"

dashboard.M1AstutePanels.register(BillingTypeMappings)
