#
# Copyright 2017 NephoScale
#

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api

from astutedashboard.common import \
    create_billing_type, \
    modify_billing_type, \
    create_service_type, \
    modify_service_type, \
    create_discount, \
    modify_discount, \
    create_plan, \
    modify_plan, \
    get_billing_types, \
    get_discount_types, \
    get_service_types, \
    get_flavors, \
    PAYG_BILLING_TYPE_ID, \
    RAB_BILLING_TYPE_ID




#
# helper routines
#

# generate service types list
def gen_billing_types(request):
    data = []
    for item in get_billing_types(request):
        data.append((item['id'], _(item['name'])))
    return data

# generate dicount types list
def gen_discount_types(request):
    data = []
    for item in get_discount_types(request):
        data.append((item['id'], _(item['name'])))
    return data

# generate service types list
def gen_service_types(request):
    data = []
    for item in get_service_types(request):
        data.append((item['id'], _(item['name'])))
    return data

# generate flavors list
def gen_flavors(request):
    data = [(0, '')]
    for flavor in get_flavors(request):
        data.append((flavor.id, '%s (CPU: %s; RAM: %sMB, Disk: %sGB)' % ( \
        	flavor.name, \
        	flavor.vcpus, \
        	flavor.ram, \
        	flavor.disk
        )))
    return data


#
# Billing Type forms
#

