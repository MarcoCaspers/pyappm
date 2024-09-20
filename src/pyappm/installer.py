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
import os

__version__ = "1.1.0"
__author__ = "Marco Caspers"
__copyright__ = "Copyright 2024 Marco Caspers"
__license__ = "MIT License"

# Define the download URL of the pyappm application for the installer to download
DOWNLOAD_URL = "https://pyappm.nl/downloads/pyappm.zip"

# Define the path to the pyappm executable
BIN_DIR = Path("~/.local/bin").expanduser()

# Define the executable name for the pyappm application
EXE_NAME = "pyappm"

# Define the path to the pyappm application
INSTALL_DIR = Path("~/.pyappm").expanduser()

# Define the path to the pyappm download cache directory
DL_CACHE = Path("~/.cache/pyappm").expanduser()

# Define the path to the pyappm configuration directory
CFG_DIR = Path("~/.config/pyappm").expanduser()

# Define the minimum Python version
MINIMUM_PYTHON_VERSION = (3, 10)

# Define the Linux/Windows dependencies
LINUX_DEPENDENCIES = ["wget", "unzip", "zip", "python3", "pip3"]
WINDOWS_DEPENDENCIES = ["wget.exe", "unzip.exe", "zip.exe"]

# Define the path to the pyappm temporary directory for the installer
TMP_DIR = Path("/tmp/pyappm")

# Define the path to the pyappm applications directory
APP_DIR = Path("~/.pyappm/share/applications").expanduser()

# Error Messages
ERR_VENV_NOT_INSTALLED = "Error: Python3 venv module is not installed!"
ERR_NOARGS = "Error: No arguments provided!"
ERR_UNKNOWN_CMD = "Error: Unknown command:"

# Messages

MSG_PLEASE_INSTALL_VENV = (
    "Please install the Python3 venv module using the following command:"
)
MSG_HOW_TO_INSTALL_VENV = "sudo apt install python3-venv"
MSG_CREATING_INSTALL_DIR = "Creating Pyappm installation directory:"
MSG_CREATING_BIN_DIR = "Creating Pyappm bin directory:"
MSG_CREATING_APP_DIR = "Creating Pyappm applications directory:"
MSG_CREATING_DL_CACHE = "Creating Pyappm download cache directory:"
MSG_CREATING_TMP_DIR = "Creating temporary download directory:"
MSG_DOWNLOADING_APP = "Downloading Pyappm application from:"
MSG_EXTRACTING_APP = "Extracting Pyappm application to:"
MSG_REMOVING_TMP_DIR = "Removing temporary download directory:"
MSG_INSTALLING_PYAPPM = "Installing Pyappm application..."
MSG_PATH_ADDED = "Added ~/.local/bin to PATH in ~/.bashrc"
MSG_RESTART_SHELL = "Please restart your shell to apply the changes."
MSG_ALT_CMD_RESTART_SHELL = "Alternatively, you can run the following command:"
MSG_SOURCE_BASHRC = "source ~/.bashrc"
MSG_INSTALLATION_COMPLETE = "Pyappm installation complete!"
MSG_USAGE = "Usage: ./installer.py [command] [options]"
MSG_COMMANDS = "Commands:"
MSG_INSTALL_COMMAND = "  install    Install the Pyappm application"
MSG_UNINSTALL_COMMAND = "  uninstall  Uninstall the Pyappm application"


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
    print(__copyright__)
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


def show_venv_help() -> None:
    print(ERR_VENV_NOT_INSTALLED)
    print(MSG_PLEASE_INSTALL_VENV)
    print(MSG_HOW_TO_INSTALL_VENV)


def check_python3_venv() -> None:
    """Check if the Python3 venv module is installed."""
    try:
        output = subprocess.check_output(
            "dpkg -l | grep python3-venv", shell=True, executable="/bin/bash"
        ).decode("utf-8")
        if output is None or output == "":
            show_venv_help()
            sys.exit(404)
    except subprocess.CalledProcessError:
        show_venv_help()
        sys.exit(404)


