from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import memoized
from horizon.utils import validators
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import base
from openstack_dashboard.api import cinder
from openstack_dashboard.api import keystone
#from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova
from openstack_dashboard.usage import quotas
from openstack_dashboard.local import local_settings

import smtplib
import re, requests

try:
    import simplejson as json
except ImportError:
    import json
except:
    raise


from astutedashboard.common import get_admin_ksclient, \
                                   get_billing_types, \
                                   create_billing_type_mapping, \
                                   modify_billing_type_mapping, \
                                   create_user_letter, \
                                   get_projects, \
                                   get_project, \
                                   create_project, \
                                   create_user, \
                                   get_tenants, \
                                   get_users, \
                                   get_neutron_client, \
                                   create_network, \
                                   create_subnet, \
                                   list_network, \
                                   list_subnet, \
                                   create_router, \
                                   add_interface_to_router

from astutedashboard.dashboards.billing.cipher import encrypt
from openstack_dashboard.local.local_settings import CIPHER_KEY


ACCOUNT_MAPPING_FIELDS = (
    "domain_id",
    "domain_name",
    "project_mapping",
    "project_name",
    "description",
    "username",
    "password",
    "confirm_password",
    "project_id",
    "billing_type"
)
ACCOUNT_EXTRA_FIELDS = (
    "crm_account_num",
    "service_id",
    "customer_name",
    "business_reg_num",
    "registered_address",
    "authorized_officer_name",
    "authorized_officer_nric",
    "authorized_officer_phone",
    "authorized_officer_email",
    "account_manager"
)
ACCOUNT_QUOTA_FIELDS = (
    "quota_instances",
    "quota_cores",
    "quota_ram",
    "quota_floating_ips",
    "quota_fixed_ips",
    "quota_gigabytes"
)

COMMON_HORIZONTAL_TEMPLATE = "billing/type_mappings/_common_form.html"
WELCOME_EMAIL_TEMPLATE = "billing/type_mappings/welcome_email.html"

# send multipart email
def send_mail(subject=None, sender=None, to=None, body=None, html=None, smtp_host='localhost', smtp_port=25, username=None, password=None):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(to) if isinstance(to, list) else to

    # Record the MIME types of both parts - text/plain and text/html.
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    if body:
        body_part = MIMEText(body, 'plain')
        msg.attach(body_part)
    if html:
        html_part = MIMEText(html, 'html')
        msg.attach(html_part)

    smtp = smtplib.SMTP(smtp_host, smtp_port)
    smtp.ehlo()
    if username and password:
        smtp.login(username, password)
    smtp.sendmail(sender, to, msg.as_string())
    smtp.quit()


class CommonAccountGenericAction(workflows.Action):

    class Meta(object):
        name = _("Generic")
        slug = 'account_generic'

    # Hide the domain_id and domain_name by default
    domain_id = forms.CharField(
        label=_("Domain ID"),
        required=False,
        widget=forms.HiddenInput()
    )
    domain_name = forms.CharField(
        label=_("Domain Name"),
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, request, *args, **kwargs):
        super(CommonAccountGenericAction, self).__init__(request, *args, **kwargs)

        # set domain values
        #FIXME: Following line need to be checked for keystone V3 case (M1 specific roles)
        domain = keystone.get_default_domain(self.request)
        self.fields['domain_id'].widget.attrs['value'] = domain.id or ''
        self.fields['domain_name'].widget.attrs['value'] = domain.name or ''


password_requirement_str = 'must be at least 8 chars long and contain of mixed case and digit chars'


class CreateAccountGenericAction(CommonAccountGenericAction):

    class Meta(object):
        name = _("Generic")
        slug = 'account_generic'

    project_mapping = forms.ChoiceField(
        label = _('Mapping'),
        choices=[
            ('0', 'Create New Project'),
            ('1', 'Use Existing Project')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'project_mapping'
        })
    )
    project_name = forms.CharField(
        label=_('Project Name'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'must be a valid project name',
            'class': 'switched',
            'data-switch-on': 'project_mapping',
            'data-project_mapping-0': _('Project Name')
        })
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={
                'rows': 4,
                'class': 'switched',
                'data-switch-on': 'project_mapping',
                'data-project_mapping-0': _('Description')
            }
        )
    )
    username = forms.CharField(
        label=_('Project User'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'leave blank to use value of project name',
            'class': 'switched',
            'data-switch-on': 'project_mapping',
            'data-project_mapping-0': _('Project User')
        })
    )
