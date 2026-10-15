# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from unittest.mock import Mock, patch

from django.urls import reverse
from restclients_core.exceptions import InvalidNetID

from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.models import AccessRecord, AccessRecordConflict
from endorsement.test.api import EndorsementApiTest


class TestOfficeAccessGet(EndorsementApiTest):
    """Unit tests for Access.get() method in office/access.py"""

    def setUp(self):
        super().setUp()
        self.url = reverse('access_api')
        self.netid = 'testuser'
        self.set_user(self.netid)

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_user_with_office_access(self, mock_get_accessee,
                                          mock_is_office_permitted,
                                          mock_get_supported,
                                          mock_get_messages):
        """Test GET when user has office access permission"""
        mock_accessee = Mock()
        mock_accessee.netid = self.netid
        mock_accessee.display_name = 'Test User'

        mock_get_accessee.return_value = mock_accessee
        mock_is_office_permitted.side_effect = lambda netid: netid == self.netid
        mock_get_supported.return_value = []
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('netids', data)
        self.assertIn('messages', data)
        self.assertIn(self.netid, data['netids'])
        self.assertEqual(data['netids'][self.netid]['name'], 'Test User')
        self.assertEqual(data['netids'][self.netid]['access'], [])
        self.assertEqual(data['netids'][self.netid]['conflict'], [])

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_user_without_office_access(self, mock_get_accessee,
                                             mock_is_office_permitted,
                                             mock_get_supported,
                                             mock_get_messages):
        """Test GET when user does not have office access permission"""
        mock_get_accessee.return_value = Mock()
        mock_is_office_permitted.return_value = False
        mock_get_supported.return_value = []
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('netids', data)
        self.assertNotIn(self.netid, data['netids'])

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_with_supported_resources(self, mock_get_accessee,
                                          mock_is_office_permitted,
                                          mock_get_supported,
                                          mock_get_messages):
        """Test GET when user has supported resources"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        supported_accessee = Mock()
        supported_accessee.netid = 'supported_user'
        supported_accessee.display_name = 'Supported User'

        supported_resource = Mock()
        supported_resource.name = 'supported_user'
        supported_resource.is_owner.return_value = True
        supported_resource.is_shared_netid.return_value = True
        supported_resource.netid_type = 'shared_netid'

        mock_get_accessee.side_effect = [
            user_accessee,
            supported_accessee
        ]
        mock_is_office_permitted.side_effect = [
            True,  # For user
            True   # For supported resource
        ]
        mock_get_supported.return_value = [supported_resource]
        mock_get_messages.return_value = [{'text': 'Test message'}]

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(self.netid, data['netids'])
        self.assertIn('supported_user', data['netids'])
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['text'], 'Test message')

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_with_access_records(self, mock_get_accessee,
                                     mock_is_office_permitted,
                                     mock_get_supported,
                                     mock_get_messages):
        """Test GET returns access records for user"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        mock_get_accessee.return_value = user_accessee
        mock_is_office_permitted.return_value = True
        mock_get_supported.return_value = []
        mock_get_messages.return_value = []

        access_record = Mock()
        access_record.json_data.return_value = {
            'accessee': {'netid': self.netid},
            'accessor': {'netid': 'accessor_user'},
            'access_type': 'FullAccess'
        }

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[access_record]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['netids'][self.netid]['access']), 1)
        self.assertEqual(
            data['netids'][self.netid]['access'][0]['accessor']['netid'],
            'accessor_user'
        )

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_with_access_conflicts(self, mock_get_accessee,
                                       mock_is_office_permitted,
                                       mock_get_supported,
                                       mock_get_messages):
        """Test GET returns access conflicts for user"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'
        user_accessee.id = 1

        mock_get_accessee.return_value = user_accessee
        mock_is_office_permitted.return_value = True
        mock_get_supported.return_value = []
        mock_get_messages.return_value = []

        conflict = Mock()
        conflict.json_data.return_value = {
            'accessee': {'netid': self.netid},
            'conflict_type': 'dual_mailbox'
        }

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[conflict]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['netids'][self.netid]['conflict']), 1)
        self.assertEqual(
            data['netids'][self.netid]['conflict'][0]['conflict_type'],
            'dual_mailbox'
        )

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_filters_access_by_accessee(self, mock_get_accessee,
                                            mock_is_office_permitted,
                                            mock_get_supported,
                                            mock_get_messages):
        """Test GET filters access records by accessee netid"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        supported_accessee = Mock()
        supported_accessee.netid = 'supported_user'
        supported_accessee.display_name = 'Supported User'

        supported_resource = Mock()
        supported_resource.name = 'supported_user'
        supported_resource.is_owner.return_value = True
        supported_resource.is_shared_netid.return_value = True

        user_resource = Mock()
        user_resource.name = self.netid
        user_resource.is_owner.return_value = True
        user_resource.is_shared_netid.return_value = True

        mock_get_accessee.side_effect = [
            user_accessee,
            user_accessee,
            supported_accessee
        ]
        mock_is_office_permitted.side_effect = [True, True, True]
        mock_get_supported.return_value = [user_resource, supported_resource]
        mock_get_messages.return_value = []

        access_for_user = Mock()
        access_for_user.json_data.return_value = {
            'accessee': {'netid': self.netid},
            'accessor': {'netid': 'accessor1'},
            'access_type': 'FullAccess'
        }

        access_for_supported = Mock()
        access_for_supported.json_data.return_value = {
            'accessee': {'netid': 'supported_user'},
            'accessor': {'netid': 'accessor2'},
            'access_type': 'SendAs'
        }

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[access_for_user, access_for_supported]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # User should only have access_for_user
        self.assertEqual(len(data['netids'][self.netid]['access']), 1)
        self.assertEqual(
            data['netids'][self.netid]['access'][0]['accessor']['netid'],
            'accessor1'
        )
        # Supported user should only have access_for_supported
        self.assertEqual(len(data['netids']['supported_user']['access']), 1)
        self.assertEqual(
            data['netids']['supported_user']['access'][0]['accessor']['netid'],
            'accessor2'
        )

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_filters_conflicts_by_accessee(self, mock_get_accessee,
                                               mock_is_office_permitted,
                                               mock_get_supported,
                                               mock_get_messages):
        """Test GET filters conflict records by accessee netid"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'
        user_accessee.id = 1

        supported_accessee = Mock()
        supported_accessee.netid = 'supported_user'
        supported_accessee.display_name = 'Supported User'
        supported_accessee.id = 2

        supported_resource = Mock()
        supported_resource.name = 'supported_user'
        supported_resource.is_owner.return_value = True
        supported_resource.is_shared_netid.return_value = True

        user_resource = Mock()
        user_resource.name = self.netid
        user_resource.is_owner.return_value = True
        user_resource.is_shared_netid.return_value = True

        mock_get_accessee.side_effect = [
            user_accessee,
            user_accessee,
            supported_accessee
        ]
        mock_is_office_permitted.side_effect = [True, True, True]
        mock_get_supported.return_value = [user_resource, supported_resource]
        mock_get_messages.return_value = []

        conflict_for_user = Mock()
        conflict_for_user.json_data.return_value = {
            'accessee': {'netid': self.netid},
            'conflict_type': 'dual_mailbox'
        }

        conflict_for_supported = Mock()
        conflict_for_supported.json_data.return_value = {
            'accessee': {'netid': 'supported_user'},
            'conflict_type': 'shared_netid_access'
        }

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[conflict_for_user, conflict_for_supported]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)



        # User should only have conflict_for_user
        self.assertEqual(len(data['netids'][self.netid]['conflict']), 1)
        self.assertEqual(
            data['netids'][self.netid]['conflict'][0]['conflict_type'],
            'dual_mailbox'
        )
        # Supported user should only have conflict_for_supported
        self.assertEqual(len(data['netids']['supported_user']['conflict']), 1)
        self.assertEqual(
            data['netids']['supported_user']['conflict'][0]['conflict_type'],
            'shared_netid_access'
        )

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_excludes_invalid_accessors(self, mock_get_accessee,
                                            mock_is_office_permitted,
                                            mock_get_supported,
                                            mock_get_messages):
        """Test GET excludes supported resources that are not valid accessors"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        # Valid accessor - owner with shared netid
        valid_resource = Mock()
        valid_resource.name = 'valid_user'
        valid_resource.is_owner.return_value = True
        valid_resource.is_shared_netid.return_value = True

        # Invalid accessor - not owner
        invalid_resource = Mock()
        invalid_resource.name = 'invalid_user'
        invalid_resource.is_owner.return_value = False
        invalid_resource.is_shared_netid.return_value = True

        mock_get_accessee.return_value = user_accessee
        mock_is_office_permitted.return_value = True
        mock_get_supported.return_value = [valid_resource, invalid_resource]
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Only user should be in netids, valid_user should not be added
        # because it was a supported resource with is_office_permitted() = True
        self.assertEqual(len(data['netids']), 1)

    @patch('endorsement.views.api.office.access.logger')
    @patch('endorsement.views.api.office.access.is_support_user')
    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_unrecognized_netid(self, mock_get_accessee,
                                    mock_is_office_permitted,
                                    mock_get_supported,
                                    mock_get_messages,
                                    mock_is_support,
                                    mock_logger):
        """Test GET with UnrecognizedUWNetid exception returns invalid session"""
        with patch(
            'endorsement.views.api.office.access.Access._validate_user'
        ) as mock_validate:
            mock_validate.side_effect = UnrecognizedUWNetid('test')

            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    @patch('endorsement.views.api.office.access.logger')
    @patch('endorsement.views.api.office.access.is_support_user')
    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_invalid_netid(self, mock_get_accessee,
                               mock_is_office_permitted,
                               mock_get_supported,
                               mock_get_messages,
                               mock_is_support,
                               mock_logger):
        """Test GET with InvalidNetID exception returns invalid endorser"""
        with patch(
            'endorsement.views.api.office.access.Access._validate_user'
        ) as mock_validate:
            mock_validate.side_effect = InvalidNetID('test')

            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_response_structure(self, mock_get_accessee,
                                    mock_is_office_permitted,
                                    mock_get_supported,
                                    mock_get_messages):
        """Test GET response has correct structure"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        mock_get_accessee.return_value = user_accessee
        mock_is_office_permitted.return_value = True
        mock_get_supported.return_value = []
        mock_get_messages.return_value = [{'id': 1, 'text': 'msg1'}]

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Check top-level structure
        self.assertIsInstance(data, dict)
        self.assertIn('netids', data)
        self.assertIn('messages', data)
        self.assertIsInstance(data['netids'], dict)
        self.assertIsInstance(data['messages'], list)

        # Check netid structure
        netid_data = data['netids'][self.netid]
        self.assertIn('name', netid_data)
        self.assertIn('access', netid_data)
        self.assertIn('conflict', netid_data)
        self.assertIsInstance(netid_data['name'], str)
        self.assertIsInstance(netid_data['access'], list)
        self.assertIsInstance(netid_data['conflict'], list)

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_with_administrator_accessor(self, mock_get_accessee,
                                             mock_is_office_permitted,
                                             mock_get_supported,
                                             mock_get_messages):
        """Test GET includes supported resources that are administrators"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        admin_accessee = Mock()
        admin_accessee.netid = 'admin_user'
        admin_accessee.display_name = 'Admin User'

        admin_resource = Mock()
        admin_resource.name = 'admin_user'
        admin_resource.is_owner.return_value = True
        admin_resource.is_shared_netid.return_value = False
        admin_resource.netid_type = 'administrator'

        mock_get_accessee.side_effect = [
            user_accessee,
            admin_accessee
        ]
        mock_is_office_permitted.side_effect = [True, True]
        mock_get_supported.return_value = [admin_resource]
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(self.netid, data['netids'])
        self.assertIn('admin_user', data['netids'])

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_with_support_accessor(self, mock_get_accessee,
                                       mock_is_office_permitted,
                                       mock_get_supported,
                                       mock_get_messages):
        """Test GET includes supported resources that are support users"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        support_accessee = Mock()
        support_accessee.netid = 'support_user'
        support_accessee.display_name = 'Support User'

        support_resource = Mock()
        support_resource.name = 'support_user'
        support_resource.is_owner.return_value = True
        support_resource.is_shared_netid.return_value = False
        support_resource.netid_type = 'support'

        mock_get_accessee.side_effect = [
            user_accessee,
            support_accessee
        ]
        mock_is_office_permitted.side_effect = [True, True]
        mock_get_supported.return_value = [support_resource]
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(self.netid, data['netids'])
        self.assertIn('support_user', data['netids'])

    @patch('endorsement.views.api.office.access.get_persistent_messages')
    @patch('endorsement.views.api.office.access.get_supported_resources_for_netid')
    @patch('endorsement.views.api.office.access.is_office_permitted')
    @patch('endorsement.views.api.office.access.get_accessee_model')
    def test_get_multiple_accessees_with_mixed_permissions(
            self, mock_get_accessee,
            mock_is_office_permitted,
            mock_get_supported,
            mock_get_messages):
        """Test GET with multiple accessees and mixed office permissions"""
        user_accessee = Mock()
        user_accessee.netid = self.netid
        user_accessee.display_name = 'Test User'

        permitted_accessee = Mock()
        permitted_accessee.netid = 'permitted_user'
        permitted_accessee.display_name = 'Permitted User'

        permitted_resource = Mock()
        permitted_resource.name = 'permitted_user'
        permitted_resource.is_owner.return_value = True
        permitted_resource.is_shared_netid.return_value = True

        unpermitted_resource = Mock()
        unpermitted_resource.name = 'unpermitted_user'
        unpermitted_resource.is_owner.return_value = True
        unpermitted_resource.is_shared_netid.return_value = True

        mock_get_accessee.side_effect = [
            user_accessee,
            permitted_accessee
        ]
        # Return True for user and permitted_user, False for unpermitted_user
        mock_is_office_permitted.side_effect = [True, True, False]
        mock_get_supported.return_value = [
            permitted_resource,
            unpermitted_resource
        ]
        mock_get_messages.return_value = []

        with patch.object(
            AccessRecord.objects,
            'get_access_for_accessee',
            return_value=[]
        ), patch.object(
            AccessRecordConflict.objects,
            'filter',
            return_value=[]
        ):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(self.netid, data['netids'])
        self.assertIn('permitted_user', data['netids'])
        self.assertNotIn('unpermitted_user', data['netids'])
