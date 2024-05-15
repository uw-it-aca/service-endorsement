# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Loop over all shared drives verifying lifecycle and subscriptions'

    def handle(self, *args, **options):

        # for shared drives, only include members/managers that are in
        # the uw_employee group since we'll be showing managers that aren't
        # able to do anything about the subscription since their access to
        # prt will be denied.

        # query itbill status for partiular key_memote
        # only add provisions  and quanties to itbill models
        # for the given product sys_id
        # (could it be the case that the product sys_id is not unique?)

        raise Exception("Not implemented yet")
