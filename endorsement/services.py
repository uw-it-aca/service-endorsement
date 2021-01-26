from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    is_office365_permitted, initiate_office365_endorsement,
    store_office365_endorsement, clear_office365_endorsement,
    is_google_permitted, initiate_google_endorsement,
    store_google_endorsement, clear_google_endorsement,
    is_canvas_permitted, initiate_canvas_endorsement,
    store_canvas_endorsement, clear_canvas_endorsement)


choices = dict(EndorsementRecord.CATEGORY_CODE_CHOICES)
ENDORSEMENT_SERVICES = {
    'o365': {
        'category_code': EndorsementRecord.OFFICE_365_ENDORSEE,
        'category_name': choices[EndorsementRecord.OFFICE_365_ENDORSEE],
        'permitted': is_office365_permitted,
        'initiate': initiate_office365_endorsement,
        'store': store_office365_endorsement,
        'clear': clear_office365_endorsement,
        'shared_supported_roles': ['owner', 'owner-admin'],
        'shared_supported_types': ['shared', 'administrator', 'support'],
        'shared_excluded_categories': [22],
        'service_link': ('https://itconnect.uw.edu/connect/'
                         'productivity-platforms/uw-office-365/')
    },
    'google': {
        'category_code': EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
        'category_name': choices[EndorsementRecord.GOOGLE_SUITE_ENDORSEE],
        'permitted': is_google_permitted,
        'initiate': initiate_google_endorsement,
        'store': store_google_endorsement,
        'clear': clear_google_endorsement,
        'shared_supported_roles': ['owner', 'owner-admin'],
        'shared_supported_types': ['shared', 'administrator', 'support'],
        'shared_excluded_categories': [22],
        'service_link': ('https://itconnect.uw.edu/connect/email/'
                         'google-apps/getting-started/#activate')
    },
    'canvas': {
        'category_code': EndorsementRecord.CANVAS_PROVISIONEE,
        'category_name': choices[EndorsementRecord.CANVAS_PROVISIONEE],
        'permitted': is_canvas_permitted,
        'initiate': initiate_canvas_endorsement,
        'store': store_canvas_endorsement,
        'clear': clear_canvas_endorsement,
        'shared_supported_roles': ['owner', 'owner-admin'],
        'shared_supported_types': ['administrator'],
        'shared_excluded_categories': None,
        'service_link': 'https://itconnect.uw.edu/learn/tools/canvas/'
    }
}


def endorsement_service_keys(keys, shared=False):
    endorsement_services = {}
    for k, v in ENDORSEMENT_SERVICES.items():
        if shared and not service_supports_shared(v):
            continue

        endorsement_services[k] = {}
        for key in keys:
            if key in v:
                endorsement_services[k][key] = v[key]

    return endorsement_services


def service_supports_shared(service):
    return (('shared_supported_roles' in service and
             service['shared_supported_roles'] is not None and
             len(service['shared_supported_roles']) > 0) or
            ('shared_supported_types' in service and
             service['shared_supported_types'] is not None and
             len(service['shared_supported_types']) > 0))


def service_names():
    names = service_name_list()
    return '{} and {}'.format(', '.join(names[:-1]), names[-1]) if (
        len(names) > 1) else names[0]


def service_name_list():
    return [s['category_name'] for t, s in ENDORSEMENT_SERVICES.items()]