#    password = forms.CharField(
#        label=_('Password'),
#        required=False,
#        widget=forms.TextInput(attrs={
#            'placeholder': password_requirement_str,
#            'type': 'password',
#            'class': 'switched',
#            'data-switch-on': 'project_mapping',
#            'data-project_mapping-0': _('Password')
#        })
#    )
#    confirm_password = forms.CharField(
#        label=_('Confirm Password'),
#        required=False,
#        widget=forms.TextInput(attrs={
#            'placeholder': 'must match password value above',
#            'type': 'password',
#            'class': 'switched',
#            'data-switch-on': 'project_mapping',
#            'data-project_mapping-0': _('Confirm Password')
#        })
#    )
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.TextInput(attrs={
            'placeholder': password_requirement_str,
            'type': 'password',
            'class': 'switched',
            'data-switch-on': 'project_mapping',
            'data-project_mapping-0': _('Password')
        }),
        required = False,
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()}
    )
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        required = False,
        widget=forms.TextInput(attrs={
            'placeholder': 'must match password value above',
            'type': 'password',
            'class': 'switched',
            'data-switch-on': 'project_mapping',
            'data-project_mapping-0': _('Confirm Password')
        })
    )
    project_id = forms.ChoiceField(
        label=_('Project'),
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'project_mapping',
            'data-project_mapping-1': _('Project')
        })
    )
    billing_type = forms.ChoiceField(label=_('Billing Type'), choices=[], required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateAccountGenericAction, self).__init__(request, *args, **kwargs)

        # populate existing projects
        #Keystone connection
        #(_projects, _) = keystone.tenant_list(self.request)
        (_projects, _)  = get_tenants(self.request)
        projects = [(project.id, project.name) for project in _projects]
        self.fields['project_id'].choices = projects

        # populate billing types
        # TODO (div): switch on astudeclient lib [get_billing_types()]
        billing_types = [(billing_type['id'], billing_type['name']) for billing_type in get_billing_types(request)]
        self.fields['billing_type'].choices = billing_types


    # data clean up and validation
    def clean(self):
        cleaned_data = super(CreateAccountGenericAction, self).clean()

        if str(cleaned_data.get('project_mapping')) == '0':
            # validate new project fields

            #Password and confirm password field values are required
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

            msg_field_is_required = 'This field is required.'

            cleaned_data['project_name'] = (cleaned_data.get('project_name') or '').strip()
            project_name = cleaned_data['project_name']
            if project_name == '':
                self.add_error('project_name', msg_field_is_required)
            else:
                # check if specified project is already exists
                #if len([p for p in keystone.tenant_list(self.request)[0] if p.name == project_name]) > 0:
                if len([p for p in get_projects(self.request) if p.name == project_name]) > 0:
                    self.add_error('project_name', 'Project `%s` already exists.' % project_name)

            cleaned_data['username'] = (cleaned_data.get('username') or cleaned_data.get('project_name') or '').strip()
            username = cleaned_data['username']
            if username != '':
                # check if specified user is already exists
                #if len([u for u in keystone.user_list(self.request) if u.name == username]) > 0:
                ks = get_admin_ksclient()
                if len([u for u in get_users(self.request) if u.name == username]) > 0:
                    self.add_error('username', 'User `%s` already exists.' % username)

            password = cleaned_data.get('password')
            if not password:
                self.add_error('password', msg_field_is_required)
#            else:
#                # check password strength
#                if not (
#                    any(c.isupper() for c in password) and \
#                    any(c.islower() for c in password) and \
#                    any(c.isdigit() for c in password) and \
#                    len(password) >= 8
#                ):
#                    self.add_error('password', 'Password is too weak: %s.' % password_requirement_str)

            confirm = cleaned_data.get('confirm_password')
            if not confirm:
                self.add_error('confirm_password', msg_field_is_required)

            if password and confirm and password != confirm:
                self.add_error('confirm_password', 'Confirmation does not match password.')

            return cleaned_data


