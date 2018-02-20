from openstack_dashboard.local.local_settings import ADMIN_USERNAME, \
                                                     ADMIN_PASSWORD, \
                                                     ADMIN_TENANT, \
                                                     ADMIN_AUTH_URL, \
                                                     API_RESULT_LIMIT, \
                                                     OPENSTACK_API_VERSIONS, \
                                                     M1_USER_ADMIN_ROLES, \
                                                     OPENSTACK_KEYSTONE_DEFAULT_ROLE
                                                     
from openstack_dashboard.api import keystone
from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova
from openstack_dashboard.api import cinder
from openstack_dashboard.api import base

from horizon.utils import functions as utils
from django.conf import settings
import collections

if OPENSTACK_API_VERSIONS['identity'] >= 3:
    from keystoneclient.v3 import client as ksclient
else:
    from keystoneclient.v2_0 import client as ksclient
    
from cinderclient import client as cclient
from neutronclient.v2_0 import client
from novaclient import client as nova_client
from openstack_dashboard.api import base

def get_admin_ksclient():
    keystone = ksclient.Client(
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        tenant_name=ADMIN_TENANT,
        auth_url=ADMIN_AUTH_URL
    )
    if OPENSTACK_API_VERSIONS['identity'] >= 3:
        keystone.tenants = keystone.projects

    return keystone

def get_cinder_client():
    cinder = cclient.Client('2', ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_TENANT, ADMIN_AUTH_URL)
    return cinder

def get_neutron_client():
    neutron = client.Client(username = ADMIN_USERNAME,
                            password = ADMIN_PASSWORD,
                            tenant_name = ADMIN_TENANT,
                            auth_url = ADMIN_AUTH_URL)
    return neutron

def get_nova_client():
    nova = nova_client.Client(2, 
                              ADMIN_USERNAME, 
                              ADMIN_PASSWORD, 
                              ADMIN_TENANT, 
                              ADMIN_AUTH_URL)
    return nova

def is_m1_user_admin(request):
    user   = request.user.id
    tenant = request.user.tenant_id
    if not tenant:
        tenant = request.user.project_id
    keystone = get_admin_ksclient()
    if OPENSTACK_API_VERSIONS['identity'] >= 3:
        roles = keystone.roles.list(user=user, project=tenant)
    else:
        roles = keystone.roles.roles_for_user(user, tenant)
    for role in roles:
        if role.name in M1_USER_ADMIN_ROLES or role.id in M1_USER_ADMIN_ROLES:
            return True
    return False

def get_tenants(request, paginate=False, marker=None, domain=None, 
                user=None, admin=True, filters=None):
    
    ksclient = get_admin_ksclient()
    page_size = utils.get_page_size(request)
    limit     = None

    if paginate:
        limit = page_size + 1

    has_more = False

    # if requesting the projects for the current user,
    # return the list from the cache
    if user == request.user.id:
        projects = request.user.authorized_tenants
    elif keystone.VERSIONS.active < 3:
        projects = ksclient.tenants.list(limit, marker)
        if paginate and len(projects) > page_size:
            projects.pop(-1)
            has_more = True
    else:
        kwargs = {
            "domain": domain,
            "user": user
        }
        if filters is not None:
            kwargs.update(filters)
        projects = ksclient.projects.list(**kwargs)
    return (projects, has_more)

def get_project(request, id):
    ks = get_admin_ksclient()
    return ks.tenants.get(id)

def get_domain(request, domain_id):
    ksclient = get_admin_ksclient()
    domain = ksclient.domains.get(domain_id)

def delete_tenant(request, tenant_id):
    ksclient = get_admin_ksclient()
    return ksclient.tenants.delete(tenant_id)

def update_tenant(request, project, name=None, description=None,
                  enabled=None, domain=None, **kwargs):
    
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.tenants.update(project, name, description, enabled,
                                  **kwargs)
    else:
        return ksclient.projects.update(project, name=name, description=description,
                              enabled=enabled, domain=domain, **kwargs)

    
def gt_default_role(request):
    default = None
    default_role = None
    ksclient = get_admin_ksclient()
    default = getattr(settings, "OPENSTACK_KEYSTONE_DEFAULT_ROLE", None)
    roles = ksclient.roles.list()

    for role in roles:
        if role.id == default or role.name == default:
            default_role = role
            break
    return default_role

def list_users(request, project=None, domain=None, group=None, filters=None):
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        kwargs = {"tenant_id": project}
    else:
        kwargs = {
            "project": project,
            "domain": domain,
            "group": group
        }
        if filters is not None:
            kwargs.update(filters)
    users = ksclient.users.list(**kwargs)
    return [keystone.VERSIONS.upgrade_v2_user(user) for user in users]

def roles_for_user(request, user, project=None, domain=None):
    """Returns a list of user roles scoped to a project or domain."""
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.roles.roles_for_user(user, project)
    else:
        return ksclient.roles.list(user=user, domain=domain, project=project)

def list_roles(request):
    ksclient = get_admin_ksclient()
    roles = ksclient.roles.list()
    return roles

