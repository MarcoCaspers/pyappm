# -*- coding: utf-8 -*-
#
# Product:   Pyappm
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-08-03
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

# Description:
#
# This module takes care of the virtual environment related functions.
#

import os
import sys

from pathlib import Path

from pyappm_configuration import PyAPPMConfiguration  # type: ignore

from pyappm_constants import APP_TOML  # type: ignore
from pyappm_constants import MSG_INIT_VENV  # type: ignore
from pyappm_constants import ENV_ENVIRON  # type: ignore
from pyappm_constants import ERR_VENV_ACTIVE  # type: ignore
from pyappm_constants import ERR_DEACTIVATE_VENV  # type: ignore
from pyappm_constants import SHELL_EXE  # type: ignore
from pyappm_constants import MSG_VENV_NOT_FOUND  # type: ignore
from pyappm_constants import MSG_VENV_ALREADY_EXISTS  # type: ignore

from pyapp_toml import LoadAppToml  # type: ignore
from pyapp_toml import AppTomlGetDependencies

from pyappm_tools import run_command  # type: ignore
from pyappm_tools import run_command_output  # type: ignore


def GetEnvName(path: Path, config: PyAPPMConfiguration) -> str:
    """Get the name of the virtual environment.
    Uses pyapp.toml if it exists, or uses the current directory."""
    toml_path = path / APP_TOML
    toml = None
    if toml_path.exists():
        toml = LoadAppToml(toml_path)
    name = config.default_env_name if toml is None else toml["tools"]["env_name"]
    return name


def GetVirtualEnvPath(
    path: Path, config: PyAPPMConfiguration, override: str | None = None
) -> Path:
    """Get the path to the virtual environment of the current project."""
    name = GetEnvName(path, config)
    if override is not None:
        name = override
    return Path(path, name, "bin").resolve()


def IsVirtualEnvActive() -> bool:
    return ENV_ENVIRON in os.environ


def EnsureVirtualEnvIsNotActive() -> None:
    """Ensure that a virtual environment is not active."""
    if IsVirtualEnvActive():
        print(ERR_VENV_ACTIVE)
        print(ERR_DEACTIVATE_VENV)
        sys.exit(1)


def IsVirtualEnvInstalled(path: Path, config: PyAPPMConfiguration) -> bool:
    """Check if the virtual environment is installed."""
    return GetVirtualEnvPath(path, config).exists()


def GetVirtualEnvInstalledPackages(
    path: Path, config: PyAPPMConfiguration
) -> list[str]:
    """Get the installed packages from the virtual environment of the current project."""
    if not IsVirtualEnvInstalled(path, config):
        print(MSG_VENV_NOT_FOUND)
        sys.exit(1)
    envpath = GetVirtualEnvPath(path, config)
    lib_installer = config.env_lib_installer_tool
    output = run_command_output(
        f"cd {envpath}; source activate; {lib_installer} freeze"
    )
    lst = output.split("\n")
    plst = [pkg.split("==")[0] for pkg in lst]  # remove the version number
    return [
        plst.split(" @ ")[0] for plst in plst if len(plst) > 0
    ]  # remove the bits for a file install.


def CreateVirtualEnv(
    path: Path,
    config: PyAPPMConfiguration,
    name: str | None = None,
    ctool: str | None = None,
    ltool: str | None = None,
) -> None:
    """Create a virtual environment using the configured tool."""
    if IsVirtualEnvInstalled(path, config):
        print(MSG_VENV_ALREADY_EXISTS)
        sys.exit(1)
    EnsureVirtualEnvIsNotActive()
    print(MSG_INIT_VENV)
    env_create_tool = config.env_create_tool
    if ctool is not None:
        env_create_tool = ctool
    env_name = config.default_env_name if name is None else name
    envpath = GetVirtualEnvPath(path, config, override=name)
    lib_installer = config.env_lib_installer_tool
    if ltool is not None:
        lib_installer = ltool
    commands = [
        f"cd {path}; {env_create_tool} {env_name}",
        f"cd {envpath}; source activate; {lib_installer} install --upgrade pip setuptools virtualenv> /dev/null 2>&1",
    ]
    for cmd in commands:
        run_command(cmd)


def DeleteVirtualEnv(path: Path, config: PyAPPMConfiguration) -> None:
    EnsureVirtualEnvIsNotActive()
    """Delete the virtual environment of the current project."""
    if not IsVirtualEnvInstalled(path, config):
        print(MSG_VENV_NOT_FOUND)
        sys.exit(1)
    cmd = f"rm -rf {GetVirtualEnvPath(path, config).parent}"
    run_command(cmd)


def VirtualEnvInstallDependencies(path: Path, config: PyAPPMConfiguration) -> None:
    """Install the requirements of the virtual environment."""
    if not IsVirtualEnvInstalled(path, config):
        print(MSG_VENV_NOT_FOUND)
        sys.exit(1)
    envpath = GetVirtualEnvPath(path, config)
    lib_installer = config.env_lib_installer_tool
    requirements = AppTomlGetDependencies(path / APP_TOML)
    if len(requirements) == 0:
        print("No dependencies found.")
        return
    print("Installing dependencies... (this may take a while)")
    for req in requirements:
        dep = req[0]
        if len(req[1]) > 0:
            dep = f"{dep}[{req[1]}]"
        cmd = f"cd {envpath}; source activate; {lib_installer} install {dep} > /dev/null 2>&1"
        run_command(cmd)
    print("Dependencies installed.")


def VirtualEnvListDependencies(path: Path, config: PyAPPMConfiguration) -> None:
    """List the installed packages in the virtual environment."""
    if not IsVirtualEnvInstalled(path, config):
        print(MSG_VENV_NOT_FOUND)
        sys.exit(1)
    envpath = GetVirtualEnvPath(path, config)
    lib_installer = config.env_lib_installer_tool
    output = run_command_output(
        f"cd {envpath}; source activate; {lib_installer} freeze",
    )
    if output == "":
        print("No packages installed.")
        return
    print("Installed packages:")
    print(output)
