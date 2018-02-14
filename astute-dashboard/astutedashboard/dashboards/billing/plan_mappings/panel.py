#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _

import horizon
from astutedashboard.dashboards.billing import dashboard

class BillingPlanMappings(horizon.Panel):
    name = _("Plan Mappings")
    slug = "billing_plan_mappings"

dashboard.M1AstutePanels.register(BillingPlanMappings)
