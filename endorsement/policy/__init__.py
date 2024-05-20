# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Provisioned service lifecycle policy base class
"""
from abc import ABC, abstractmethod
from django.utils import timezone
from datetime import timedelta


# Default lifecycle day counts
DEFAULT_LIFETIME = 365
DEFAULT_GRACEPERIOD = 0
PRIOR_DAYS_NOTICE_WARNING_1 = 90
PRIOR_DAYS_NOTICE_WARNING_2 = 30
PRIOR_DAYS_NOTICE_WARNING_3 = 7
PRIOR_DAYS_NOTICE_WARNING_4 = 0


class PolicyBase(ABC):
    @property
    @abstractmethod
    def record_model(self):
        """Provision Record subect to policy"""
        pass

    @property
    @abstractmethod
    def datetime_provisioned_key(self):
        """Model Field storing datetime the service was provisioned"""
        pass

    @property
    def lifetime(self):
        return DEFAULT_LIFETIME

    @property
    def graceperiod(self):
        return DEFAULT_GRACEPERIOD

    @property
    def warning_1(self):
        """ day of lifecycle for initial expiration notice"""
        return PRIOR_DAYS_NOTICE_WARNING_1

    @property
    def warning_2(self):
        """ day of lifecycle for second expiration notice"""
        return PRIOR_DAYS_NOTICE_WARNING_2

    @property
    def warning_3(self):
        """ day of lifecycle for final expiration notice"""
        return PRIOR_DAYS_NOTICE_WARNING_3

    @property
    def warning_4(self):
        """ day of lifecycle expired notice"""
        return PRIOR_DAYS_NOTICE_WARNING_4

    def days_till_expiration(self, level):
        if level == 1:
            return self.warning_1
        elif level == 2:
            return self.warning_2
        elif level == 3:
            return self.warning_3
        elif level == 4:
            return self.warning_4

        raise Exception('bad warning level {}'.format(level))

    def expiration_warning_date(self, now, level):
        days_prior = self.days_till_expiration(level)
        return now - timedelta(days=self.lifetime - days_prior)

    def expiration_date(self, now):
        return now - timedelta(days=self.graceperiod)

    def prior_warning_date(self, now, level):
        days_prior = self.days_till_expiration(level)
        prev_days_prior = self.days_till_expiration(level - 1)
        prev_warning_date = now - timedelta(days=prev_days_prior - days_prior)
        return prev_warning_date

    def additional_warning_terms(self):
        """
        service-specific query terms to include in warning/expiration queries
        """
        return {}

    def records_to_warn(self, level):
        return self.records_to_warn_on_date(timezone.now(), level)

    def records_to_warn_on_date(self, now, level):
        """
        Return query set of shared provision records to warn
        """
        return self.record_model.objects.get_records_to_warn(now, level, self)

    def records_to_expire(self):
        return self.records_to_expire_on_date(timezone.now())

    def records_to_expire_on_date(self, now):
        """
        Return query set of provision records to expire
        """
        return self.record_model.objects.get_records_to_expire(now, self)
