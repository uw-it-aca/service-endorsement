# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.models import EndorsementRecord
from endorsement.test.api import EndorsementApiTest
from endorsement.exceptions import NoEndorsementException
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import get_endorsement_service


class TestEndorsementAcceptAPI(EndorsementApiTest):
    def test_acceptance(self):
        endorser = get_endorser_model('jfaculty')
        endorsee = get_endorsee_model('endorsee7')
        try:
            get_endorsement_service('o365').clear_endorsement(
                endorser, endorsee)
        except NoEndorsementException as ex:
            pass

        get_endorsement_service('o365').initiate_endorsement(
            endorser, endorsee, 'endorsee6')

        endorsement = EndorsementRecord.objects.get(endorser=endorser,
                                                    endorsee=endorsee)

        self.set_user('endorsee6')
        url = reverse('accept_api')
        data = json.dumps({
            "accept_id": endorsement.accept_id
        })

        response = self.client.post(url, data, content_type='application/json')

        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['accept_id'], endorsement.accept_id)
        self.assertEqual(data['service_tag'], 'o365')
        self.assertEqual(data['reason'], 'endorsee6')
        self.assertEqual(data['endorser']['netid'], 'jfaculty')
        self.assertEqual(data['endorsee']['netid'], 'endorsee7')