def gt_pjct_groups_roles(request, project):
    groups_roles = collections.defaultdict(list)
    project_role_assignments = role_assignments_list(request,
                                                     project=project)
    for role_assignment in project_role_assignments:
        if not hasattr(role_assignment, 'group'):
            continue
        group_id = role_assignment.group['id']
        role_id = role_assignment.role['id']
        groups_roles[group_id].append(role_id)
    return groups_roles

def role_assignments_list(request, project=None, user=None, role=None,
                          group=None, domain=None, effective=False):
    ksclient = get_admin_ksclient()
    return ksclient.role_assignments.list(project=project, user=user, role=role, group=group,
                        domain=domain, effective=effective)

def gt_pjct_users_roles(request, project):
    users_roles = collections.defaultdict(list)
    if keystone.VERSIONS.active < 3:
        project_users = list_users(request, project=project)

        for user in project_users:
            roles = roles_for_user(request, user.id, project)
            roles_ids = [role.id for role in roles]
            users_roles[user.id].extend(roles_ids)
    else:
        project_role_assignments = role_assignments_list(request,
                                                         project=project)
        for role_assignment in project_role_assignments:
            if not hasattr(role_assignment, 'user'):
                continue
            user_id = role_assignment.user['id']
            role_id = role_assignment.role['id']
            users_roles[user_id].append(role_id)
    return users_roles

def create_tenant(request, name, description=None, enabled=None,
                  domain=None, **kwargs):
    
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.tenants.create(name, description, enabled, **kwargs)
    else:
        return ksclient.projects.create(name, domain,
                                  description=description,
                                  enabled=enabled, **kwargs)

def grant_tenant_user_role(request, project=None, user=None, role=None, 
                           group=None, domain=None):
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.roles.add_user_role(user, role, project)
    else:
        return ksclient.roles.grant(role, user=user, project=project,
                             group=group, domain=domain)

def add_gp_role(request, role, group, domain=None, project=None):
    """Adds a role for a group on a domain or project."""
    ksclient = get_admin_ksclient()
    return ksclient.roles.grant(role=role, group=group, domain=domain,
                         project=project)

def update_tenant(request, project, name=None, description=None,
                  enabled=None, domain=None, **kwargs):
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.tenants.update(project, name, description, enabled,
                                  **kwargs)
    else:
        return kclient.projects.update(project, name=name, description=description,
                                  enabled=enabled, domain=domain, **kwargs)

def list_groups(request, domain=None, project=None, user=None):
    ksclient = get_admin_ksclient()
    groups = ksclient.groups.list(user=user, domain=domain)

    if project:
        project_groups = []
        for group in groups:
            roles = roles_for_group(request, group=group.id, project=project)
            if roles and len(roles) > 0:
                project_groups.append(group)
        groups = project_groups

    return groups

def roles_for_gp(request, group, domain=None, project=None):
    ksclient = get_admin_ksclient()
    return ksclient.roles.list(group=group, domain=domain, project=project)

def add_gp_role(request, role, group, domain=None, project=None):
    """Adds a role for a group on a domain or project."""
    ksclient = get_admin_ksclient()
    return ksclient.roles.grant(role=role, group=group, domain=domain,
                         project=project)

def remove_group_role(request, role, group, domain=None, project=None):
    """Removes a given single role for a group from a domain or project."""
    ksclient = get_admin_ksclient()
    return ksclient.roles.revoke(role=role, group=group, project=project,
                          domain=domain)

def add_user_role_to_tenant(request, project=None, user=None, role=None,
                         group=None, domain=None):
    """Adds a role for a user on a tenant."""
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.roles.add_user_role(user, role, project)
    else:
        return ksclient.roles.grant(role, user=user, project=project,
                             group=group, domain=domain)

def remove_user_role_frm_tenant(request, project=None, user=None, role=None,
                            group=None, domain=None):
    """Removes a given single role for a user from a tenant."""
    ksclient = get_admin_ksclient()
    if keystone.VERSIONS.active < 3:
        return ksclient.roles.remove_user_role(user, role, project)
    else:
        return ksclient.roles.revoke(role, user=user, project=project,
                              group=group, domain=domain)

###neutron
def get_tenant_quota_neutron(request, tenant_id):
    nclient = get_neutron_client()
    return base.QuotaSet(nclient.show_quota(tenant_id)['quota'])

def tenant_quota_update_neutron(request, tenant_id, **kwargs):
    nclient = get_neutron_client()
    quotas = {'quota': kwargs}
    return nclient.update_quota(tenant_id, quotas)

def network_list_neutron(request, **params):
    nclient = get_neutron_client()
    networks = nclient.list_networks(**params).get('networks')
    
    # Get subnet list to expand subnet info in network list.
    subnets = subnet_list_neutron(request)
    subnet_dict = dict([(s['id'], s) for s in subnets])
    # Expand subnet list from subnet_id to values.
    for n in networks:
        # Due to potential timing issues, we can't assume the subnet_dict data
        # is in sync with the network data.
        n['subnets'] = [subnet_dict[s] for s in n.get('subnets', []) if
                        s in subnet_dict]
    return [neutron.Network(n) for n in networks]

