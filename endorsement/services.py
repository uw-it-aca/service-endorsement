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
        'valid_shared': True
    },
    'google': {
        'category_code': EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
        'category_name': choices[EndorsementRecord.GOOGLE_SUITE_ENDORSEE],
        'permitted': is_google_permitted,
        'initiate': initiate_google_endorsement,
        'store': store_google_endorsement,
        'clear': clear_google_endorsement,
        'valid_shared': True
    },
    'canvas': {
        'category_code': EndorsementRecord.CANVAS_PROVISIONEE,
        'category_name': choices[EndorsementRecord.CANVAS_PROVISIONEE],
        'permitted': is_canvas_permitted,
        'initiate': initiate_canvas_endorsement,
        'store': store_canvas_endorsement,
        'clear': clear_canvas_endorsement,
        'valid_shared': False
    }
}


def endorsement_service_keys(keys, shared=False):
    endorsement_services = {}
    for k, v in ENDORSEMENT_SERVICES.items():
        if shared and not v['valid_shared']:
            continue

        endorsement_services[k] = {}
        for key in keys:
            if key in v:

                endorsement_services[k][key] = v[key]

    return endorsement_services