def setup_directories() -> None:
    """Setup the Pyapp directories."""
    if not INSTALL_DIR.exists():
        print(f"{MSG_CREATING_INSTALL_DIR} {INSTALL_DIR}")
        INSTALL_DIR.mkdir(parents=True)
    if not BIN_DIR.exists():
        print(f"{MSG_CREATING_BIN_DIR} {BIN_DIR}")
        BIN_DIR.mkdir(parents=True)
    if not APP_DIR.exists():
        print(f"{MSG_CREATING_APP_DIR} {APP_DIR}")
        APP_DIR.mkdir(parents=True)
    if not DL_CACHE.exists():
        print(f"{MSG_CREATING_DL_CACHE} {DL_CACHE}")
        DL_CACHE.mkdir(parents=True)


def rm_rf(path: Path) -> None:
    """Recursively remove a directory."""
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    elif path.exists() and path.is_file():
        path.unlink()


def download_pyapp() -> None:
    """Download the Pyappm application."""
    # Check if the temporary download directory exists
    if not TMP_DIR.exists():
        print(f"{MSG_CREATING_TMP_DIR}: {TMP_DIR}")
        TMP_DIR.mkdir(parents=True)
    # Download the Pyapp application
    print(f"{MSG_DOWNLOADING_APP} {DOWNLOAD_URL}")
    subprocess.run(
        ["wget", "-q", "--show-progress", DOWNLOAD_URL, "-O", f"{TMP_DIR}/pyapp.zip"]
    )
    # Extract the Pyapp application
    print(f"{MSG_EXTRACTING_APP} {INSTALL_DIR}")
    subprocess.run(["unzip", "-q", "-o", f"{TMP_DIR}/pyapp.zip", "-d", INSTALL_DIR])
    # Remove the temporary download directory
    print(f"{MSG_REMOVING_TMP_DIR} {TMP_DIR}")
    rm_rf(TMP_DIR)


def install_pyapp(add_bin_dir: bool) -> None:
    """Install the Pyapp application."""
    print(MSG_INSTALLING_PYAPPM)
    # perform the installation pre-requisites checks
    check_if_root_or_sudo()
    check_mimimum_python_version()
    check_dependencies()
    check_python3_venv()
    # setup the Pyapp directories
    setup_directories()

    # download the Pyapp application
    download_pyapp()

    with open(BIN_DIR / EXE_NAME, "w") as f:
        f.write(f'#!/bin/bash\n{INSTALL_DIR}/{EXE_NAME} "$@"')
    (BIN_DIR / EXE_NAME).chmod(0o755)

    if add_bin_dir and not is_bin_dir_in_path():
        add_bin_dir_to_bashrc()
        print(MSG_PATH_ADDED)
        print(MSG_RESTART_SHELL)
        print(MSG_ALT_CMD_RESTART_SHELL)
        print(MSG_SOURCE_BASHRC)

    print(MSG_INSTALLATION_COMPLETE)


def is_bin_dir_in_path() -> bool:
    """Check if ~/.local/bin is in the PATH environment variable."""
    bin_dir = os.path.expanduser("~/.local/bin")
    path = os.getenv("PATH")
    if path is None:
        return False
    return bin_dir in path.split(":")


def add_bin_dir_to_bashrc() -> None:
    """Add ~/.local/bin to .bashrc if it is not already present."""
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, "a") as f:
        f.write(f'\nexport PATH="$PATH:{BIN_DIR}"\n')


def usage() -> None:
    """Print the usage of the Pyapp installer."""
    print(MSG_USAGE)
    print(MSG_COMMANDS)
    print(MSG_INSTALL_COMMAND)
    print(MSG_UNINSTALL_COMMAND)


def main() -> None:
    """Main entry point of the Pyapp installer."""
    print_info()
    if len(sys.argv) == 1:
        print(ERR_NOARGS)
        usage()
        sys.exit(1)
    if sys.argv[1] == "install":
        add_bin_dir = True
        if "--no-path" in sys.argv:
            add_bin_dir = False
        install_pyapp(add_bin_dir)
    elif sys.argv[1] == "uninstall":
        uninstall_pyapp()
    else:
        print(f"{ERR_UNKNOWN_CMD} {sys.argv[1]}!")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