class UpdateAccountGenericAction(CommonAccountGenericAction):

    class Meta(object):
        name = _("Generic")
        slug = 'account_generic'

    id = forms.CharField(
        label=_("id"),
        required=True,
        widget=forms.HiddenInput()
    )
    project_id = forms.CharField(
        label=_("project_id"),
        required=True,
        widget=forms.HiddenInput()
    )
    project_name = forms.CharField(
        label=_("Account"),
        required=False,
        widget=forms.TextInput(attrs = {'readonly': 'readonly'})
    )
    billing_type = forms.CharField(
        label=_("billing_type"),
        required=False,
        widget=forms.HiddenInput()
    )
    billing_type_name = forms.CharField(
        label=_('Billing Type'),
        required=False,
        widget=forms.TextInput(attrs = {'readonly': 'readonly'})
    )

    def __init__(self, request, *args, **kwargs):
        super(UpdateAccountGenericAction, self).__init__(request, *args, **kwargs)

        # populate billing types
        # TODO (div): switch on astudeclient lib [get_billing_types()]
        billing_types = dict([(str(billing_type['id']), billing_type['name']) for billing_type in get_billing_types(request)])
        self.fields['billing_type_name'].widget.attrs['value'] = billing_types[str(self.initial['billing_type'])]


class CommonAccountDetailsAction(workflows.Action):

    class Meta(object):
        name = _("Details")
        slug = 'account_details'

    crm_account_num = forms.CharField(label=_("CRM Account #"), required=True)
    service_id = forms.CharField(label=_("Service ID"), required=True)
    customer_name = forms.CharField(label=_("Customer Name"), required=True)
    business_reg_num = forms.CharField(label=_("Business Reg. #"), required=True)
    registered_address = forms.CharField(label=_("Registered Address"), required=True)
    authorized_officer_name = forms.CharField(label=_("Authorized Officer"), required=True)
    authorized_officer_nric = forms.CharField(label=_("    - NRIC"), required=True)
    authorized_officer_phone = forms.CharField(label=_("    - Phone"), required=True)
    authorized_officer_email = forms.CharField(label=_("    - Email"), required=True)
    account_manager = forms.CharField(label=_("Account Manager"), required=True)


