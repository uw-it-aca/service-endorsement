# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.db.models import Q


class RecordManagerBase(models.Manager):
    def get_records_to_warn(self, now, level, policy):
        """
        Gather provision records to receive expiration warning messages where
        level is the index of the warning message: first, second and so forth

        The expiration clock starts on the date of the first warning notice
        """
        if level < 1 or level > 4:
            raise Exception('bad warning level {}'.format(level))

        days_prior = policy.days_till_expiration(level)
        params = {
            'is_deleted__isnull': True
        }

        params.update(policy.additional_warning_terms())

        if level == 1:
            warn_date = policy.expiration_warning_date(now, level)
            params.update({
                f"{policy.datetime_provisioned_key}__lte": warn_date,
                'datetime_notice_1_emailed__isnull': True
            })
        else:
            prev_warning_date = policy.prior_warning_date(now, level)

            if level == 2:
                params.update({
                    'datetime_notice_1_emailed__lte': prev_warning_date,
                    'datetime_notice_2_emailed__isnull': True
                })
            elif level == 3:
                params.update({
                    'datetime_notice_2_emailed__lte': prev_warning_date,
                    'datetime_notice_3_emailed__isnull': True
                })
            else:
                params.update({
                    'datetime_notice_3_emailed__lte': prev_warning_date,
                    'datetime_notice_4_emailed__isnull': True
                })

        return self.filter(Q(**params))

    def get_records_to_expire(self, now, policy):
        params = {
            'datetime_notice_4_emailed__lte': policy.expiration_date(now),
            'datetime_notice_3_emailed__isnull': False,
            'datetime_notice_2_emailed__isnull': False,
            'datetime_notice_1_emailed__isnull': False,
            'is_deleted__isnull': True
        }

        params.update(policy.additional_warning_terms())

        return self.filter(Q(**params))
