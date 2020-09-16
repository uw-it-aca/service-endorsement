from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    initiate_office365_endorsement, store_office365_endorsement,
    clear_office365_endorsement,
    initiate_google_endorsement, store_google_endorsement,
    clear_google_endorsement,
    initiate_canvas_endorsement, store_canvas_endorsement,
    clear_canvas_endorsement)


choices = dict(EndorsementRecord.CATEGORY_CODE_CHOICES)
ENDORSEMENT_SERVICES = {
    'o365': {
        'category_code': EndorsementRecord.OFFICE_365_ENDORSEE,
        'category_name': choices[EndorsementRecord.OFFICE_365_ENDORSEE],
        'initiate': initiate_office365_endorsement,
        'store': store_office365_endorsement,
        'clear': clear_office365_endorsement,
        'valid_shared': True
    },
    'google': {
        'category_code': EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
        'category_name': choices[EndorsementRecord.GOOGLE_SUITE_ENDORSEE],
        'initiate': initiate_google_endorsement,
        'store': store_google_endorsement,
        'clear': clear_google_endorsement,
        'valid_shared': True
    },
    'canvas': {
        'category_code': EndorsementRecord.CANVAS_PROVISIONEE,
        'category_name': choices[EndorsementRecord.CANVAS_PROVISIONEE],
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

