import logging
from django.conf import settings
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model,
    get_endorsee_email_model, is_shared_netid)
from endorsement.dao.endorse import (
    is_office365_permitted, is_google_permitted, is_canvas_permitted,
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
    def post(self, request, *args, **kwargs):
        timer = Timer()

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorser = get_endorser_model(netid)
        netids = request.data.get('netids', [])
        validated = {
            'endorser': endorser.json_data(),
            'validated': []
        }

        endorsements = get_endorsements_by_endorser(endorser)
        max_netids = getattr(settings, "ENDORSER_LIMIT", 300)
        netid_count = max_netids - endorsements.filter(
            endorsee__is_person=True).count()

        for endorse_netid in netids:
            try:
                endorsee = get_endorsee_model(endorse_netid)
                if not endorsee.is_person:
                    if is_shared_netid(endorsee.netid):
                        raise SharedUWNetid(
                            '{0} is a Shared NetID'.format(endorse_netid))
                    else:
                        raise InvalidNetID(
                            '{0} not a personal NetID'.format(endorse_netid))

                netid_count -= 1
                if netid_count < 0:
                    raise TooManyUWNetids()

                endorsements = get_endorsements_for_endorsee(endorsee)
                valid = {
                    'netid': endorse_netid,
                    'name': endorsee.display_name,
                    'email': get_endorsee_email_model(
                        endorsee, endorser).email,
                    'endorsements': {}
                }

                for e in endorsements:
                    if e.reason and len(e.reason):
                        valid['reason'] = e.reason
                        break

                valid['endorsements']['o365'] = self._endorsement(
                    endorser, endorsee, endorsements,
                    EndorsementRecord.OFFICE_365_ENDORSEE)

                valid['endorsements']['google'] = self._endorsement(
                    endorser, endorsee, endorsements,
                    EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

                valid['endorsements']['canvas'] = self._endorsement(
                    endorser, endorsee, endorsements,
                    EndorsementRecord.CANVAS_PROVISIONEE)

            except UnrecognizedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Unrecognized NetID: {0}'.format(ex),
                }
            except SharedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Shared NetID: {0}'.format(ex),
                    'is_shared': True
                }
            except InvalidNetID as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '{0}'.format(ex),
                    'is_ineligible': True
                }
            except TooManyUWNetids:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Provision Count Exceeded',
                    'error_message':
                        'Limit of {0} provisioned netids exceeded'.format(
                            max_netids)
                }
            except Exception as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '{0}'.format(ex)
                }

            validated['validated'].append(valid)

        return self.json_response(validated)

    def _endorsement(self, endorser, endorsee,
                     endorsements, endorsement_category):
        try:
            active, endorsed = is_canvas_permitted(endorser, endorsee)
            endorsement = {
                'category_name': dict(
                    EndorsementRecord.CATEGORY_CODE_CHOICES)[
                        endorsement_category],
                'active': active,
                'endorsers': [],
                'self_endorsed': endorsed
            }

            for e in endorsements:
                if (e.category_code == endorsement_category):
                    endorsements['endorsers'].append(e.endorser.json_data())

        except Exception as ex:
            endorsement = {
                'error': "{0}".format(ex)
            }

        return endorsement
