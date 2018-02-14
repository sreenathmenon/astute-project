from openstack_dashboard.local.local_settings import ADMIN_USERNAME, \
                                                     ADMIN_PASSWORD, \
                                                     ADMIN_TENANT, \
                                                     ADMIN_AUTH_URL, \
                                                     M1_USER_ADMIN_ROLES, \
                                                     OPENSTACK_API_VERSIONS

if OPENSTACK_API_VERSIONS['identity'] == 3:
    from keystoneclient.v3 import client as ksclient
else:
    from keystoneclient.v2_0 import client as ksclient

def get_admin_ksclient():
    keystone = ksclient.Client(
        username    = ADMIN_USERNAME,
        password    = ADMIN_PASSWORD,
        tenant_name = ADMIN_TENANT,
        auth_url    = ADMIN_AUTH_URL
    )    
    if OPENSTACK_API_VERSIONS['identity'] == 3:
        keystone.tenants = keystone.projects
    return keystone

def is_m1_user_admin(request):
    user   = request.user.id
    tenant = request.user.tenant_id
    if not tenant:
        tenant = request.user.project_id
    keystone = get_admin_ksclient()
    if OPENSTACK_API_VERSIONS['identity'] == 3:
        roles = keystone.roles.list(user=user, project=tenant)
    else:
        roles = keystone.roles.roles_for_user(user, tenant)
    for role in roles:
        if role.name in M1_USER_ADMIN_ROLES or role.id in M1_USER_ADMIN_ROLES:
            return True
    return False

