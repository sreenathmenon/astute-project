#
# Copyright 2017 NephoScale
#

#from keystoneauth1.identity import v2
#from keystoneauth1 import session
#from keystoneclient.v2_0.client import Client as KeystoneClient

#from novaclient.client import Client as NovaClient

from django.conf import settings

from horizon.exceptions import HorizonException

from openstack_dashboard import api
from openstack_dashboard.api import base
from openstack_dashboard.api import cinder
from openstack_dashboard.api import keystone
from openstack_dashboard.api import nova
from openstack_dashboard.usage import quotas


from openstack_dashboard.local.local_settings import \
    ADMIN_AUTH_URL, \
    ADMIN_USERNAME, \
    ADMIN_PASSWORD, \
    ADMIN_TENANT

import requests as http


# Astute service base URL
ASTUTE_BASE_URL = getattr(settings, 'ASTUTE_BASE_URL', 'http://os-controller1:9080/v1/')

# Astute service request
def astute(request, endpoint, method='GET', data=None):
    auth_token = request.META.get('X_AUTH_TOKEN') or request.session['token'].id
    response = getattr(http, method.lower())(
                   ASTUTE_BASE_URL + endpoint,
                   headers={'X-Auth-Token': auth_token},
                   json=data
               )
    if getattr(settings, 'DEBUG'):
        print "###", "ASTUTE RESPONSE ### " * 5
        print response, response.text

    return response.json()

#
# Common OpenStack API helpers
#

# @returns list projects
def get_projects(request):
    #auth = v2.Password(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, \
    #    tenant_name=ADMIN_TENANT, auth_url=ADMIN_AUTH_URL)
    #sess = session.Session(auth=auth)
    #keystone = KeystoneClient(session=sess)

    #Role based check has to be added
    #Passing the admin paramter temporarily to fix issue while loading as users with provisioning, finance, support or catalogue roles
    return keystone.tenant_list(request)[0]

# @returns project
def get_project(request, id):
    #auth = v2.Password(username=ADMIN_USERNAME, password=ADMIN_PASSWORD, \
    #    tenant_name=ADMIN_TENANT, auth_url=ADMIN_AUTH_URL)
    #Ssess = session.Session(auth=auth)
    #keystone = KeystoneClient(session=sess)
    return keystone.tenant_get(request, id)

# @returns list of defined flavors
def get_flavors(request):
    #nova = NovaClient('2', ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_TENANT, ADMIN_AUTH_URL)
    return nova.flavor_list(request)


#
# Billing Types helper routines
#

# returns billing types list
def get_billing_types(request):
    return astute(request, 'billing/type/')

# returns billing type data
def get_billing_type(request, id):
    return astute(request, 'billing/type/' + str(id))

# create billing type
def create_billing_type(request, data):
    return astute(request, 'billing/type/', 'POST', data)

# modify billing type
def modify_billing_type(request, id, data):
    return astute(request, 'billing/type/' + str(id), 'PUT', data)

# delete billing type
def delete_billing_type(request, id):
    return astute(request, 'billing/type/' + str(id), 'DELETE')

#
# Service Tyles helper routines
#

# returns service types list
def get_service_types(request):
    return astute(request, 'service_type/')

# returns service type data
def get_service_type(request, id):
    return astute(request, 'service_type/' + str(id))

# create service type
def create_service_type(request, data):
    return astute(request, 'service_type/', 'POST', data)

# modify service type
def modify_service_type(request, id, data):
    return astute(request, 'service_type/' + str(id), 'PUT', data)

# delete service type
def delete_service_type(request, id):
    return astute(request, 'service_type/' + str(id), 'DELETE')

#
# Discount helper routines
#

# returns discount types list
def get_discount_types(request):
    return astute(request, 'discount/type/')

# returns discount type data
def get_discount_type(request, id):
    return astute(request, 'discount/type/' + str(id))

#
# Discounts helper routines
#

# @returns discounts list
def get_discounts(request):
    data = astute(request, 'discount/')
    # adjust data
    for item in data:
        item['create_time'] = item.get('create_time') and item['create_time'].split(' ')[0]
        item['expiration_date'] = item.get('expiration_date') and item['expiration_date'].split(' ')[0]
    return data

# @returns discount data
def get_discount(request, id):
    data = astute(request, 'discount/' + str(id))
    # adjust data
    data['create_time'] = data.get('create_time') and data['create_time'].split(' ')[0]
    data['expiration_date'] = data.get('expiration_date') and data['expiration_date'].split(' ')[0]
    return data

# create discount
def create_discount(request, data):
    return astute(request, 'discount/', 'POST', data)

