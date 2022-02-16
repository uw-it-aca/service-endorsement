# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create DRF Token for a given user'

    def create_user_token(self, username, reset_token):
        user = User.objects.get_or_create(username=username[0])[0]

        if reset_token:
            Token.objects.filter(user=user).delete()

        token = Token.objects.get_or_create(user=user)
        return token[0]

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, nargs='+')

        parser.add_argument(
            '-r',
            '--reset',
            action='store_true',
            dest='reset_token',
            default=False,
            help='Reset existing User token and create a new one',
        )

    def handle(self, *args, **options):
        username = options['username']
        reset_token = options['reset_token']

        token = self.create_user_token(username, reset_token)
        self.stdout.write(
            'Generated token {0} for user {1}'.format(token.key, username))