def subnet_list_neutron(request, **params):
    nclient = get_neutron_client()
    subnets = nclient.list_subnets(**params).get('subnets')
    return [neutron.Subnet(s) for s in subnets]

def router_list_neutron(request, **params):
    nclient = get_neutron_client()
    routers = nclient.list_routers(**params).get('routers')
    return [neutron.Router(r) for r in routers]


##nova
def tenant_quota_update_nova(request, tenant_id, **kwargs):
    nvclient = get_nova_client()
    nvclient.quotas.update(tenant_id, **kwargs)

def tenant_quota_get_nova(request, tenant_id):
    return base.QuotaSet(get_nova_client().quotas.get(tenant_id))

def server_list_nova(request, search_opts=None, all_tenants=False):
    page_size = utils.get_page_size(request)
    c = get_nova_client()
    paginate = False
    if search_opts is None:
        search_opts = {}
    elif 'paginate' in search_opts:
        paginate = search_opts.pop('paginate')
        if paginate:
            search_opts['limit'] = page_size + 1

    if all_tenants:
        search_opts['all_tenants'] = True
    else:
        search_opts['project_id'] = request.user.tenant_id
    servers = [nova.Server(s, request)
               for s in c.servers.list(True, search_opts)]

    has_more_data = False
    if paginate and len(servers) > page_size:
        servers.pop(-1)
        has_more_data = True
    elif paginate and len(servers) == getattr(settings, 'API_RESULT_LIMIT',
                                              1000):
        has_more_data = True
    return (servers, has_more_data)

def flavor_list_nova(request, is_public=True, get_extras=False):
    """Get the list of available instance sizes (flavors)."""
    flavors = get_nova_client().flavors.list(is_public=is_public)
    if get_extras:
        for flavor in flavors:
            flavor.extras = flavor_get_extras(request, flavor.id, True, flavor)
    return flavors

def flavor_get_nova(request, flavor_id, get_extras=False):
    flavor = get_nova_client().flavors.get(flavor_id)
    if get_extras:
        flavor.extras = flavor_get_extras(request, flavor.id, True, flavor)
    return flavor

def tenant_absolute_limits_nova(request, reserved=False):
    limits = get_nova_client().limits.get(reserved=reserved).absolute
    limits_dict = {}
    for limit in limits:
        if limit.value < 0:
            # Workaround for nova bug 1370867 that absolute_limits
            # returns negative value for total.*Used instead of 0.
            # For such case, replace negative values with 0.
            if limit.name.startswith('total') and limit.name.endswith('Used'):
                limits_dict[limit.name] = 0
            else:
                # -1 is used to represent unlimited quotas
                limits_dict[limit.name] = float("inf")
        else:
            limits_dict[limit.name] = limit.value
    return limits_dict

##Cinder
def tenant_quota_update_cinder(request, tenant_id, **kwargs):
    cclient = get_cinder_client()
    return cclient.quotas.update(tenant_id, **kwargs)

def tenant_quota_get_cinder(request, tenant_id):
    c_client = get_cinder_client()
    if c_client is None:
        return base.QuotaSet()
    return base.QuotaSet(c_client.quotas.get(tenant_id))

def get_volume_snapshot_list(request, search_opts=None):
    c_client = get_cinder_client()
    if c_client is None:
        return []
    return [cinder.VolumeSnapshot(s) for s in c_client.volume_snapshots.list(
        search_opts=search_opts)]

def get_volume_list(request, search_opts=None):
    """To see all volumes in the cloud as an admin you can pass in a special
    search option: {'all_tenants': 1}
    """

    c_client = get_cinder_client()
    if c_client is None:
        return []

    # build a dictionary of volume_id -> transfer
    transfers = {t.volume_id: t
                 for t in transfer_list_cinder(request, search_opts=search_opts)}

    volumes = []
    for v in c_client.volumes.list(search_opts=search_opts):
        v.transfer = transfers.get(v.id)
        volumes.append(Volume(v))

    return volumes

def transfer_list_cinder(request, detailed=True, search_opts=None):
    """To see all volumes transfers as an admin pass in a special
    search option: {'all_tenants': 1}
    """
    c_client = get_cinder_client()
    return [cinder.VolumeTransfer(v) for v in c_client.transfers.list(
        detailed=detailed, search_opts=search_opts)]


def tenant_absolute_limits_cinder(request):
    c_client = get_cinder_client()
    limits = c_client.limits.get().absolute
    limits_dict = {}
    for limit in limits:
        if limit.value < 0:
            # In some cases, the absolute limits data in Cinder can get
            # out of sync causing the total.*Used limits to return
            # negative values instead of 0. For such cases, replace
            # negative values with 0.
            if limit.name.startswith('total') and limit.name.endswith('Used'):
                limits_dict[limit.name] = 0
            else:
                # -1 is used to represent unlimited quotas
                limits_dict[limit.name] = float("inf")
        else:
            limits_dict[limit.name] = limit.value
    return limits_dict