# modify discount
def modify_discount(request, id, data):
    return astute(request, 'discount/' + str(id), 'PUT', data)

# delete discount
def delete_discount(request, id):
    return astute(request, 'discount/' + str(id), 'DELETE')


#
# Plans helper routines
#

# @returns plans list
def get_plans(request, verbose = False):
    plans = astute(request, 'plan/')
    if verbose:
        billing_types = dict([(bt['id'], bt) for bt in get_billing_types(request)])
        billing_types[0] = {'name': None}
        flavors = dict([(fl.id, fl.name) for fl in get_flavors(request)])
        service_types = dict([(st['id'], st) for st in get_service_types(request)])
        for plan in plans:
            billing_type_id = plan.get('billing_type') or 0
            plan['billing_type'] = billing_types[billing_type_id]['name']
            flavor_id = plan.get('ref_id', None)
            if flavor_id and str(flavor_id) != '0':
                plan['ref_id'] = flavors.get(flavor_id, None) or '!ERR: %s' % plan['ref_id']
            else:
                plan['ref_id'] = None
            plan['service_type'] = service_types[plan['service_type']]['name']
    return plans

# @returns plan data
def get_plan(request, id, verbose = False):
    plan = astute(request, 'plan/' + str(id))
    if verbose:
        billing_types = dict([(bt['id'], bt) for bt in get_billing_types(request)])
        billing_types[0] = {'name': None}
        flavors = dict([(fl.id, fl.name) for fl in get_flavors(request)])
        service_types = dict([(st['id'], st) for st in get_service_types(request)])
        plan['billing_type'] = billing_types[plan.get('billing_type') or 0]['name']
        flavor_id = plan.get('ref_id', None)
        if flavor_id:
            plan['ref_id'] = flavors.get(flavor_id, None) or '#UNKNOWN: %s' % plan['ref_id']
        plan['service_type'] = service_types[plan['service_type']]['name']
    return plan

# create plan
def create_plan(request, data):
    return astute(request, 'plan/', 'POST', data)

# modify plan
def modify_plan(request, id, data):
    return astute(request, 'plan/' + str(id), 'PUT', data)

# delete plan
def delete_plan(request, id):
    return astute(request, 'plan/' + str(id), 'DELETE')


#
# Billing Type Mapping routines
#

def get_billing_type_mappings(request, verbose=False):
    data = astute(request, 'billing/mapping/')
    if verbose:
        projects = dict([(p.id, p.name) for p in get_projects(request)])
        billing_types = dict([(bt['id'], bt) for bt in get_billing_types(request)])
        billing_types[0] = {'name': None}
        for item in data:
            item['user_id'] = item['user']
            item['user'] = projects.get(item['user']) or '!ERR: ' + item['user']
            item['billing_type_code'] = billing_types[item['billing_type']]['code']
            item['billing_type'] = billing_types[item['billing_type']]['name']
        # add discounts
        for item in data:
            item['discount_mapping'] = get_type_mapping_discount_mapping(request, item['user_id'], verbose)
    return data

def get_billing_type_mapping(request, id, verbose=False):
    data = astute(request, 'billing/mapping/' + str(id))
    data['project'] = keystone.tenant_get(request, data['user'])
    data['discount_mapping'] = get_type_mapping_discount_mapping(request, id, verbose)
    return data

# create billing type mapping
def create_billing_type_mapping(request, data):
    return astute(request, 'billing/mapping/', 'POST', data)

# modify billing type mapping
def modify_billing_type_mapping(request, id, data):
    return astute(request, 'billing/mapping/' + str(id), 'PUT', data)

# delete billing type mapping
def delete_billing_type_mapping(request, id):
    return astute(request, 'billing/mapping/' + str(id), 'DELETE')

# get project type mapping (none if not mapped)
# @param id {str} - openstack project ID
def get_project_type_mapping(request, id):
    # get billing types
    bill_types = dict([(bt['id'], bt) for bt in get_billing_types(request)])
    for type_map in get_billing_type_mappings(request):
        if type_map['user'] == str(id):
            type_map['billing_type'] = bill_types[type_map['billing_type']]
            return type_map
    return None


#
# Billing Plan Mapping routines
#

