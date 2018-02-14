#
# Copyright 2017 NephoScale
#

from django.utils.translation import ugettext_lazy as _

import horizon
from astutedashboard.dashboards.billing import dashboard

class Config(horizon.Panel):
    name = _("Configuration")
    slug = "billing_config"

    #Only the following roles are allowed to access this dashboard
    permissions = (('openstack.roles.admin',
                    'openstack.roles.finance', \
                    'openstack.roles.support', \
                    'openstack.roles.catalogue'
                  ),)

dashboard.M1AstutePanels.register(Config)

