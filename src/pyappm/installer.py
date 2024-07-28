#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyappm Installer
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-07-07
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


# This is the installer script for the pyappm application

# I love MyPy.
# I HATE MyPy.

# I hate imports in Python, i love em, but i just hate em how MyPy thinks they should work.

import os
import sys
import shutil
import subprocess

from pathlib import Path

from pyappm_constants import BIN_DIR  # type: ignore
from pyappm_constants import EXE_NAME  # type: ignore
from pyappm_constants import INSTALL_DIR  # type: ignore
from pyappm_constants import DL_CACHE  # type: ignore
from pyappm_constants import CFG_DIR  # type: ignore
from pyappm_constants import __version__  # type: ignore
from pyappm_constants import __author__  # type: ignore
from pyappm_constants import __copyright__  # type: ignore
from pyappm_constants import __license__  # type: ignore
from pyappm_constants import MINIMUM_PYTHON_VERSION  # type: ignore
from pyappm_constants import LINUX_DEPENDENCIES  # type: ignore
from pyappm_constants import WINDOWS_DEPENDENCIES  # type: ignore
from pyappm_constants import DOWNLOAD_URL  # type: ignore
from pyappm_constants import TMP_DIR  # type: ignore
from pyappm_constants import APP_DIR  # type: ignore


def uninstall_pyapp() -> None:
    """Uninstall the Pyapp application."""
    print(f"Uninstalling Pyappm application")
    (BIN_DIR / EXE_NAME).unlink()
    rm_rf(INSTALL_DIR)
    rm_rf(DL_CACHE)
    rm_rf(CFG_DIR)
    print("Pyapp uninstallation complete!")


def print_info() -> None:
    """Print the Pyapp information."""
    print(f"Pyapp Installer v{__version__}")
    print()
    print(f"Author: {__author__}")
    print(f"Copyright {__copyright__}")
    print(f"License: {__license__}")
    print()


def check_if_root_or_sudo() -> None:
    """Check if the user is root or using sudo."""
    if os.getenv("SUDO_USER") is not None:
        print("Error: Do not run the installer with sudo!")
        sys.exit(1)
    if os.getuid() == 0:
        print("Error: Do not run the installer as root!")
        sys.exit(1)


def check_mimimum_python_version() -> None:
    """Check the minimum Python version."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        print(
            f"Error: Python {MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]} or higher is required to run Pyapp."
        )
        sys.exit(1)


def check_dependencies() -> None:
    """Check the system dependencies."""
    if os.name == "posix":
        print("Checking Linux system dependencies...")
        for dependency in LINUX_DEPENDENCIES:
            if shutil.which(dependency) is None:
                print(f"Error: {dependency} is required to run Pyapp.")
                sys.exit(1)
    elif os.name == "nt":
        print("Windows is not supported yet!")
        sys.exit(1)
        for dependency in WINDOWS_DEPENDENCIES:
            if shutil.which(dependency) is None:
                print(f"Error: {dependency} is required to run Pyapp.")
                sys.exit(1)
    else:
        print(f"Error: Unsupported operating system {os.name}!")
        sys.exit(1)


def setup_directories() -> None:
    """Setup the Pyapp directories."""
    if not INSTALL_DIR.exists():
        print(f"Creating Pyapp installation directory: {INSTALL_DIR}")
        INSTALL_DIR.mkdir(parents=True)
    if not BIN_DIR.exists():
        print(f"Creating Pyapp bin directory: {BIN_DIR}")
        BIN_DIR.mkdir(parents=True)
    if not APP_DIR.exists():
        print(f"Creating Pyapp applications directory: {APP_DIR}")
        APP_DIR.mkdir(parents=True)
    if not DL_CACHE.exists():
        print(f"Creating Pyapp download cache directory: {DL_CACHE}")
        DL_CACHE.mkdir(parents=True)


def rm_rf(path: Path) -> None:
    """Recursively remove a directory."""
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    elif path.exists() and path.is_file():
        path.unlink()


def download_pyapp() -> None:
    """Download the Pyapp application."""
    # Check if the temporary download directory exists
    if not TMP_DIR.exists():
        print(f"Creating temporary download directory: {TMP_DIR}")
        TMP_DIR.mkdir(parents=True)
    # Download the Pyapp application
    print(f"Downloading Pyapp application from: {DOWNLOAD_URL}")
    subprocess.run(
        ["wget", "-q", "--show-progress", DOWNLOAD_URL, "-O", f"{TMP_DIR}/pyapp.zip"]
    )
    # Extract the Pyapp application
    print(f"Extracting Pyapp application to: {INSTALL_DIR}")
    subprocess.run(["unzip", "-q", "-o", f"{TMP_DIR}/pyapp.zip", "-d", INSTALL_DIR])
    # Remove the temporary download directory
    print(f"Removing temporary download directory: {TMP_DIR}")
    rm_rf(TMP_DIR)


def install_pyapp() -> None:
    """Install the Pyapp application."""
    print(f"Installing Pyappm application")
    # perform the installation pre-requisites checks
    check_if_root_or_sudo()
    check_mimimum_python_version()
    check_dependencies()

    # setup the Pyapp directories
    setup_directories()

    # download the Pyapp application
    download_pyapp()

    with open(BIN_DIR / EXE_NAME, "w") as f:
        f.write(f'#!/bin/bash\n{INSTALL_DIR}/{EXE_NAME} "$@"')
    (BIN_DIR / EXE_NAME).chmod(0o755)
    print("Pyappm installation complete!")


def usage() -> None:
    """Print the usage of the Pyapp installer."""
    print(f"Usage: {sys.argv[0]} <command>")
    print(f"Commands:")
    print(f"  install    Install the Pyapp application")
    print(f"  uninstall  Uninstall the Pyapp application")


def main() -> None:
    """Main entry point of the Pyapp installer."""
    print_info()
    if len(sys.argv) == 1:
        print("Error: No arguments provided!")
        usage()
        sys.exit(1)
    if sys.argv[1] == "install":
        install_pyapp()
    elif sys.argv[1] == "uninstall":
        uninstall_pyapp()
    else:
        print(f"Error: Unknown command {sys.argv[1]}!")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