def get_billing_plan_mappings(request, project_id=None, verbose=False):
    data = astute(request, 'plan/mapping/' + ('user?id=' + str(project_id) if project_id else ''))
    if verbose:
        projects = dict([(p.id, p.name) for p in get_projects(request)])
        plans = {}
        srv_types = {}
        for plan in get_plans(request):
            plans[plan['id']] = plan['name']
            srv_types[plan['id']] = plan['service_type']
        for item in data:
            item['user'] = projects.get(item['user'], None) or '!ERR: %s' % item['user']
            item['plan'] = plans.get(item['plan_id'], None) or '!ERR: %s' % item['plan_id']
            item['service_type'] = srv_types.get(item['plan_id'], None) or '!ERR: %s' % item['plan_id']
            item['created_on'] = item.get('created_on').split(' ')[0]
    return data

def get_billing_plan_mapping(request, id, verbose=False):
    return astute(request, 'plan/mapping/' + str(id))

# create billing plan mapping
def create_billing_plan_mapping(request, data):
    return astute(request, 'plan/mapping', 'POST', data)

# modify billing plan mapping
def modify_billing_plan_mapping(request, id, data):
    return astute(request, 'plan/mapping/' + str(id), 'PUT', data)

# delete billing plan mapping
def delete_billing_plan_mapping(request, id):
    return astute(request, 'plan/mapping/' + str(id), 'DELETE')


#
# Invoices helper routines
#

def get_invoices(request, account=None, period_from=None, period_to=None, verbose=False):

    url = 'invoice' + ('?' if account or period_from or period_to else '')

    params = []

    if account:
        params.append('user=' + str(account))
    if period_from:
        params.append('inv_from=' + str(period_from))
    if period_to:
        params.append('inv_to=' + str(period_to))
    if len(params) > 0:
        url += "&".join(params)

    data = astute(request, url)
    if verbose:
        projects = dict([(p.id, p) for p in get_projects(request)])
        accounts = dict([(a['user'], a) for a in get_billing_type_mappings(request)])

        for item in data:
            project = projects.get(item['user'], None)
            account = accounts.get(item['user'], None)
            item['user'] = project and project.name or '!ERR'
            item['service_id'] = account and account['extra_fields'] and account['extra_fields']['service_id'] or '!ERR: %s' % item['user']
            #item['inv_date'] = item['inv_date'].split(' ')[0]
            #item['inv_from'] = item['inv_from'].split(' ')[0]
            #item['inv_to'] = item['inv_to'].split(' ')[0]
            item['last_updated'] = item['last_updated'].split(' ')[0]
    return data

def get_invoice(request, id, verbose=False):
    data = astute(request, 'invoice/' + str(id))
    if verbose:
        projects = dict([(p.id, p.name) for p in get_projects(request)])
        plans = dict([(p['id'], p['name']) for p in get_plans(request)])
        data['user'] = projects.get(data['user'], None) or '!ERR: %s' % data['user']
        data['inv_date'] = data['inv_date'].split(' ')[0]
        data['inv_from'] = data['inv_from'].split(' ')[0]
        data['inv_to'] = data['inv_to'].split(' ')[0]
        data['last_updated'] = data['last_updated'].split(' ')[0]
        for item in data['items']:
            item['plan'] = plans.get(item['plan_id'], None) or '!ERR: %s' % item['plan_id']
    return data

def modify_invoice(request, id, data):
    return astute(request, 'invoice/' + str(id), 'PUT', data)

#
# Discount mappings helper routines
#

def get_discount_mappings(request):
    return astute(request, 'discount/mapping/')

def get_discount_mapping(request, id):
    return astute(request, 'discount/mapping/' + str(id))

# create discount mapping
def create_discount_mapping(request, data):
    return astute(request, 'discount/mapping/', 'POST', data)

# modify discount mapping
def modify_discount_mapping(request, id, data):
    return astute(request, 'discount/mapping/' + str(id), 'PUT', data)

# delete discount mapping
def delete_discount_mapping(request, id):
    return astute(request, 'discount/mapping/' + str(id), 'DELETE')

# discount serch helpers
def get_user_discount(request, user_id):
    return astute(request, 'discount/mapping/?map_object=user&user=' + str(user_id))[0]

# discount serch helpers
# FIXME(div): requires API side implementation (see get_user_discount)
def get_plan_discount(request, plan_id):
    discount = None
    for disc in get_discounts(request):
        if disc['map_object'] == 'user_plan' and disc['ref_id'] == plan_id:
            discount = disc
            break
    return discount


def get_type_mapping_discount_mapping(request, ref_id, verbose=False):
    ref_id = str(ref_id)
    for disc_map in get_discount_mappings(request):
        if disc_map['map_object'] == 'user' and str(disc_map['ref_id']) == ref_id :
            if verbose:
                disc_map['discount'] = get_discount(request, disc_map['discount_id'])
            return disc_map
    return None

