# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import uuid
from django.test import TestCase
from django.utils import timezone

from endorsement.models import (
    Accessor,
    Accessee,
    AccessRight,
    AccessRecord,
)


def generate_regid():
    """Generate a unique regid for testing"""
    return uuid.uuid4().hex[:32]


def generate_accessor_name(prefix='accessor'):
    """Generate a unique accessor name for testing"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestAccessRecord(TestCase):
    """Unit tests for AccessRecord model"""

    def setUp(self):
        """Set up test fixtures"""
        self.accessor = Accessor.objects.create(
            name=generate_accessor_name('test_accessor'),
            display_name='Test Accessor',
            is_valid=True
        )
        self.accessee = Accessee.objects.create(
            netid='testuser',
            display_name='Test User',
            regid=generate_regid(),
            is_valid=True
        )
        self.access_right = AccessRight.objects.create(
            name='full-access',
            display_name='Full Access'
        )

    def test_access_record_creation(self):
        """Test creating an AccessRecord"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            acted_as='admin',
            datetime_granted=timezone.now()
        )
        self.assertEqual(record.accessee, self.accessee)
        self.assertEqual(record.accessor, self.accessor)
        self.assertEqual(record.access_right, self.access_right)
        self.assertEqual(record.acted_as, 'admin')
        self.assertIsNotNone(record.datetime_granted)
        self.assertIsNone(record.is_deleted)

    def test_access_record_json_data(self):
        """Test AccessRecord json_data method"""
        now = timezone.now()
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            acted_as='admin',
            datetime_granted=now,
            datetime_created=now
        )
        json_data = record.json_data()
        self.assertIn('accessor', json_data)
        self.assertIn('accessee', json_data)
        self.assertIn('access_right', json_data)
        self.assertEqual(json_data['acted_as'], 'admin')
        self.assertFalse(json_data['is_revoked'])

    def test_access_record_json_data_with_dates(self):
        """Test AccessRecord json_data includes all date fields"""
        now = timezone.now()
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            datetime_created=now,
            datetime_emailed=now,
            datetime_granted=now,
            datetime_renewed=now,
            datetime_expired=now
        )
        json_data = record.json_data()
        self.assertIsNotNone(json_data['datetime_emailed'])
        self.assertIsNotNone(json_data['datetime_granted'])
        self.assertIsNotNone(json_data['datetime_renewed'])
        self.assertIsNotNone(json_data['datetime_expired'])

    def test_access_record_json_data_with_notice_dates(self):
        """Test AccessRecord json_data includes notice email dates"""
        now = timezone.now()
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            datetime_notice_1_emailed=now,
            datetime_notice_2_emailed=now,
            datetime_notice_3_emailed=now,
            datetime_notice_4_emailed=now
        )
        json_data = record.json_data()
        self.assertIsNotNone(json_data['datetime_notice_1_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_2_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_3_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_4_emailed'])

    def test_access_record_revoke(self):
        """Test revoking an AccessRecord"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record.revoke()

        self.assertTrue(record.is_deleted)
        self.assertIsNotNone(record.datetime_expired)

        # Verify json_data reflects revoke
        json_data = record.json_data()
        self.assertTrue(json_data['is_revoked'])

    def test_access_record_revoke_persistence(self):
        """Test revoked record is persisted to database"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record_id = record.id
        record.revoke()

        # Fetch from database to verify persistence
        fetched = AccessRecord.objects.get(id=record_id)
        self.assertTrue(fetched.is_deleted)
        self.assertIsNotNone(fetched.datetime_expired)

    def test_access_record_emailed(self):
        """Test marking an AccessRecord as emailed"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record.emailed()

        self.assertIsNotNone(record.datetime_emailed)

    def test_access_record_emailed_persistence(self):
        """Test emailed timestamp is persisted to database"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record_id = record.id
        record.emailed()

        # Fetch from database to verify persistence
        fetched = AccessRecord.objects.get(id=record_id)
        self.assertIsNotNone(fetched.datetime_emailed)

    def test_access_record_equality(self):
        """Test AccessRecord equality comparison"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )

        # Create another accessee and record
        accessee2 = Accessee.objects.create(
            netid='user2',
            regid=generate_regid()
        )
        record2 = AccessRecord.objects.create(
            accessee=accessee2,
            accessor=self.accessor,
            access_right=self.access_right
        )

        # Same accessee, accessor, and right
        record1_again = AccessRecord.objects.get(id=record1.id)
        self.assertEqual(record1, record1_again)

        # Different accessee
        self.assertNotEqual(record1, record2)
        self.assertNotEqual(record1, None)

    def test_access_record_equality_different_right(self):
        """Test AccessRecord equality with different access rights"""
        right2 = AccessRight.objects.create(
            name='send-as',
            display_name='Send As'
        )
        accessor2 = Accessor.objects.create(
            name=generate_accessor_name('accessor'),
            display_name='Accessor 2'
        )
        record1 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=accessor2,
            access_right=right2
        )

        self.assertNotEqual(record1, record2)

    def test_access_record_equality_different_accessor(self):
        """Test AccessRecord equality with different accessors"""
        accessor2 = Accessor.objects.create(
            name=generate_accessor_name('accessor'),
            display_name='Test Accessor 2'
        )
        record1 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=accessor2,
            access_right=self.access_right
        )

        self.assertNotEqual(record1, record2)

    def test_access_record_string_representation(self):
        """Test AccessRecord __str__ method"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        str_repr = str(record)
        self.assertIn('testuser', str_repr)
        self.assertIn('test_accessor', str_repr)

    def test_access_record_unique_constraint(self):
        """Test AccessRecord unique constraint on accessor and accessee"""
        AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )

        with self.assertRaises(Exception):
            AccessRecord.objects.create(
                accessee=self.accessee,
                accessor=self.accessor,
                access_right=self.access_right
            )

    def test_access_record_with_all_dates(self):
        """Test AccessRecord with all date fields"""
        now = timezone.now()
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            datetime_created=now,
            datetime_emailed=now,
            datetime_notice_1_emailed=now,
            datetime_notice_2_emailed=now,
            datetime_notice_3_emailed=now,
            datetime_notice_4_emailed=now,
            datetime_granted=now,
            datetime_renewed=now,
            datetime_expired=now
        )

        json_data = record.json_data()
        self.assertIsNotNone(json_data['datetime_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_1_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_2_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_3_emailed'])
        self.assertIsNotNone(json_data['datetime_notice_4_emailed'])
        self.assertIsNotNone(json_data['datetime_granted'])
        self.assertIsNotNone(json_data['datetime_renewed'])
        self.assertIsNotNone(json_data['datetime_expired'])

    def test_access_record_null_dates(self):
        """Test AccessRecord handles null date fields"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )

        json_data = record.json_data()
        self.assertIsNone(json_data['datetime_emailed'])
        self.assertIsNone(json_data['datetime_granted'])

    def test_access_record_null_acted_as(self):
        """Test AccessRecord with null acted_as field"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right,
            acted_as=None
        )
        json_data = record.json_data()
        self.assertIsNone(json_data['acted_as'])

    def test_access_record_null_access_right(self):
        """Test AccessRecord with null access_right field"""
        record = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=None
        )
        # This should work since access_right is nullable
        self.assertIsNone(record.access_right)

    def test_access_record_multiple_for_same_accessee(self):
        """Test multiple AccessRecords for same accessee with different accessors"""
        accessor2 = Accessor.objects.create(
            name=generate_accessor_name('accessor'),
            display_name='Accessor 2'
        )
        record1 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=accessor2,
            access_right=self.access_right
        )

        records = AccessRecord.objects.filter(accessee=self.accessee)
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)

    def test_access_record_multiple_for_same_accessor(self):
        """Test multiple AccessRecords for same accessor with different accessees"""
        accessee2 = Accessee.objects.create(
            netid='user2',
            regid=generate_regid()
        )
        record1 = AccessRecord.objects.create(
            accessee=self.accessee,
            accessor=self.accessor,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=accessee2,
            accessor=self.accessor,
            access_right=self.access_right
        )

        records = AccessRecord.objects.filter(accessor=self.accessor)
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)

    def test_access_record_meta_db_table(self):
        """Test AccessRecord uses correct database table"""
        self.assertEqual(
            AccessRecord._meta.db_table,
            'uw_service_endorsement_access'
        )

    def test_access_record_meta_unique_together(self):
        """Test AccessRecord has unique_together constraint"""
        unique_together = AccessRecord._meta.unique_together
        self.assertIn(('accessor', 'accessee'), unique_together)


