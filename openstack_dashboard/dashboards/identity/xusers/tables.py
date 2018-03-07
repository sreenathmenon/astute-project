# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core import exceptions as django_exceptions
from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions as horizon_exceptions
from horizon import forms
from horizon import messages
from horizon import tables
from openstack_dashboard import api
from openstack_dashboard import policy

from openstack_dashboard.dashboards.identity.xusers.common import get_admin_ksclient, \
                                                                  is_m1_user_admin                                                                  
ENABLE = 0
DISABLE = 1
KEYSTONE_V2_ENABLED = api.keystone.VERSIONS.active < 3

class CreateUserLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create User")
    url = "horizon:identity:xusers:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (('identity', 'identity:create_grant'),
                   ("identity", "identity:create_user"),
                   ("identity", "identity:list_roles"),
                   ("identity", "identity:list_projects"),)
 
    def allowed(self, request, user):
        return api.keystone.keystone_can_edit_user()

class EditUserLink(policy.PolicyTargetMixin, tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:identity:xusers:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("identity", "identity:update_user"),
                    ("identity", "identity:list_projects"),)
    policy_target_attrs = (("user_id", "id"),)
 
    def allowed(self, request, user):
        return api.keystone.keystone_can_edit_user()

class ChangePasswordLink(policy.PolicyTargetMixin, tables.LinkAction):
    name = "change_password"
    verbose_name = _("Change Password")
    url = "horizon:identity:xusers:change_password"
    classes = ("ajax-modal",)
    icon = "key"
    policy_rules = (("identity", "identity:change_password"),)
    policy_target_attrs = (("user_id", "id"),)
 
    def allowed(self, request, user):
        return api.keystone.keystone_can_edit_user()

class ToggleEnabled(policy.PolicyTargetMixin, tables.BatchAction):
    name = "toggle"

    @staticmethod
    def action_present(count):
        return (
            ungettext_lazy(
                u"Enable User",
                u"Enable Users",
                count
            ),
            ungettext_lazy(
                u"Disable User",
                u"Disable Users",
                count
            ),
        )

    @staticmethod
    def action_past(count):
        return (
            ungettext_lazy(
                u"Enabled User",
                u"Enabled Users",
                count
            ),
            ungettext_lazy(
                u"Disabled User",
                u"Disabled Users",
                count
            ),
        )
    classes = ("btn-toggle",)
    policy_rules = (("identity", "identity:update_user"),)
    policy_target_attrs = (("user_id", "id"),)

    def allowed(self, request, user=None):
        if not api.keystone.keystone_can_edit_user():
            return False

        self.enabled = True
        if not user:
            return self.enabled
        self.enabled = user.enabled
        if self.enabled:
            self.current_present_action = DISABLE
        else:
            self.current_present_action = ENABLE
        return True

    def update(self, request, user=None):
        super(ToggleEnabled, self).update(request, user)
        if user and user.id == request.user.id:
            self.attrs["disabled"] = "disabled"

    def action(self, request, obj_id):
        if obj_id == request.user.id:
            messages.info(request, _('You cannot disable the user you are '
                                     'currently logged in as.'))
            return
        if self.enabled:
            if is_m1_user_admin(request):
                ksclient = get_admin_ksclient()
                if api.keystone.VERSIONS.active < 3:
                    ksclient.users.update_enabled(obj_id, False)
                else:
                    ksclient.users.update(obj_id, enabled=False)
            else:
                api.keystone.user_update_enabled(request, obj_id, False)
        
            self.current_past_action = DISABLE
        else:
            if is_m1_user_admin(request):
                ksclient = get_admin_ksclient()
                if api.keystone.VERSIONS.active < 3:
                    ksclient.users.update_enabled(obj_id, True)
                else:
                    ksclient.users.update(obj_id, enabled=True)
            else:
                api.keystone.user_update_enabled(request, obj_id, True)
                
            self.current_past_action = ENABLE

class Disable2FAAction(policy.PolicyTargetMixin, tables.Action):
    name = "disable2fa"
    verbose_name = _("Disable Two Factor Authentication")
    policy_rules = (("identity", "identity:update_user"),)
    policy_target_attrs = (("user_id", "id"),)
   
    def single(self, table, request, obj_id):
        user = table.get_object_by_id(obj_id)
        try:
            ksclient = get_admin_ksclient()
            kwargs = {
                "two_factor_enabled": False
            }

            #if 'two_factor_enabled' in user:
            if user.two_factor_enabled:
                if user.two_factor_enabled ==  True:
                    update = ksclient.users.update(obj_id, **kwargs)
                    msg = _('Successfully disabled Two Factor Authentication for "%s"'
                            ) % user.name
                    messages.success(request, msg)
            else:
                msg = _('Two Factor Authentication is already disabled for "%s"'
                       ) % user.name
                messages.info(request, msg)
        except Exception:
            horizon_exceptions.handle(request, _("Unable to disable Two Factor Authentication for the user!"))


class DeleteUsersAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete User",
            u"Delete Users",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted User",
            u"Deleted Users",
            count
        )
    policy_rules = (("identity", "identity:delete_user"),)
 
    def allowed(self, request, datum):
        if not api.keystone.keystone_can_edit_user() or \
                (datum and datum.id == request.user.id):
            return False
        return True

    def delete(self, request, obj_id):
        if is_m1_user_admin(request):
            ksclient = get_admin_ksclient()
            ksclient.users.delete(obj_id)
        else:
            api.keystone.user_delete(request, obj_id)

class UserFilterAction(tables.FilterAction):
    def filter(self, table, users, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [user for user in users
                if q in user.name.lower()
                or q in (getattr(user, 'email', None) or '').lower()]

class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, user_id):
        if is_m1_user_admin(request):
            ksclient = get_admin_ksclient()
            user = ksclient.users.get(user_id)
            user_info = api.keystone.VERSIONS.upgrade_v2_user(user)
        else:
            user_info = api.keystone.user_get(request, user_id, admin=True)
        return user_info

class UpdateCell(tables.UpdateAction):
    def allowed(self, request, user, cell):
        return api.keystone.keystone_can_edit_user() and \
            policy.check((("identity", "identity:update_user"),),
                         request)

    def update_cell(self, request, datum, user_id,
                    cell_name, new_cell_value):
        try:
            user_obj = datum
            setattr(user_obj, cell_name, new_cell_value)
            kwargs = {}
            attr_to_keyword_map = {
                'name': 'name',
                'description': 'description',
                'email': 'email',
                'enabled': 'enabled',
                'project_id': 'project'
            }
            for key in attr_to_keyword_map:
                value = getattr(user_obj, key, None)
                keyword_name = attr_to_keyword_map[key]
                if value is not None:
                    kwargs[keyword_name] = value
                    
            if is_m1_user_admin(request):
                ksclient = get_admin_ksclient()
                if api.keystone.VERSIONS.active < 3:
                    project = kwargs.pop('project')
                    user = ksclient.users.update(user_obj, **kwargs)
                    ksclient.users.update_tenant(user, project)
                    user.tenantId = project
                    user_roles =  ksclient.roles.roles_for_user(user, project)
                    if not user_roles:
                        messages.warning(request, _('User %s has no role defined for '
                                                    'that project.')
                                                   % kwargs.get('name', None))
                else:
                    ksclient.users.update(user_obj, **kwargs)
            else:        
                api.keystone.user_update(request, user_obj, **kwargs)

        except horizon_exceptions.Conflict:
            message = _("This name is already taken.")
            messages.warning(request, message)
            raise django_exceptions.ValidationError(message)
        except Exception:
            horizon_exceptions.handle(request, ignore=True)
            return False
        return True

class UsersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("true", True),
        ("false", False)
    )
    name = tables.Column('name',
                         link="horizon:identity:xusers:detail",
                         verbose_name=_('User Name'),
                         form_field=forms.CharField(),
                         update_action=UpdateCell)
    description = tables.Column(lambda obj: getattr(obj, 'description', None),
                                verbose_name=_('Description'),
                                hidden=KEYSTONE_V2_ENABLED,
                                form_field=forms.CharField(
                                    widget=forms.Textarea(attrs={'rows': 4}),
                                    required=False),
                                update_action=UpdateCell)
    email = tables.Column(lambda obj: getattr(obj, 'email', None),
                          verbose_name=_('Email'),
                          form_field=forms.EmailField(required=False),
                          update_action=UpdateCell,
                          filters=(lambda v: defaultfilters
                                   .default_if_none(v, ""),
                                   defaultfilters.escape,
                                   defaultfilters.urlize)
                          )
    # Default tenant is not returned from Keystone currently.
    # default_tenant = tables.Column('default_tenant',
    #                               verbose_name=_('Default Project'))
    id = tables.Column('id', verbose_name=_('User ID'),
                       attrs={'data-type': 'uuid'})
    enabled = tables.Column('enabled', verbose_name=_('Enabled'),
                            status=True,
                            status_choices=STATUS_CHOICES,
                            filters=(defaultfilters.yesno,
                                     defaultfilters.capfirst),
                            empty_value="False")

    class Meta(object):
        name = "xusers"
        verbose_name = _("Users")
        row_actions = (EditUserLink, ChangePasswordLink, ToggleEnabled,
                       DeleteUsersAction, Disable2FAAction)
        table_actions = (UserFilterAction, CreateUserLink, DeleteUsersAction)
        row_class = UpdateRow

