#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyappm Installer
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-07-25
#
# Copyright 2024 Marco Caspers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# SPDX-License-Identifier: MIT
#

# Global constants for pyappm.

from pathlib import Path

from __about__ import __version__  # type: ignore
from __about__ import __author__  # type: ignore
from __about__ import __copyright__  # type: ignore
from __about__ import __license__  # type: ignore

from installer import BIN_DIR  # type: ignore
from installer import EXE_NAME  # type: ignore
from installer import INSTALL_DIR  # type: ignore
from installer import DL_CACHE  # type: ignore
from installer import MINIMUM_PYTHON_VERSION  # type: ignore
from installer import DOWNLOAD_URL  # type: ignore
from installer import CFG_DIR  # type: ignore
from installer import APP_DIR  # type: ignore
from installer import TMP_DIR  # type: ignore


# Define the filename of the pyappm configuration file
CONFIG_FILE_NAME = "pyappmconfig.toml"


# Define the .toml filename for applications
APP_TOML = "pyapp.toml"

SHELL_EXE = "/bin/bash"
ENV_ENVIRON = "VIRTUAL_ENV"

PYAPP_EXT = ".pap"
WHEEL_EXT = ".whl"

ERR_VENV_ACTIVE = "ERROR: A virtual environment is active."
ERR_DEACTIVATE_VENV = "Please deactivate the virtual environment and try again."

MSG_INIT_VENV = "Initializing virtual environment... (this may take a while)"
MSG_VENV_INIT_DONE = "Virtual environment initialized."
MSG_VENV_ALREADY_EXISTS = "Virtual environment already exists."
MSG_VENV_NOT_FOUND = "Virtual environment not found."

EX_FAILED_TO_LOAD_CONFIG = "Failed to load the configuration."
EX_FAILED_TO_SAVE_CONFIG = "Failed to save the configuration."
EX_FAILED_TO_LOAD_TOML = "Failed to load the application toml file."
EX_FAILED_TO_SAVE_TOML = "Failed to save the application toml file."
EX_FAILED_TO_CREATE_TOML = "Failed to create the application toml file."
EX_FAILED_TO_CREATE_APP = "Failed to create the application."
EX_FAILED_TO_CREATE_VENV = "Failed to create the virtual environment."

EX_INVALID_COMMAND = "Invalid command:"
EX_NO_COMMAND_SPECIFIED = "No command specified."
EX_INVALID_NUMBER_OF_ARGUMENTS = "Invalid invalid number of arguments specified."
EX_NO_DEP_SPECIFIED = "No dependency specified."
EX_NO_APP_SPECIFIED = "No application specified."
EX_INVALID_VENV_COMMAND = "Invalid venv command."
EX_INVALID_TOML_COMMAND = "Invalid toml command."
EX_INVALID_VERSION_STRING = "Invalid version string:"
EX_INVALID_SERVICE_OPTION = "Service option is only valid with the init command."

EX_APP_ALREADY_INITIALIZED = "Application already initialized."
EX_DEACTIVATE_VENV = "Please deactivate the virtual environment and try again."
EX_APP_ALREADY_INSTALLED = "Application already installed."
EX_APP_NOT_INSTALLED = "Application not installed."
EX_INVALID_DEPENDENCY = "Invalid dependency:"
EX_IS_ALREADY_INSTALLED = "is already installed."
EX_IS_NOT_INSTALLED = "is not installed."

EX_UNSUPPORTED_APP_TYPE = "Unsupported app_type:"

MSG_NOAPPSINSTALLED = "No applications installed."
MSG_INSTALLEDAPPS = "Installed applications:"
MSG_CREATED = "Created:"
MSG_CREATED_VENV = "Created the virtual environment."
MSG_DELETED_VENV = "Deleted the virtual environment."
MSG_VENV_NOT_ACTIVE = "A virtual environment is not active."
MSG_ACTIVATE_VENV = "Please activate a virtual environment for this application."
MSG_TOML_NOT_FOUND = "pyapp.toml not found."
MSG_CREATE_TOML = "Please run `pyapp --toml` to create the file."
MSG_VERSION = "version:"