class CommonAccountQuotaAction(workflows.Action):

    class Meta(object):
        name = _("Quota")
        slug = 'account_quota'

    quota_instances = forms.IntegerField(label=_("Instances"), required=False)
    quota_cores = forms.IntegerField(label=_("vCPUs"), required=False)
    quota_ram = forms.IntegerField(label=_("RAM (MB)"), required=False)
    quota_floating_ips = forms.IntegerField(label=_("Floating IPs"), required=False)
    quota_fixed_ips = forms.IntegerField(label=_("Fixed IPs"), required=False)
    quota_gigabytes = forms.IntegerField(label=_("Total Size of Volumes and Snapshots (GB)"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CommonAccountQuotaAction, self).__init__(request, *args, **kwargs)

        # set fields min value to -1
        for field in self.fields:
            self.fields[field].widget.attrs.update({'min': '-1'})

        # populate volume type quotas
        for volume_type in cinder.volume_type_list(self.request):
            self.fields['quota_gigabytes_' + volume_type.name] = forms.IntegerField(
                label=_("%s (GB)" % volume_type.name),
                required=False
            )

        # display default quota values
        for quota in nova.itenant_quota_get(self.request, None):
            field = 'quota_' + quota.name
            if self.fields.get(field):
                self.fields[field].widget.attrs.update({'placeholder': str(quota.limit)})

        for quota in cinder.default_quota_get(self.request, None):
            field = 'quota_' + quota.name
            if self.fields.get(field):
                self.fields[field].widget.attrs.update({'placeholder': str(quota.limit)})


class CreateAccountQuotaAction(CommonAccountQuotaAction):

    class Meta(object):
        name = _("Quota")
        slug = 'account_quota'


class UpdateAccountQuotaAction(CommonAccountQuotaAction):

    class Meta(object):
        name = _("Quota")
        slug = 'account_quota'

    def clean(self):
        usages = quotas.tenant_quota_usages(self.request, tenant_id=self.initial['project_id'])
        # Validate the quota values before updating quotas.
        bad_values = []
        for data_key, value in cleaned_data.items():
            key = data_key[6:]
            used = usages[key].get('used', 0)
            if value is not None and value >= 0 and used > value:
                bad_values.append(_('%(used)s %(key)s used') %
                                  {'used': used,
                                   'key': quotas.QUOTA_NAMES.get(key, key)})
        if bad_values:
            value_str = ", ".join(bad_values)
            msg = (_('Quota value(s) cannot be less than the current usage '
                     'value(s): %s.') %
                   value_str)
            raise forms.ValidationError(msg)


class CreateAccountGenericStep(workflows.Step):

    action_class = CreateAccountGenericAction
    template_name = COMMON_HORIZONTAL_TEMPLATE
    contributes = ACCOUNT_MAPPING_FIELDS


class UpdateAccountGenericStep(workflows.Step):

    action_class = UpdateAccountGenericAction
    template_name = COMMON_HORIZONTAL_TEMPLATE
    contributes = ("id", "project_id", "project_name", "description", "billing_type")


class CommonAccountDetailsStep(workflows.Step):

    action_class = CommonAccountDetailsAction
    template_name = COMMON_HORIZONTAL_TEMPLATE
    contributes = ACCOUNT_EXTRA_FIELDS


class CommonAccountWorkflow(workflows.Workflow):

    pass


class CreateAccountWorkflow(CommonAccountWorkflow):

    slug = "billing_create_account"
    name = "Create Account"
    finalize_button_name = _("Submit")
    success_message = _('Created new account "%s".')
    failure_message = _('Unable to create account "%s".')
    success_url = "horizon:billing:billing_type_mappings:index"
    default_steps = (
        CreateAccountGenericStep,
        CommonAccountDetailsStep
    )

    def handle(self, request, data):

        is_new_project = str(data['project_mapping']) == '0'
        project = None

        #Keystone connection
        ks = get_admin_ksclient()

        # handle project mapping
        if is_new_project:
            # create new project first
            '''
            project = keystone.tenant_create(
                request,
                data.get('project_name'),
                description=data.get('description'),
                enabled=True,
                domain=data.get('domain_id')
            )
            '''
            project = create_project(request, 
                                     data.get('project_name'), 
                                     description=data.get('description'), 
                                     enabled=True, 
                                     domain=data.get('domain_id'))

        else:
            # fetch project
            #project = keystone.tenant_get(request, data.get('project_id'))
            project = get_project(request, data.get('project_id'))

        # map project to billing account
        extra_fields = dict([(f, data[f]) for f in ACCOUNT_EXTRA_FIELDS])
        try:
            success = bool(create_billing_type_mapping(request, {
                "user": project.id,
                "billing_type": data.get('billing_type') or 1,
                "extra_fields": json.dumps(extra_fields)
            }))
            if not success:
                raise exceptions.HorizonException('Unable to create billing type mapping.')
        except:
            # clean up created project in case of error
            if is_new_project:
                #FIXME: Need to check V3 related issues
                #keystone.tenant_delete(request, project.id)
                ks.tenants.delete(project.id)
            raise


        # create user (in case of new project)
        user = None
        try:
            if is_new_project:
                '''
                user = keystone.user_create(
                    request,
                    name=data.get('username'),
                    password=data.get('password'),
                    email=data.get('authorized_officer_email'),
                    enabled=True,
                    description='General user of project `%s`' % project.name,
                    project=project.id,
                    domain=data.get('domain_id')
                )
                '''
                user = create_user(request, 
                                   name=data.get('username'),
                                   password=data.get('password'),
                                   email=data.get('authorized_officer_email'),
                                   enabled=True,
                                   description='General user of project `%s`' % project.name,
                                   project=project.id,
                                   domain=data.get('domain_id'))

        except:
            # clean up created project in case of error
            if is_new_project:
                #keystone.tenant_delete(request, project.id)
                #FIXME: Need to check V3 related issues
                ks.tenants.delete(project.id)
            raise

        # do networking deployment
        if is_new_project and getattr(local_settings, 'ASTUDE_CONFIGURE_ACCOUNT_NETWORKING', True):
            try:
                self._configure_networking(request, project)
            except Exception as e:
                print "Exception while adding network"
                print e
                pass

        self.name = project.name

        # send welcome email
        if not getattr(local_settings, 'ASTUTE_ENABLE_WELCOME_EMAIL', True):
            return True

        # send welcome email
        subj = getattr(settings, 'ASTUTE_WELCOME_EMAIL_SUBJ', 'Your new M1 Cloud Application Service')
        sender = getattr(settings, 'ASTUTE_WELCOME_EMAIL_FROM', 'donotreplyCAS@m1.com.sg')
        host = getattr(settings, 'ASTUTE_SMTP_HOST', 'localhost')
        port = getattr(settings, 'ASTUTE_SMTP_PORT', 25)
        user = getattr(settings, 'ASTUTE_SMTP_USER', None)
        pswd = getattr(settings, 'ASTUTE_SMTP_PASS', None)
        html = render_to_string(WELCOME_EMAIL_TEMPLATE, data)

        # save the email content for the project user
        try:
            success = bool(create_user_letter(request, {
                "user": project.id,
                "content": encrypt(CIPHER_KEY, html),
            }))

        except Exception as e:
            print '*******mail*****'
            print e
            pass

        try:
            send_mail(
                subject=subj,
                sender=sender,
                to=data.get('authorized_officer_email'),
                body=None,
                html=html,
                smtp_host=host,
                smtp_port=port,
                username=user,
                password=pswd
            )
        except Exception as e:
            print e
            #raise exceptions.RecoverableError("Account has been created but error ocured on sending welcome email")
            pass

	return True

    def _configure_networking(self, request, project):
        # configuration
        external_network_name = getattr(local_settings, 'ASTUDE_ACCOUNT_EXTERNAL_NETWORK_NAME', 'public')
        internal_network_name = getattr(local_settings, 'ASTUDE_ACCOUNT_INTERNAL_NETWORK_NAME', '{{ account }}-nw')
        internal_network_cidr = getattr(local_settings, 'ASTUDE_ACCOUNT_INTERNAL_NETWORK_CIDR', '10.0.0.0/24')
        account_router_name = getattr(local_settings, 'ASTUDE_ACCOUNT_ROUTER_NAME', '{{ account }}-gw')

        rexp = r'\{\{\s*account\s*\}\}'
        external_network_name = re.sub(rexp, project.name, external_network_name)
        internal_network_name = re.sub(rexp, project.name, internal_network_name)
        account_router_name = re.sub(rexp, project.name, account_router_name)

        # create network
        #network = neutron.network_create(request, tenant_id=project.id, name=internal_network_name)
        network = create_network(request, tenant_id=project.id, name=internal_network_name)
        
        #subnet = neutron.subnet_create(request, network_id=network.id, tenant_id=project.id, name=internal_network_cidr, cidr=internal_network_cidr, ip_version=4)
        subnet = create_subnet(request, network_id=network.id, tenant_id=project.id, name=internal_network_cidr, cidr=internal_network_cidr, ip_version=4)
 
        # find external network
        #external_network = [n for n in neutron.network_list(request) if n.name == external_network_name]
        external_network = [n for n in list_network(request) if n.name == external_network_name]
        if len(external_network) < 1:
            raise exceptions.HorizonException('Public network `%s` not found.' % external_network_name)
        external_network = external_network[0]
        # create router
        params = {
            "tenant_id": project.id,
            "name": account_router_name,
            "external_gateway_info": {
                "network_id": external_network.id
            }
        }
        
        #router = neutron.router_create(request, **params)
        router = create_router(request, **params)
        
        # apply internal network into account router
        #neutron.router_add_interface(request, router.id, subnet_id=subnet.id)
        add_interface_to_router(request, router.id, subnet_id=subnet.id)

        return True


class UpdateAccountWorkflow(CommonAccountWorkflow):

    slug = "billing_update_account"
    name = "Modify Account"
    finalize_button_name = _("Submit")
    success_message = _('Updated account "%s".')
    failure_message = _('Unable to update account "%s".')
    success_url = "horizon:billing:billing_type_mappings:index"
    default_steps = (
        UpdateAccountGenericStep,
        CommonAccountDetailsStep
    )

    def handle(self, request, data):

        extra_fields = dict([(f, data[f]) for f in ACCOUNT_EXTRA_FIELDS])
        params = {
            "user": data['project_id'],
            "billing_type": data['billing_type'],
            "extra_fields": json.dumps(extra_fields)
        }
        modify_billing_type_mapping(request, data['id'], params)

        self.name = data.get('project_name')

        return True

