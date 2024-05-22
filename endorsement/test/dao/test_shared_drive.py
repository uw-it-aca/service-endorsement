# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import contextlib
import datetime
import inspect
import unittest.mock

from django.test.utils import override_settings

from uw_itbill.models import Subscription
from uw_msca.models import GoogleDriveState

from endorsement.dao.shared_drive import (
    Reconciler,
    load_or_update_subscription,
    load_shared_drives,
)
from endorsement.exceptions import ITBillSubscriptionNotFound
from endorsement.models import (
    ITBillSubscription,
    Role,
    SharedDrive,
    SharedDriveRecord,
)
from endorsement.test.dao import TestDao


# for succinctness we will always refer to this as DQ
DEFAULT_QUOTA = DQ = 100


@contextlib.contextmanager
def mock_get_default_quota():
    "Mock endorsement.dao.shared_drive.get_default_quota to return 100."
    with unittest.mock.patch(
        "endorsement.dao.shared_drive.get_default_quota", return_value=DQ
    ) as mocked_func:
        yield mocked_func


@contextlib.contextmanager
def mock_get_google_drive_states():
    "Mock endorsement.dao.shared_drive.get_google_drive_states."
    with unittest.mock.patch(
        "endorsement.dao.shared_drive.get_google_drive_states",
    ) as mocked_func:
        yield mocked_func


@contextlib.contextmanager
def mock_set_drive_quota():
    "Mock endorsement.dao.shared_drive.set_drive_quota."
    with unittest.mock.patch(
        "endorsement.dao.shared_drive.set_drive_quota"
    ) as mocked_func:
        yield mocked_func


@contextlib.contextmanager
def mock_get_subscription_by_key_remote():
    """
    Mock endorsement.dao.shared_drive.get_subscription_by_key_remote.

    Default behavior will be to raise ITBillSubscriptionNotFound().

    Set return_value or side_effect on mocked_func as needed for tests.
    """

    # Precedence of mocks is side_effect, return_value, wraps
    #
    # Create a dummy function to "wrap" for lowest precedence
    #
    # If we instead used side_effect=ITBillSubscriptionNotFound() then tests
    # would need to manually assign side_effect=None to use return_value=FOO
    def raise_ITBillSubscriptionNotFound(key_remote):
        raise ITBillSubscriptionNotFound(key_remote)

    mocked_func = unittest.mock.Mock(wraps=raise_ITBillSubscriptionNotFound)

    # mock the function in two places due to how mocking works
    # https://nedbatchelder.com/blog/201908/why_your_mock_doesnt_work.html
    with unittest.mock.patch(
        "endorsement.dao.shared_drive.get_subscription_by_key_remote",
        new=mocked_func,
    ), unittest.mock.patch(
        "endorsement.dao.itbill.get_subscription_by_key_remote",
        new=mocked_func,
    ):
        yield mocked_func


@override_settings(
    ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID="7078586b2f6cb076cad75ae9aab3ea05"
)
class BaseReconcilerTest(TestDao):
    abstract = True

    # automatically run contextmanager functions to mock DAO methods that are
    # heavily used by internal machinery
    mock_functions = [
        ("get_default_quota", mock_get_default_quota),
        (
            "get_google_drive_states",
            mock_get_google_drive_states,
        ),
        ("set_drive_quota", mock_set_drive_quota),
        (
            "get_subscription_by_key_remote",
            mock_get_subscription_by_key_remote,
        ),
    ]

    def setUp(self):
        # values we have mocked, for modification as the test needs
        self.mocks = {}
        # the context managers we use to mock, so we can __enter__ + __exit__
        self.mock_contexts = {}

        # TODO: beginning Python 3.11+ use self.enterContext()
        for name, mock_func in self.mock_functions:
            self.mock_contexts[name] = mock_func()

        for name, mock in self.mock_contexts.items():
            self.mocks[name] = mock.__enter__()

    def tearDown(self):
        for val in self.mock_contexts.values():
            val.__exit__(None, None, None)

    def get_instance(self):
        """
        Return a Reconciler instance with wraped methods.

        Patched methods delegate to underlying method by default.

        This allows checking the calls without changing behavior.

        In addition one can specify the methods to do something else. See
        https://docs.python.org/3/library/unittest.mock.html#order-of-precedence-of-side-effect-return-value-and-wraps
        """
        instance = Reconciler()

        # wrap all methods
        to_wrap = inspect.getmembers(instance, predicate=inspect.ismethod)
        for method_name, method in to_wrap:
            wrapped = unittest.mock.Mock(spec=method, wraps=method)
            setattr(instance, method_name, wrapped)

        return instance


