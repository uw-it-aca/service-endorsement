# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from os.path import abspath, dirname

from restclients_core.dao import MockDAO

MockDAO.register_mock_path(os.path.join(
    abspath(dirname(__file__)), "resources"))
