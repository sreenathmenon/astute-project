#
# Copyright 2017 NephoScale
#


from django.utils.translation import ugettext_lazy as _
import horizon


#class M1AstutePanels(horizon.PanelGroup):
class M1AstutePanels(horizon.Dashboard):
    slug = "billing"
    name = _("Billing")
    panels = ('plan_mappings', 'config', 'invoices', 'discounts', 'type_mappings')
    default_panel = 'billing_config'
   
    permissions = (('openstack.roles.admin', 
                   'openstack.roles.provisioning', \
                   'openstack.roles.finance', \
                   'openstack.roles.support', \
                   'openstack.roles.catalogue'
                  ),)
   

horizon.register(M1AstutePanels)
#horizon.register(AstutePanels)