def get_plan_mapping_discount_mapping(request, plan_map_id, verbose=False):
    disc_maps = get_discount_mappings(request)
    plan_map_id = str(plan_map_id)
    for disc_map in get_discount_mappings(request):
        if disc_map['map_object'] == 'user_plan' and str(disc_map['ref_id']) == plan_map_id:
            if verbose:
                disc_map['discount'] = get_discount(request, disc_map['discount_id'])
            return disc_map
    return None


def get_project_plan_mappings(request, project_id, unassociated=False):
    return astute(request, 'plan/mapping/' + \
                           ('unassociated_plans' if unassociated else 'user') + \
                           '?id=' + str(project_id))

def associate_plan_mapping_with_instance(request, plan_id, instance_id):
    data = {
        'user_plan_id': int(plan_id),
        'ref_id': str(instance_id)
    }
    return astute(request, 'plan/mapping/associate', 'POST', data)

def disassociate_plan_mapping_with_instance(request, plan_id):
    data = {
        'user_plan_id': int(plan_id)
    }
    return astute(request, 'plan/mapping/dissociate', 'POST', data)


# TODO (div): fill following 'constants' from DB values
PAYG_BILLING_TYPE_ID = 1
RAB_BILLING_TYPE_ID  = 2

# TODO (div): fill following 'constants' from DB values
PERCENTS_DISCOUNT_TYPE_ID = 1
OVERRIDE_DISCOUNT_TYPE_ID = 2


def get_project_volume_type_quotas(request, project_id):
    result = {}
    client = cinder.cinderclient(request)
    quotas = client.quotas.get(project_id)
    for volume_type in client.volume_types.list():
        result[volume_type.name] = getattr(quotas, 'gigabytes_' + volume_type.name, -1)
    return result

def modify_project_volume_type_quotas(request, project_id, quotas):
    client = cinder.cinderclient(request)
    return client.quotas.update(project_id, **quotas)

#Features corresponding to Customer Interface
def get_user_sub_plans(request, verbose=False):
    """Get all the plans subscribed by the user"""

    user_id = request.user.tenant_id
    data = astute(request, 'plan/mapping/user?id=' + str(user_id))
    for item in data:
                plan_id = item['plan_id']
                plan_details = get_plan(request, plan_id)
                plan_name = plan_details.get('name')
                service_name = plan_details.get('service_name')
                description = plan_details.get('description')
                item['name'] = plan_name
                item['service_name'] = service_name
                item['description'] = description
    return data

def get_avbl_user_plans(request, verbose=False):
    """Get all the plans under the current billing type"""

    user_id = request.user.tenant_id
    plan_list = get_plans(request)
    #user_sub_plan_list = get_user_sub_plans(req)
    user_billing_details = get_user_billing_type(request)

    if user_billing_details:
        #Billing type code should already be present for a user
        billing_type_code = user_billing_details[0]['type_code']

        #Display only additional services for rab billing type
        if billing_type_code == 'rab':
            #print "Entering rab section"
            rab_billing_typeId = user_billing_details[0]['billing_type']
            data = filter(lambda x: (x['billing_type'] == None and x['service_name'] != 'SetupFee'), plan_list)

        if billing_type_code == 'payg':
            #print "Entering payg section"
            payg_billing_typeId = user_billing_details[0]['billing_type']
            data = filter(lambda x: ((x['billing_type'] == payg_billing_typeId or x['billing_type'] == None) and (x['service_name'] != 'SetupFee')), plan_list)

        for item in data:
            if billing_type_code == 'payg':
                item['billing_type']  = 'Usage Based Billing'
            elif billing_type_code =='rab':
                item['billing_type']  = 'Resource Allocation Based Billing'
            else:
                item['billing_type']  = 'NA'
    else:
        data = []
    """
    for item in data:
        billing_type_id = item['billing_type']
    """
    # filteredList = filter(lambda x: (x['billing_type'] == 1 and x['name'] not in keyVal2List), plan_list)
    return data

def get_user_invoices(request, verbose=True):
    """Get all the invoices correspodning to the user"""

    user_id = request.user.tenant_id
    data = astute(request, 'invoice?user=' + str(user_id))

    #Rounding to 2 decimal points
    for item in data:
        item['total_amt']   = format(round(item['total_amt'], 2), '.2f')
        item['balance_amt'] = format(round(item['balance_amt'], 2), '.2f')
        item['amt_paid']    = format(round(item['amt_paid'], 2), '.2f')
    return data

def get_user_billing_type(request, verbose=False):
    """Get the billing type details corresponding to the user"""

    user_id = request.user.tenant_id
    data = astute(request, 'billing/mapping/user?id=' + str(user_id))
    return data