class CreateBillingTypeForm(forms.SelfHandlingForm):

    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))

    def handle(self, request, data):
        try:
            create_billing_type(request, data=data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create billing type.'))


class ModifyBillingTypeForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))

    def handle(self, request, data):
        type_id = data.pop('id', None)
        if not type_id:
            exceptions.handle(request, _('Invalid request.'))
            return False
        try:
            modify_billing_type(request, id=type_id, data=data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify billing type.'))

#
# Service Type forms
#

class CreateServiceTypeForm(forms.SelfHandlingForm):

    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=64, label=_("Code"), required=False)
    units = forms.CharField(max_length=32, label=_("Units"), required=False)

    def handle(self, request, data):
        try:
            create_service_type(request, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create service type.'))


class ModifyServiceTypeForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=64, label=_("Code"), required=False)
    units = forms.CharField(max_length=32, label=_("Units"))

    def handle(self, request, data):
        type_id = data.pop('id', None)
        if not type_id:
            exceptions.handle(request, _('Invalid request.'))
            return False
        try:
            modify_service_type(request, type_id, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to service billing type.'))

#
# Discount forms
#

class CreateDiscountForm(forms.SelfHandlingForm):

    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))
    discount_type_id = forms.ChoiceField(label=_('Discount Type'), choices=[])
    expiration_date = forms.DateField(label=_('Expiration Date'))
    amt = forms.FloatField(label=_('Amount'))
    notes = forms.CharField(max_length=255, label=_("Notes"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateDiscountForm, self).__init__(request, *args, **kwargs)
        # set discount types
        self.fields['discount_type_id'].choices = gen_discount_types(request)

    def handle(self, request, data):
        data['expiration_date'] = str(data['expiration_date'])
        try:
            create_discount(request, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create discount type.'))


class ModifyDiscountForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))
    discount_type_id = forms.ChoiceField(label = _('Discount Type'), choices=[])
    expiration_date = forms.DateField(label=_('Expiration Date'), required=False)
    amt = forms.FloatField(label=_('Amount'))
    notes = forms.CharField(max_length=255, label=_("Notes"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(ModifyDiscountForm, self).__init__(request, *args, **kwargs)
        # set discount types
        self.fields['discount_type_id'].choices = gen_discount_types(request)

    def handle(self, request, data):
        data['expiration_date'] = str(data['expiration_date'])
        type_id = data.pop('id', None)
        if not type_id:
            exceptions.handle(request, _('Invalid request.'))
            return False
        try:
            modify_discount(request, type_id, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify discount type.'))



#
# Billing Plan forms
#

class CreatePlanForm(forms.SelfHandlingForm):

    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))
    service_type = forms.ChoiceField(label = _('Service Type'), choices=[])
    rate = forms.FloatField(label=_('Rate'))
    setup_fee = forms.FloatField(label=_('Setup Fee'), required=False)
    billing_type = forms.ChoiceField(
        label = _('Billing Type'),
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'billing_type'
        })
    )
    ref_id = forms.ChoiceField(
        label = _('Flavor'),
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-1': _('Flavor')
        })
    )
    attr_instances = forms.FloatField(
        label=_("Instances"),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('Instances')
        })
    )
    attr_cpu = forms.FloatField(
        label=_("CPU"),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('CPU')
        })
    )
    attr_ram = forms.FloatField(
        label=_("RAM (MB)"),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('RAM (GB)')
        })
    )
    attr_storage = forms.FloatField(
        label=_("Storage (GB)"),
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('Storage (GB)')
        })
    )
    description = forms.CharField(label = _('Description'))
    metadata_mark = forms.CharField(max_length=255, label=_("Image Mark"), required=False)


    def __init__(self, request, *args, **kwargs):
        super(CreatePlanForm, self).__init__(request, *args, **kwargs)
        # set discount types
        self.fields['service_type'].choices = gen_service_types(request)
        self.fields['billing_type'].choices = gen_billing_types(request)
        self.fields['billing_type'].choices.append((None, '-'))
        self.fields['ref_id'].choices = gen_flavors(request)

    def handle(self, request, data):
        print "================data in handle----------------"
        print data
        try:
            attr_instances =  data.pop('attr_instances')
            attr_cpu = data.pop('attr_cpu')
            attr_ram = data.pop('attr_ram')
            attr_storage = data.pop('attr_storage')
            if int(data['billing_type']) == RAB_BILLING_TYPE_ID:
                data['attrs'] = {}
                if attr_instances:
                    data['attrs']['instances'] = attr_instances
                if attr_cpu:
                    data['attrs']['cpu'] = attr_cpu
                if attr_ram:
                    data['attrs']['ram'] = attr_ram
                if attr_storage:
                    data['attrs']['storage'] = attr_storage
            create_plan(request, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to create billing plan.'))


class ModifyPlanForm(forms.SelfHandlingForm):

    id = forms.CharField(label=_("ID"), widget=forms.HiddenInput())
    name = forms.CharField(max_length=255, label=_("Name"))
    code = forms.CharField(max_length=32, label=_("Code"))
    service_type = forms.ChoiceField(label = _('Service Type'), choices=[])
    rate = forms.FloatField(label=_('Rate'))
    setup_fee = forms.FloatField(label=_('Setup Fee'), required=False)
    billing_type = forms.ChoiceField(
        label = _('Billing Type'),
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'billing_type'
        })
    )
    ref_id = forms.ChoiceField(
        label = _('Flavor'),
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-1': _('Flavor')
        })
    )
    attr_instances = forms.FloatField(
        label=_("Instances"),
        required=False,
        widget=forms.NumberInput(attrs={
            'step': 1,
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('Instances')
        })
    )
    attr_cpu = forms.FloatField(
        label=_("CPU"),
        required=False,
        widget=forms.NumberInput(attrs={
            'step': 1,
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('CPU')
        })
    )
    attr_ram = forms.FloatField(
        label=_("RAM (MB)"),
        required=False,
        widget=forms.NumberInput(attrs={
            'step': 1,
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('RAM (GB)')
        })
    )
    attr_storage = forms.FloatField(
        label=_("Storage (GB)"),
        required=False,
        widget=forms.NumberInput(attrs={
            'step': 1,
            'class': 'switched',
            'data-switch-on': 'billing_type',
            'data-billing_type-2': _('Storage (GB)')
        })
    )
    description = forms.CharField(label = _('Description'))
    metadata_mark = forms.CharField(max_length=255, label=_("Image Mark"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(ModifyPlanForm, self).__init__(request, *args, **kwargs)
        # set discount types
        self.fields['service_type'].choices = gen_service_types(request)
        self.fields['billing_type'].choices = gen_billing_types(request)
        self.fields['billing_type'].choices.append((None, '-'))
        self.fields['ref_id'].choices = gen_flavors(request)

    def handle(self, request, data):
        type_id = data.pop('id', None)
        if not type_id:
            exceptions.handle(request, _('Invalid request.'))
            return False
        try:
            attr_instances =  data.pop('attr_instances')
            attr_cpu = data.pop('attr_cpu')
            attr_ram = data.pop('attr_ram')
            attr_storage = data.pop('attr_storage')
            if int(data['billing_type']) == RAB_BILLING_TYPE_ID:
                data['attrs'] = {}
                if attr_instances:
                    data['attrs']['instances'] = attr_instances
                if attr_cpu:
                    data['attrs']['cpu'] = attr_cpu
                if attr_ram:
                    data['attrs']['ram'] = attr_ram
                if attr_storage:
                    data['attrs']['storage'] = attr_storage
            modify_plan(request, type_id, data)
            return True

        except Exception:
            exceptions.handle(request, _('Unable to modify billing plan.'))