def GDS(drive_id, member, **kwargs):
    """
    Return a GoogleDriveState object with given values.

    This object can be quite verbose to define by hand so use this helper.
    """
    defaults = {
        "role": Role.MANAGER_ROLE,
        "drive_name": "testdrive_" + drive_id,
        "org_unit_id": "org_100gb",
        "org_unit_name": "100GB",
        "size": 12345,
    }
    defaults.update(drive_id=drive_id, member=member, **kwargs)
    return GoogleDriveState(**defaults)


def SubMod(quantity, *, lifecycle_state=Subscription.DEPLOYED):
    """
    Return a uw_itbill.models.Subscription object with given values.

    This object can be quite verbose to define by hand so use this helper.

    Args:
        quantity: units of 100GB storage being purchased in excess of the
            subsidized quota. When units == 2 and subsidized_quota == 100GB,
            the drive's storage would be 300GB.
    """
    if isinstance(quantity, int):
        quantity = str(quantity)
    # Note that this missing much of an actual subscription payload
    #
    # If this quits passing tests because related classes become more strict
    # see uw_itbill/resources for a test fixture with a full payload
    data = {}

    # must match ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID
    subscription_sys_id = "7078586b2f6cb076cad75ae9aab3ea05"
    sd_provision = {
        "provision": {
            # "sys_id": subscription_sys_id,
            "product": {
                "sys_id": subscription_sys_id,
            },
            "subscription": {},
            "current_quantity": quantity,
            # quantities is the time series of provision quantity history
            "quantities": [
                {
                    "quantity": quantity,
                    "start_date": "2024-05-01",
                    "end_date": "",
                },
            ],
        },
    }
    data.update(lifecycle_state=lifecycle_state, provisions=[sd_provision])
    return Subscription(data=data)


class TestReconciler_GoogleDriveState_by_drive_id(BaseReconcilerTest):
    """
    Reconciler.GoogleDriveState_by_drive_id() provides the "current state"
    information that we reconcile our saved state against.

    Note: GoogleDriveState_by_drive_id() returns a defaultdict because it's
    easy to work with but the literal values seen in test expectations with be
    regular dicts for succinctness.
    """

    def test_empty(self):
        self.mocks["get_google_drive_states"].return_value = []
        self.assertEqual(
            self.get_instance().GoogleDriveState_by_drive_id(), {}
        )

    def test_non_empty(self):
        a = GDS(drive_id="drive1", member="bob")
        b = GDS(drive_id="drive1", member="dan")
        c = GDS(drive_id="drive2", member="steve")
        self.mocks["get_google_drive_states"].return_value = [a, b, c]

        self.assertEqual(
            self.get_instance().GoogleDriveState_by_drive_id(),
            {
                "drive1": [a, b],
                "drive2": [c],
            },
        )


class TestReconciler_base_cases(BaseReconcilerTest):
    """
    Show base case of reconciler behavior where there is no work.
    """

    def setUp(self):
        super().setUp()
        # no current drivestates
        self.mocks["get_google_drive_states"].return_value = []

    def test_reconcile_nothing(self):
        """
        Establish baseline behavior when there is no work.

        Precondition: no data loaded in database, no current drivestates.
        """
        instance = self.get_instance()
        instance.reconcile()

        # Note that these 3 methods are always called
        instance.handle_new_drives.assert_called_once_with(
            set(),
            {},
            DQ,
        )
        instance.handle_missing_drives.assert_called_once_with(set(), DQ)
        instance.reconcile_existing_drives.assert_called_once_with(
            set(), {}, DQ
        )

    def test_reconcile_calls(self):
        "Test reconcile() inner calls drive_id values."
        # TODO


