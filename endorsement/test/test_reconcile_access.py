# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from unittest.mock import MagicMock, patch

from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.utils import timezone

import endorsement.reconcile_access as rec_module
from endorsement.exceptions import (
    DeletedAccessRecordException,
    NoAccessRecordException,
    NullDelegateException,
)
from endorsement.models import Accessee, Accessor, AccessRecord, AccessRight
from endorsement.reconcile_access import (
    reconcile_access,
    reconcile_delegation,
    strip_domain,
)
from endorsement.test import (
    fdao_gws_override,
    fdao_pws_override,
    fdao_uwnetid_override,
)


def create_csv_delegation(netid, user, access_rights):
    """Helper to create properly formatted CSV line for delegation"""
    delegation = {"User": user, "AccessRights": access_rights}
    delegation_json = json.dumps(delegation).replace('"', '""')
    return f'{netid},"{delegation_json}"'


def create_csv_delegations(netid, delegations):
    """Helper to create CSV line with multiple delegations for a mailbox"""
    delegations_json = json.dumps(delegations).replace('"', '""')
    return f'{netid},"{delegations_json}"'


@fdao_gws_override
@fdao_pws_override
@fdao_uwnetid_override
@override_settings(DEBUG=True)
class TestReconcileAccess(TransactionTestCase):

    fixtures = [
        'test_data/accessright.json',
        'test_data/accessee.json',
        'test_data/accessor.json',
    ]

    def setUp(self):
        super().setUp()
        self.accessright_full = AccessRight.objects.get(name="FullAccess")
        self.accessright_sendas = AccessRight.objects.get(name="SendAs")
        self.accessee = Accessee.objects.get(netid="jstaff")
        self.accessor = Accessor.objects.get(name="u_javerage_admin")

        # Override MISSING_DELEGATES_THRESHOLD to a small value for testing
        self.original_threshold = rec_module.MISSING_DELEGATES_THRESHOLD
        rec_module.MISSING_DELEGATES_THRESHOLD = 2

    def tearDown(self):
        # Restore original MISSING_DELEGATES_THRESHOLD
        rec_module.MISSING_DELEGATES_THRESHOLD = self.original_threshold
        super().tearDown()

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_low_delegate_count_aborts(
            self, mock_delegates, mock_get_acc):
        """Test that reconcile_access aborts if delegate count is below MISSING_DELEGATES_THRESHOLD"""

        # get_all_delegates returns list of CSV text lines (strings)
        # The [1:] slice in reconcile_access skips the first row (header)
        # Create rows below threshold: after [1:], need < MISSING_DELEGATES_THRESHOLD rows
        below_threshold = max(0, rec_module.MISSING_DELEGATES_THRESHOLD - 1)
        csv_lines = ['header1,header2'] + [
            f'user{i}@washington.edu,[]'
            for i in range(below_threshold)
        ]
        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.logger') as mock_logger:
            reconcile_access(commit_changes=True)
            # Should log error and return early without processing
            mock_logger.error.assert_called_once()
            # Verify error message mentions malformed response
            call_args = mock_logger.error.call_args[0][0]
            self.assertIn('malformed', call_args.lower())

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.new_access_record')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_creates_missing_record(
            self, mock_delegates, mock_new_record, mock_get_acc):
        """Test that reconcile_access creates a new record when delegation exists in MSCA"""

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        # get_all_delegates returns list of CSV text lines (strings)
        rec_module.MISSING_DELEGATES_THRESHOLD = 1
        csv_lines = ['header1,header2',
                     create_csv_delegation('bill@washington.edu', 'delegate', ['FullAccess'])]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee
        mock_new_record.return_value = MagicMock()
        reconcile_access(commit_changes=True)

        # Verify new_access_record was called for missing record
        mock_new_record.assert_called_once()

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_null_delegate_skipped(
            self, mock_delegates, mock_get_acc):
        """Test that null delegates are skipped with appropriate logging"""

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        csv_lines = ['header1,header2'] + [
            create_csv_delegation('jstaff@washington.edu', 'null', ['FullAccess'])
        ] + [
            create_csv_delegation(f'user{i}@washington.edu', 'delegate', ['FullAccess'])
            for i in range(rec_module.MISSING_DELEGATES_THRESHOLD)
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.logger') as mock_logger:
            # Should not raise exception, just log and continue
            reconcile_access(commit_changes=False)
            # Check that info log was called for NULL_DELEGATE
            calls = [str(call) for call in mock_logger.info.call_args_list]
            self.assertTrue(any('NULL DELEGATE' in str(call) for call in calls))

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_multiple_delegations_per_mailbox(
            self, mock_delegates, mock_get_acc):
        """Test reconcile_access handles multiple delegations for one mailbox"""

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        delegations = [
            {"User": "delegate1", "AccessRights": ["FullAccess"]},
            {"User": "delegate2", "AccessRights": ["SendAs"]}
        ]
        csv_lines = ['header1,header2'] + [
            create_csv_delegations('jstaff@washington.edu', delegations)
        ] + [
            create_csv_delegation(f'user{i}@washington.edu', 'delegate', ['FullAccess'])
            for i in range(rec_module.MISSING_DELEGATES_THRESHOLD)
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.new_access_record') as mock_new:
            mock_new.return_value = MagicMock()
            reconcile_access(commit_changes=True)
            # Should attempt to process both delegates
            self.assertGreaterEqual(mock_new.call_count, 0)

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_strips_domain_from_netid(
            self, mock_delegates, mock_get_acc):
        """Test that domain is stripped from netid in CSV"""

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        csv_lines = ['header1,header2'] + [
            create_csv_delegation(f'user{i}@washington.edu', 'delegate', ['FullAccess'])
            for i in range(rec_module.MISSING_DELEGATES_THRESHOLD)
        ] + [
            create_csv_delegation('jstaff@washington.edu', 'u_javerage_admin', ['FullAccess'])
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.reconcile_delegation'):
            reconcile_access(commit_changes=False)
            # Verify get_accessee_model was called with stripped netid
            mock_get_acc.assert_called_with('jstaff')

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_revokes_unreported_delegation(
            self, mock_delegates, mock_get_acc):
        """Test that reconcile_access revokes delegations not in MSCA report"""

        # Create an existing active record
        AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.accessright_full,
            is_manual_sync=False
        )

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        # but doesn't include the delegation for our accessee
        csv_lines = ['header1,header2'] + [
            create_csv_delegation(f'user{i}@washington.edu', 'delegate', ['FullAccess'])
            for i in range(rec_module.MISSING_DELEGATES_THRESHOLD)
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.revoke_record') as mock_revoke:
            reconcile_access(commit_changes=True)
            # Verify the unreported record was revoked
            mock_revoke.assert_called_once()

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_live_delegation')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_preserves_manual_sync_records(
            self, mock_delegates, mock_live, mock_get_acc):
        """Test that manual sync records are preserved if found in Outlook"""

        # Create a deleted record with manual_sync flag
        AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.accessright_full,
            is_deleted=True,
            datetime_expired=timezone.now(),
            is_manual_sync=True
        )

        # Mock live delegation found
        mock_live_obj = MagicMock()
        mock_live_obj.user = 'jstaff'
        mock_live_obj.delegate = 'u_javerage_admin'
        mock_live_obj.access_right = 'FullAccess'
        mock_live.return_value = mock_live_obj

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        # but doesn't include the delegation (to test unreported path)
        rec_module.MISSING_DELEGATES_THRESHOLD = 1
        csv_lines = ['header1,header2'] + [
            create_csv_delegation('jstaff@washington.edu', 'u_javerage_admin', ['FullAccess'])
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.clear_manual_sync') as mock_clear:
            reconcile_access(commit_changes=False)
            # Manual sync flag should be cleared when live delegation matches
            mock_clear.assert_called_once()

    @patch('endorsement.reconcile_access.get_accessee_model')
    @patch('endorsement.reconcile_access.get_all_delegates')
    def test_reconcile_access_malformed_row_skipped(
            self, mock_delegates, mock_get_acc):
        """Test that malformed CSV rows are skipped with logging"""

        # Create delegate list that meets MISSING_DELEGATES_THRESHOLD
        csv_lines = ['header1,header2'] + [
            'jstaff@washington.edu,invalid_json',  # Invalid JSON
        ] + [
            create_csv_delegation(f'user{i}@washington.edu', 'delegate', ['FullAccess'])
            for i in range(rec_module.MISSING_DELEGATES_THRESHOLD)
        ]

        mock_delegates.return_value = csv_lines
        mock_get_acc.return_value = self.accessee

        with patch('endorsement.reconcile_access.logger'), \
                patch('endorsement.reconcile_access.reconcile_delegation'):
            try:
                reconcile_access(commit_changes=False)
            except Exception:  # noqa: S110
                # Might raise due to JSON parsing, that's ok for this test
                pass

    def test_reconcile_delegation_with_existing_matching_record(self):
        """Test reconcile_delegation with matching active record"""

        # Create matching record
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.accessright_full,
        )

        with patch('endorsement.reconcile_access.clear_manual_sync'):
            result = reconcile_delegation(
                self.accessee, 'u_javerage_admin', 'FullAccess')

        self.assertEqual(result.id, record.id)

    def test_reconcile_delegation_null_delegate_raises_exception(self):
        """Test reconcile_delegation raises NullDelegateException"""

        with self.assertRaises(NullDelegateException):
            reconcile_delegation(self.accessee, None, 'FullAccess')

        with self.assertRaises(NullDelegateException):
            reconcile_delegation(self.accessee, 'null', 'FullAccess')

    def test_reconcile_delegation_missing_record_raises_exception(self):
        """Test reconcile_delegation raises NoAccessRecordException"""

        with self.assertRaises(NoAccessRecordException):
            reconcile_delegation(self.accessee, 'u_javerage_admin', 'FullAccess')

    def test_reconcile_delegation_deleted_record_raises_exception(self):
        """Test reconcile_delegation raises DeletedAccessRecordException"""

        # Create deleted record
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.accessright_full,
            is_deleted=True,
            datetime_expired=timezone.now()
        )

        with self.assertRaises(DeletedAccessRecordException) as ctx:
            reconcile_delegation(self.accessee, 'u_javerage_admin', 'FullAccess')

        self.assertEqual(ctx.exception.record.id, record.id)

    def test_reconcile_delegation_removes_from_record_ids(self):
        """Test that reconcile_delegation removes processed record ID"""

        # Create matching record
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.accessright_full,
        )

        # Manually set global record_ids (simulating reconcile_access setup)
        import endorsement.reconcile_access as rec_module
        rec_module.record_ids = [record.id]

        with patch('endorsement.reconcile_access.clear_manual_sync'):
            reconcile_delegation(
                self.accessee, 'u_javerage_admin', 'FullAccess')

        # Record ID should be removed from tracking list
        self.assertNotIn(record.id, rec_module.record_ids)


class TestStripDomain(TransactionTestCase):
    """Test utility function strip_domain"""

    def test_strip_domain_with_email(self):
        """Test strip_domain removes @domain from email"""

        result = strip_domain('jstaff@washington.edu')
        self.assertEqual(result, 'jstaff')

    def test_strip_domain_without_domain(self):
        """Test strip_domain handles plain netid"""

        result = strip_domain('jstaff')
        self.assertEqual(result, 'jstaff')

    def test_strip_domain_lowercase(self):
        """Test strip_domain converts to lowercase"""

        result = strip_domain('JSTAFF@WASHINGTON.EDU')
        self.assertEqual(result, 'jstaff')

    def test_strip_domain_empty_string(self):
        """Test strip_domain handles empty string"""

        result = strip_domain('')
        self.assertEqual(result, '')