class TestAccessRecordManager(TestCase):
    """Unit tests for AccessRecordManager query methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.accessor1 = Accessor.objects.create(
            name=generate_accessor_name('accessor'),
            display_name='Accessor 1',
            is_valid=True
        )
        self.accessor2 = Accessor.objects.create(
            name=generate_accessor_name('accessor'),
            display_name='Accessor 2',
            is_valid=True
        )
        self.accessee1 = Accessee.objects.create(
            netid='accessee1',
            display_name='Accessee 1',
            regid=generate_regid(),
            is_valid=True
        )
        self.accessee2 = Accessee.objects.create(
            netid='accessee2',
            display_name='Accessee 2',
            regid=generate_regid(),
            is_valid=True
        )
        self.access_right = AccessRight.objects.create(
            name='full-access',
            display_name='Full Access'
        )

    def test_get_access_all_records(self):
        """Test get_access returns all active records when no filter"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor2,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access()
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)

    def test_get_access_by_accessor(self):
        """Test get_access filters by accessor"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor2,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access(accessor=self.accessor1)
        self.assertEqual(records.count(), 1)
        self.assertEqual(list(records), [record1])

    def test_get_access_by_accessee(self):
        """Test get_access filters by accessee"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor2,
            access_right=self.access_right
        )

        # Need to create a third accessee for another record
        accessee3 = Accessee.objects.create(
            netid='accessee3',
            regid=generate_regid()
        )
        record3 = AccessRecord.objects.create(
            accessee=accessee3,
            accessor=self.accessor1,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access(accessee=self.accessee1)
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)
        self.assertNotIn(record3, records)

    def test_get_access_by_accessor_and_accessee(self):
        """Test get_access with both accessor and accessee"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor1,
            access_right=self.access_right
        )

        record = AccessRecord.objects.get_access(
            accessor=self.accessor1,
            accessee=self.accessee1
        )
        self.assertEqual(record, record1)

    def test_get_access_excludes_deleted(self):
        """Test get_access excludes deleted records"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor2,
            access_right=self.access_right
        )
        record2.revoke()

        records = AccessRecord.objects.get_access()
        self.assertEqual(records.count(), 1)
        self.assertEqual(list(records), [record1])

    def test_get_access_for_accessor(self):
        """Test get_access_for_accessor convenience method"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record3 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor2,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access_for_accessor(self.accessor1)
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)
        self.assertNotIn(record3, records)

    def test_get_all_access_for_accessor(self):
        """Test get_all_access_for_accessor includes deleted records"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2.revoke()

        records = AccessRecord.objects.get_all_access_for_accessor(
            self.accessor1
        )
        self.assertEqual(records.count(), 2)

    def test_get_access_for_accessee(self):
        """Test get_access_for_accessee convenience method"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor2,
            access_right=self.access_right
        )
        record3 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor1,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access_for_accessee(self.accessee1)
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)
        self.assertNotIn(record3, records)

    def test_get_access_for_accessee_with_list(self):
        """Test get_access_for_accessee with a list of accessees"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        accessee3 = Accessee.objects.create(
            netid='accessee3',
            regid=generate_regid()
        )
        record3 = AccessRecord.objects.create(
            accessee=accessee3,
            accessor=self.accessor1,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access_for_accessee(
            [self.accessee1, self.accessee2]
        )
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)
        self.assertNotIn(record3, records)

    def test_get_access_for_accessee_re(self):
        """Test get_access_for_accessee_re regex filter"""
        # Create accessees with pattern
        accessee_pattern1 = Accessee.objects.create(
            netid='test001',
            regid=generate_regid()
        )
        accessee_pattern2 = Accessee.objects.create(
            netid='test002',
            regid=generate_regid()
        )
        accessee_no_match = Accessee.objects.create(
            netid='other',
            regid=generate_regid()
        )

        record1 = AccessRecord.objects.create(
            accessee=accessee_pattern1,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record2 = AccessRecord.objects.create(
            accessee=accessee_pattern2,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record3 = AccessRecord.objects.create(
            accessee=accessee_no_match,
            accessor=self.accessor1,
            access_right=self.access_right
        )

        records = AccessRecord.objects.get_access_for_accessee_re('test[0-9]{3}')
        self.assertEqual(records.count(), 2)
        self.assertIn(record1, records)
        self.assertIn(record2, records)
        self.assertNotIn(record3, records)

    def test_get_access_for_accessee_re_excludes_deleted(self):
        """Test get_access_for_accessee_re excludes deleted records"""
        accessee_pattern = Accessee.objects.create(
            netid='test001',
            regid=generate_regid()
        )

        record1 = AccessRecord.objects.create(
            accessee=accessee_pattern,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record1.revoke()

        records = AccessRecord.objects.get_access_for_accessee_re('test[0-9]{3}')
        self.assertEqual(records.count(), 0)

    def test_get_all_endorsements_for_accessee_re(self):
        """Test get_all_endorsements_for_accessee_re includes deleted records"""
        accessee_pattern = Accessee.objects.create(
            netid='test001',
            regid=generate_regid()
        )

        record1 = AccessRecord.objects.create(
            accessee=accessee_pattern,
            accessor=self.accessor1,
            access_right=self.access_right
        )
        record1.revoke()

        records = AccessRecord.objects.get_all_endorsements_for_accessee_re(
            'test[0-9]{3}'
        )
        self.assertEqual(records.count(), 1)

    def test_get_unnotified_accessors(self):
        """Test get_unnotified_accessors query"""
        now = timezone.now()

        # Create unnotified record
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right,
            datetime_granted=now,
            datetime_emailed=None
        )

        # Create notified record
        record2 = AccessRecord.objects.create(
            accessee=self.accessee2,
            accessor=self.accessor2,
            access_right=self.access_right,
            datetime_granted=now,
            datetime_emailed=now
        )

        unnotified = AccessRecord.objects.get_unnotified_accessors()
        self.assertEqual(unnotified.count(), 1)
        self.assertEqual(list(unnotified), [record1])

    def test_get_unnotified_accessors_excludes_no_grant_date(self):
        """Test get_unnotified_accessors excludes records without grant date"""
        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right,
            datetime_granted=None
        )

        unnotified = AccessRecord.objects.get_unnotified_accessors()
        self.assertEqual(unnotified.count(), 0)

    def test_get_unnotified_accessors_excludes_reconcile(self):
        """Test get_unnotified_accessors excludes reconcile records"""
        now = timezone.now()

        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right,
            datetime_granted=now,
            is_reconcile=True
        )

        unnotified = AccessRecord.objects.get_unnotified_accessors()
        self.assertEqual(unnotified.count(), 0)

    def test_get_unnotified_accessors_excludes_deleted(self):
        """Test get_unnotified_accessors excludes deleted records"""
        now = timezone.now()

        record1 = AccessRecord.objects.create(
            accessee=self.accessee1,
            accessor=self.accessor1,
            access_right=self.access_right,
            datetime_granted=now
        )
        record1.revoke()

        unnotified = AccessRecord.objects.get_unnotified_accessors()
        self.assertEqual(unnotified.count(), 0)

    def test_get_access_empty_result(self):
        """Test get_access with no matching records"""
        records = AccessRecord.objects.get_access(accessor=self.accessor1)
        self.assertEqual(records.count(), 0)
