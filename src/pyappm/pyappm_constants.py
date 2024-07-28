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

# Global constants for pyappm and the installer.

from pathlib import Path

from __about__ import __version__  # type: ignore
from __about__ import __author__  # type: ignore
from __about__ import __copyright__  # type: ignore
from __about__ import __license__  # type: ignore

# Define the Linux/Windows dependencies
LINUX_DEPENDENCIES = ["wget", "unzip"]
WINDOWS_DEPENDENCIES = ["wget.exe", "unzip.exe"]

# Define the minimum Python version
MINIMUM_PYTHON_VERSION = (3, 10)

# Define the download URL of the pyappm application for the installer to download
DOWNLOAD_URL = "https://pyappm.nl/downloads/pyappm.zip"

# Define the path to the pyappm temporary directory for the installer
TMP_DIR = Path("/tmp/pyappm")

# Define the path to the pyappm application
INSTALL_DIR = Path("~/.pyappm").expanduser()

# Define the path to the pyappm executable
BIN_DIR = Path("~/.local/bin").expanduser()

# Define the path to the pyappm applications directory
APP_DIR = Path("~/.pyappm/share/applications").expanduser()

# Define the path to the pyappm download cache directory
DL_CACHE = Path("~/.cache/pyappm").expanduser()

# Define the path to the pyappm configuration directory
CFG_DIR = Path("~/.config/pyappm").expanduser()

# Define the filename of the pyappm configuration file
CONFIG_FILE_NAME = "pyappmconfig.toml"

# Define the executable name for the pyappm application
EXE_NAME = "pyappm"

# Define the .toml filename for applications
APP_TOML = "pyapp.toml"

SHELL_EXE = "/bin/bash"
ENV_ENVIRON = "VIRTUAL_ENV"

REPOSITORY_URLS = ["https://pyappm.nl/repo"]
PYAPP_EXT = ".pap"

ERR_VENV_ACTIVE = "ERROR: A virtual environment is active."
ERR_DEACTIVATE_VENV = "Please deactivate the virtual environment and try again."

MSG_INIT_VENV = "Initializing virtual environment... (this may take a while)"
MSG_VENV_INIT_DONE = "Virtual environment initialized."
MSG_VENV_ALREADY_EXISTS = "Virtual environment already exists."
MSG_VENV_ACTIVATED = "Virtual environment activated."
MSG_VENV_DEACTIVATED = "Virtual environment deactivated."
MSG_VENV_NOT_FOUND = "Virtual environment not found."
