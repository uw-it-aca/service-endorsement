import logging
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model,
    get_endorsee_email_model, is_shared_netid)
from endorsement.dao.endorse import (
    is_office365_permitted, is_google_permitted,
    get_endorsements_for_endorsee, get_endorsements_by_endorser)
from endorsement.dao.gws import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid, TooManyUWNetids, SharedUWNetid)


logger = logging.getLogger(__name__)


class Validate(RESTDispatch):
    """
    Validate provided endorsement list
    """
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorser = get_endorser_model(netid)

        netids = json.loads(request.read())
        validated = {
            'endorser': endorser.json_data(),
            'validated': []
        }

        endorsements = get_endorsements_by_endorser(endorser)
        max_netids = getattr(settings, "ENDORSER_LIMIT", 300)
        netid_count = max_netids - endorsements.count()

        for endorse_netid in netids:
            try:
                endorsee = get_endorsee_model(endorse_netid)
                if not endorsee.is_person:
                    if is_shared_netid(endorsee.netid):
                        raise SharedUWNetid(
                            '%s is a Shared NetID' % endorse_netid)
                    else:
                        raise InvalidNetID(
                            '%s not a personal NetID' % endorse_netid)

                netid_count -= 1
                if netid_count < 0:
                    raise TooManyUWNetids()

                endorsements = get_endorsements_for_endorsee(endorsee)
                active = False
                valid = {
                    'netid': endorse_netid,
                    'name': endorsee.display_name,
                    'email': get_endorsee_email_model(
                        endorsee, endorser).email
                }

                for e in endorsements:
                    if e.reason and len(e.reason):
                        valid['reason'] = e.reason
                        break

                try:
                    active, endorsed = is_office365_permitted(
                        endorser, endorsee)
                    valid['o365'] = {
                        'active': active,
                        'endorsers': [],
                        'self_endorsed': endorsed
                    }

                    for e in endorsements:
                        if (e.category_code ==
                                EndorsementRecord.OFFICE_365_ENDORSEE):
                            valid['o365']['endorsers'].append(e.endorser.netid)

                except Exception as ex:
                    valid['o365'] = {
                        'error': "%s" % ex
                    }

                try:
                    active, endorsed = is_google_permitted(
                        endorser, endorsee)
                    valid['google'] = {
                        'active': active,
                        'endorsers': [],
                        'self_endorsed': endorsed
                    }

                    for e in endorsements:
                        if (e.category_code ==
                                EndorsementRecord.GOOGLE_SUITE_ENDORSEE):
                            valid['google']['endorsers'].append(
                                e.endorser.netid)

                except Exception as ex:
                    valid['google'] = {
                        'error': "%s" % ex
                    }

            except UnrecognizedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Unrecognized NetID: %s' % (ex),
                }
            except SharedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Shared NetID: %s' % (ex),
                    'is_shared': True
                }
            except InvalidNetID as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '%s' % (ex),
                    'is_ineligible': True
                }
            except TooManyUWNetids:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Netid Count Exceeded',
                    'error_message': 'Limit of %s netids exceeded' % (
                        max_netids)
                }
            except Exception as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '%s' % (ex)
                }

            validated['validated'].append(valid)

        return self.json_response(validated)
