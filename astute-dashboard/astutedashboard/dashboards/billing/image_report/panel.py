#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _

import horizon
from astutedashboard.dashboards.billing import dashboard

class WindowsInstanceReport(horizon.Panel):
    name = _("Windows/SQL Instance Report")
    slug = "windows_instance_report"

    #Only the following roles are allowed to access this dashboard
    permissions = (('openstack.roles.admin',),)

dashboard.M1AstutePanels.register(WindowsInstanceReport)
