# -*- coding: utf-8 -*-
#
# Product:   Pyappm
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-06-06
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

# This module contains utility functions for pyappm.

import os
import subprocess
from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore

from pyappm_constants import APP_TOML  # type: ignore
from pyappm_constants import ENV_ENVIRON  # type: ignore

from pyappm_constants import SHELL_EXE  # type: ignore
from pyappm_constants import APP_DIR  # type: ignore

from pyapp_toml import LoadAppToml  # type: ignore
from dotdict import DotDict  # type: ignore


from virtual_env import IsVirtualEnvActive  # type: ignore


def FindAppToml() -> Path | None:
    """Find the pyapp.toml file in the current directory or its parent directories."""

    # But first check if we have a virtual environment, because that makes things a lot easier.
    # Also it means that we can use pyappm from anywhere in the filesystem, whereas without the venv, we need to be in the project directory.
    if IsVirtualEnvActive():
        current_dir = Path(os.environ[ENV_ENVIRON]).parent
        if Path(current_dir, APP_TOML).exists():
            return Path(current_dir, APP_TOML)
        return None  # We are in a virtual environment, but there is no pyapp.toml file in the parent directory.
    # At this point, we must be in the project directory.
    current_dir = Path(os.getcwd())
    while current_dir != Path.home() and current_dir != Path("/"):
        if Path(current_dir, APP_TOML).exists():
            return Path(current_dir, APP_TOML)
        current_dir = Path(current_dir).parent
    return None


def run_command(command: str) -> None:
    """Run a command in a subprocess."""
    subprocess.call(command, shell=True, executable=SHELL_EXE)


def make_dependancy_cmd(
    path: Path, config: PyAPPMConfiguration, cmd: str, dep: str
) -> str:
    """Make the installer command."""
    env_path = Path(path, config.default_env_name, "bin").resolve()
    lib_installer = config.env_lib_installer_tool
    return (
        f"cd {env_path}; source activate; {lib_installer} {cmd} {dep} > /dev/null 2>&1"
    )


def get_list_diff(
    old_packages: list[str], new_packages: list[str], dep: str
) -> list[str]:
    """Get the adittional packages that were installed.,
    The structure of a package in the toml file is as follows:
    {
        "name": str (the name of the package),
        "new_packages": list[str] (the additional packages that were installed)
    }
    """
    return [pkg for pkg in new_packages if pkg not in old_packages and pkg != dep]


def create_apps_list() -> list[str]:
    """Get the installed applications from the repository."""
    apps: list[str] = []
    path_to_check = Path(os.path.expanduser(APP_DIR))
    if not path_to_check.exists():
        # create the path if it doesn't exist, you should never get here, but just in case.
        path_to_check.mkdir(parents=True, exist_ok=True)
        return apps
    for app in path_to_check.iterdir():
        if app.is_dir():
            apps.append(app.name)
    return apps


def load_app_toml(name: str) -> DotDict:
    """Load the toml file for the application."""
    app_path = Path(APP_DIR, name)
    return LoadAppToml(Path(app_path, APP_TOML))
