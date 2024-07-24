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
import sys
import subprocess
from typing import Optional
from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore


ENV_ENVIRON = "VIRTUAL_ENV"
SHELL_EXE = "/bin/bash"
APP_TOML = "pyapp.toml"

ERR_VENV_ACTIVE = "ERROR: A virtual environment is active."
ERR_DEACTIVATE_VENV = "Please deactivate the virtual environment and try again."

MSG_INIT_VENV = "Initializing virtual environment... (this may take a while)"


def is_virtual_env_active() -> bool:
    return ENV_ENVIRON in os.environ


def find_pyapp_toml() -> Path | None:
    """Find the pyapp.toml file in the current directory or its parent directories."""
    current_dir = Path(os.getcwd())
    while current_dir != Path.home() and current_dir != Path("/"):
        if Path(current_dir, APP_TOML).exists():
            return Path(current_dir, APP_TOML)
        current_dir = Path(current_dir).parent
    return None


def run_command(command: str) -> None:
    """Run a command in a subprocess."""
    subprocess.call(command, shell=True, executable=SHELL_EXE)


def ensure_no_virtual_env() -> None:
    """Ensure that a virtual environment is not active."""
    if is_virtual_env_active():
        print(ERR_VENV_ACTIVE)
        print(ERR_DEACTIVATE_VENV)
        sys.exit(1)


def create_virtual_env(
    path: Path,
    config: PyAPPMConfiguration,
    name: str | None = None,
    ctool: str | None = None,
    ltool: str | None = None,
) -> None:
    """Create a virtual environment using the configured tool."""
    ensure_no_virtual_env()
    print(MSG_INIT_VENV)
    env_create_tool = config.env_create_tool
    if ctool is not None:
        env_create_tool = ctool
    env_name = config.default_env_name

    if name is not None:
        env_name = name
    env_path = Path(path, env_name, "bin").resolve()
    lib_installer = config.env_lib_installer_tool
    if ltool is not None:
        lib_installer = ltool
    commands = [
        f"cd {path}; {env_create_tool} {env_name}",
        f"cd {env_path}; source activate; {lib_installer} install --upgrade pip setuptools > /dev/null 2>&1",
    ]
    for cmd in commands:
        run_command(cmd)


class DotDict(dict):
    """A dictionary that supports dot notation access."""

    def __getattr__(self, item):
        value = self.get(item)
        if isinstance(value, DotDict):
            return value
        if isinstance(value, dict):
            return DotDict(value)
        if value is None:
            self[item] = DotDict()
            return self[item]
        return value

    def __setattr__(self, key, value):
        if key not in self:
            self[key] = None
        self[key] = value

    def __delattr__(self, item):
        del self[item]

    def __repr__(self):
        return f"DotDict({super().__repr__()})"


def get_installed_packages(path: Path, config: PyAPPMConfiguration) -> list[str]:
    """Get the installed dependencies from the virtual environment."""
    env_path = Path(path, config.default_env_name, "bin").resolve()
    lib_installer = config.env_lib_installer_tool
    output = subprocess.check_output(
        f"cd {env_path}; source activate; {lib_installer} freeze",
        shell=True,
        executable="/bin/bash",
    ).decode("utf-8")
    lst = output.split("\n")
    return [pkg.split("==")[0] for pkg in lst]


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
    """Get the new packages that were installed."""
    return [pkg for pkg in new_packages if pkg not in old_packages and pkg != dep]


def get_arg_value(args: list[str], default: Optional[str] = None) -> Optional[str]:
    """Get the offset of the argument in the list."""
    try:
        # for index, arg in enumerate(sys.argv):
        #    print(index, arg)
        argcount = len(sys.argv)
        # print("ArgCount: ", argcount)
        for arg in args:
            if not arg in sys.argv:
                continue
            # +1 for the arg itself and +1 for the value
            value_index = args.index(arg) + 2
            # print("Index: ", index)
            # print(sys.argv[index])
            if value_index >= argcount:  # if the index is out of bounds
                return default
            return sys.argv[value_index]

    except ValueError:
        return default
    return default
