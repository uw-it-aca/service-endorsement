from restclients_core.dao import MockDAO
import os
from os.path import abspath, dirname

MockDAO.register_mock_path(os.path.join(
    abspath(dirname(__file__)), "resources"))