# TODO: is this really necessary?
def within_last_n_seconds(val: datetime.datetime, n=1):
    """
    Predicate: is val within the last n seconds?

    This is meant to approximate 'was just created'.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - datetime.timedelta(seconds=n)) <= val <= now


class TestReconciler_new_drive_quota_checks(BaseReconcilerTest):
    """
    When a new drive is discovered is its quota correctly handled?
    """

    def test_reconcile_new_drive_subsidized(self):
        """
        Test reconciling a 'new drive' that is using the subsidized quota.

        Found with subsidized quota applied and no subscription to affect that.
        """
        self.mocks["get_google_drive_states"].return_value = [
            GDS(drive_id="drive1", member="bob")
        ]
        self.assertEqual(SharedDrive.objects.count(), 0)
        self.assertEqual(SharedDriveRecord.objects.count(), 0)

        instance = self.get_instance()
        by_id = instance.GoogleDriveState_by_drive_id()

        instance.reconcile()

        with self.subTest(msg="reconcile inner calls"):
            instance.handle_new_drives.assert_called_once_with(
                {"drive1"}, by_id, DQ
            )

        with self.subTest(msg="SharedDrive created by reconcile"):
            self.assertEqual(
                SharedDrive.objects.count(), 1, "SharedDrive not created"
            )
            sd = SharedDrive.objects.get(drive_id="drive1")
            self.assertEqual(sd.drive_id, "drive1")
            self.assertEqual(sd.members.count(), 1)

            quota = sd.drive_quota
            self.assertIsNotNone(quota)
            self.assertEqual(quota.quota_limit, DQ)

        with self.subTest(msg="SharedDriveRecord created by reconcile"):
            self.assertEqual(
                SharedDriveRecord.objects.count(),
                1,
                "SharedDriveRecord not created",
            )
            sdr = SharedDriveRecord.objects.get_record_by_drive_id("drive1")
            self.assertIsNone(sdr.subscription)
            self.assertTrue(within_last_n_seconds(sdr.datetime_created))

        self.mocks["set_drive_quota"].assert_not_called()

    def test_reconcile_new_drive_over_quota(self):
        """
        Test reconcile() finding a drive over its quota.

        Found with quota applied but no corresponding subscription.
        """
        self.mocks["get_google_drive_states"].return_value = [
            # quotas are applied at the org unit (OU) level
            GDS(drive_id="drive2", member="pam", org_unit_name="200GB"),
        ]

        self.assertEqual(SharedDrive.objects.count(), 0)
        self.assertEqual(SharedDriveRecord.objects.count(), 0)

        instance = self.get_instance()
        by_id = instance.GoogleDriveState_by_drive_id()

        instance.reconcile()

        with self.subTest(msg="reconcile inner calls"):
            instance.handle_new_drives.assert_called_once_with(
                {"drive2"}, by_id, DQ
            )

        with self.subTest(msg="set_drive_quota call in reconcile"):
            self.mocks["set_drive_quota"].assert_called_once_with(
                drive_id="drive2", quota=100
            )

        with self.subTest(msg="Quota update inside reconcile"):
            sdr = SharedDriveRecord.objects.get_record_by_drive_id("drive2")
            self.assertEqual(
                sdr.shared_drive.drive_quota.quota_limit,
                DQ,
                (
                    "Quota for unsubsidized drive not set to subsidized level "
                    "due to lack of ITBill subscription"
                ),
            )

    def test_reconcile_new_drive_under_quota(self):
        """
        Test reconcile() finding drive under its subscription quota.

        Found with quota applied but subscription indicates a higher quota is
        correct.
        """
        self.mocks["get_google_drive_states"].return_value = [
            # quotas are applied at the org unit (OU) level
            GDS(drive_id="drive3", member="dan", org_unit_name="200GB"),
        ]
        self.mocks["get_subscription_by_key_remote"].return_value = SubMod(
            quantity="2",  # AKA 300 GB quota
        )

        instance = self.get_instance()
        instance.reconcile()

        with self.subTest(msg="set_drive_quota call in reconcile"):
            self.mocks["set_drive_quota"].assert_called_once_with(
                drive_id="drive3", quota=300
            )

        with self.subTest(msg="Quota update inside reconcile"):
            sdr = SharedDriveRecord.objects.get_record_by_drive_id("drive3")
            self.assertIsNotNone(sdr.subscription)
            self.assertEqual(
                sdr.shared_drive.drive_quota.quota_limit,
                300,
                (
                    "Quota for unsubsidized drive not reconciled to "
                    "ITBill provision level of 300GB"
                ),
            )

    def test_reconcile_new_drive_at_subscription_quota(self):
        """
        Test reconcile() finding a drive at the correct subscription quota.

        Found with quota applied and corresponding subscription.
        """
        self.mocks["get_google_drive_states"].return_value = [
            # quotas are applied at the org unit (OU) level
            GDS(drive_id="drive4", member="amy", org_unit_name="300GB"),
        ]
        self.mocks["get_subscription_by_key_remote"].return_value = SubMod(
            quantity=2,  # AKA 300 GB quota
        )

        instance = self.get_instance()
        instance.reconcile()

        with self.subTest(msg="set_drive_quota not called in reconcile"):
            self.mocks["set_drive_quota"].assert_not_called()

        with self.subTest(msg="Unmodified quota after reconcile"):
            sdr = SharedDriveRecord.objects.get_record_by_drive_id("drive4")
            self.assertIsNotNone(sdr.subscription)
            self.assertEqual(
                sdr.shared_drive.drive_quota.quota_limit,
                300,
            )


class TestReconciler_alerts_for_provisioning(BaseReconcilerTest):
    """
    Test reconcile() finding a new drive prompts the manager(s) to endorse it.
    """

    # TODO: what exactly is the spec here?


class TestReconciler_reconcile_missing_drives(BaseReconcilerTest):
    """
    Drives with no members will disappear from the reconciliation report.

    In addition, drives actaully deleted will disappear.
    """

    def setUp(self):
        super().setUp()
        load_shared_drives(
            [GDS(drive_id="missing1", member="amy", org_unit_name="100GB")],
        )

    def test_reconcile_missing_drives_set_deleted(self):
        "Confirm related SharedDrive object has is_deleted flag set to True"
        sd = SharedDrive.objects.get(drive_id="missing1")
        self.assertFalse(sd.is_deleted)

        instance = self.get_instance()
        instance.reconcile()

        sd = SharedDrive.objects.get(drive_id="missing1")
        self.assertTrue(sd.is_deleted)


class TestReconciler_reconcile_existing_drives(BaseReconcilerTest):
    """
    Test reconciling drives which previously existed in PRT.

    This is similar to reconciling new drives but has additional variants.

    - Does the drive_name need updating (can change out-of-band)
    - Is the subscription still valid? If not, set to subsidized quota
    - Were the related managers updated?
    - Does a drive still have manager member(s) who have provisioned?
        TODO
    - Has the provision expired? If not, does it alert the manager(s)?
        TODO
    """

    def setUp(self):
        super().setUp()
        sdr = load_shared_drives(
            [
                GDS(
                    drive_id="exists",
                    member="bob",
                    drive_name="bob's drive",
                    org_unit_name="300GB",
                )
            ]
        )
        self.mocks["get_subscription_by_key_remote"].return_value = SubMod(
            quantity="2",  # AKA 300 GB quota
        )
        load_or_update_subscription(sdr)

        # IMPORTANT - mutate this (or assign a new return_value) for tests
        self.new_drive_state = GDS(drive_id="exists", member="bob")

        self.mocks["get_google_drive_states"].return_value = [
            self.new_drive_state,
        ]

    def test_updated_drive_name(self):
        self.new_drive_state.drive_name = "Bob's Drive"

        sd = SharedDrive.objects.get(drive_id="exists")
        self.assertEqual(sd.drive_name, "bob's drive")

        instance = self.get_instance()
        instance.reconcile()

        with self.subTest(msg="Test update to drive name"):
            sd = SharedDrive.objects.get(drive_id="exists")
            self.assertEqual(sd.drive_name, "Bob's Drive")

    def test_subscription_expired(self):
        """
        Test correct updates occur when the subscription has expired.
        """
        self.mocks["get_subscription_by_key_remote"].return_value = SubMod(
            quantity="2",
            lifecycle_state=Subscription.CLOSED,
        )

        instance = self.get_instance()
        instance.reconcile()

        sdr = SharedDriveRecord.objects.get_record_by_drive_id("exists")

        with self.subTest(msg="Quota update from reconcile"):
            self.assertEqual(
                sdr.shared_drive.drive_quota.quota_limit,
                DQ,
                "Quota for subsidized drive not reconciled to 100GB",
            )

        with self.subTest(msg="related subscription is updated"):
            self.assertIsNotNone(sdr.subscription)
            self.assertEqual(
                sdr.subscription.state, ITBillSubscription.SUBSCRIPTION_CLOSED
            )

    def test_members_updated(self):
        """
        Test SharedDrive members are updated.
        """
        sd = SharedDrive.objects.get(drive_id="exists")
        self.assertEqual(
            set(sd.members.values_list("member__netid", flat=True)),
            {"bob"},
        )

        self.mocks["get_google_drive_states"].return_value = [
            GDS(drive_id="exists", member="pam"),
            GDS(drive_id="exists", member="sam"),
        ]

        instance = self.get_instance()
        instance.reconcile()

        self.assertEqual(
            set(sd.members.values_list("member__netid", flat=True)),
            {"pam", "sam"},
        )
