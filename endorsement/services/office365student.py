# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Defines UW Office 365 Student License service endorsement steps

To endorse O365, the tools should:
   *  Add category 291, status 1 for given endorsee
      (Office 365 Student (A5 License))
   *  Activate subscription 250 Future Office 365

Applied only to shared Category 11 netids that are endorser owned or
administrator are allowed as long as such shared netids do not have
the category: Category.ALTID_SHARED_CLINICAL_1 which are implicitly
permitted to Office 365
"""

from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription, Category


class EndorsementService(EndorsementServiceBase):
    @property
    def service_name(self):
        return 'o365student'

    @property
    def category_code(self):
        return EndorsementRecord.OFFICE_365_STUDENT_ENDORSEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_FUTURE_OFFICE_365]

    def valid_person_endorsee(self, endorsee):
        """ No personal netids can be assigned a Student License
        """
        return False

    @property
    def shared_params(self):
        """ Only shared Category 11 netids can be assigned Student License
        """
        return {
            'roles': ['owner', 'owner-admin'],
            'types': ['shared', 'support'],
            'types': ['shared'],
            'excluded_categories': [
                Category.ALTID_SHARED_CLINICAL_1]
        }

    @property
    def service_renewal_statement(self):
        return ("Data in {{ service_names_google_o365 }} "
                "account{{service_names_count|pluralize}} may be deleted.")

    @property
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/'
                'productivity-platforms/uw-office-365/')
