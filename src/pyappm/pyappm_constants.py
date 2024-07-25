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

# All the global constants

from pathlib import Path

from __about__ import __version__  # type: ignore
from __about__ import __author__  # type: ignore
from __about__ import __copyright__  # type: ignore
from __about__ import __license__  # type: ignore

# Define the Linux/Windows dependencies
LINUX_DEPENDENCIES = ["wget", "unzip"]
WINDOWS_DEPENDENCIES = ["wget.exe", "unzip.exe"]
MINIMUM_PYTHON_VERSION = (3, 10)

DOWNLOAD_URL = "https://pyappm.nl/downloads/pyappm.zip"

INSTALL_DIR = Path("~/.pyappm").expanduser()
BIN_DIR = Path("~/.local/bin").expanduser()
APP_DIR = Path("~/.pyappm/share/applications").expanduser()
APP_BIN_DIR = Path("~/.pyappm/share/applications/bin").expanduser()

DL_CACHE = Path("~/.cache/pyappm").expanduser()
TMP_DIR = Path("/tmp/pyappm")
CFG_DIR = Path("~/.config/pyappm").expanduser()

EXE_NAME = "pyappm"

APP_LST_NAME = "apps.lst"
CONFIG_FILE_NAME = "pyappmconfig.toml"
APP_TOML = "pyapp.toml"
PYAPP_EXT = ".pap"

SHELL_EXE = "/bin/bash"
ENV_ENVIRON = "VIRTUAL_ENV"
REPOSITORY_URLS = ["https://pyappm.nl/repo"]


ERR_VENV_ACTIVE = "ERROR: A virtual environment is active."
ERR_DEACTIVATE_VENV = "Please deactivate the virtual environment and try again."

MSG_INIT_VENV = "Initializing virtual environment... (this may take a while)"
MSG_VENV_INIT_DONE = "Virtual environment initialized."
MSG_VENV_ALREADY_EXISTS = "Virtual environment already exists."
MSG_VENV_ACTIVATED = "Virtual environment activated."
MSG_VENV_DEACTIVATED = "Virtual environment deactivated."
MSG_VENV_NOT_FOUND = "Virtual environment not found."
