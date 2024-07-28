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

#
# This module provides the functions for the pyappm app installer to install and uninstall applications.
#
# usage: pyappm install <app_name>
# usage: pyappm install <file_name.pap>
#
# usage: pyappm uninstall <app_name>
#
# The install command installs an application from a repository or a local file.
# The uninstall command uninstalls an application.
#
# A virtual environment must _not_ be active.
#

import sys
import urllib.parse
from pathlib import Path

from pyappm_constants import DL_CACHE  # type: ignore
from pyappm_constants import PYAPP_EXT  # type: ignore
from pyappm_constants import APP_TOML  # type: ignore

from simple_requests import get  # type: ignore
from simple_requests import Response  # type: ignore

from pyappm_tools import run_command  # type: ignore
from pyappm_tools import create_virtual_env  # type: ignore
from pyappm_tools import make_dependancy_cmd  # type: ignore
from pyappm_tools import create_apps_list  # type: ignore
from pyappm_tools import load_app_toml  # type: ignore
from pyappm_tools import load_toml  # type: ignore

from configuration import PyAPPMConfiguration  # type: ignore


def load_repo_app_list(url: str) -> list[str]:
    """Load the list of applications from the repository."""
    header = {"Accept": "application/json"}
    response = get(url=f"{url}/apps/list", headers=header)
    if response.status_code != 200:
        print(f"Failed to load the apps list from {url}")
        print(f"Status code:  {response.status_code}")
        print(f"Error detail: {response.detail}")
        return []
    return response.json().get("apps", [])


def download_app(url: str, name: str, version: str) -> bool:
    """Download an application from the repository."""
    header = {"Accept": "application/zip"}
    response: Response = get(
        url=f"{url}/apps/{urllib.parse.quote(name)}",
        headers=header,
        params={"version": version},
    )
    if response.status_code != 200:
        print(f"Failed to download {name} from {url}")
        print(f"Status code:  {response.status_code}")
        print(f"Error detail: {response.detail}")
        sys.exit(1)
    dlpath = Path(DL_CACHE, f"{name}{PYAPP_EXT}")
    with open(dlpath, "wb") as file:
        file.write(response.data)
    return Path(dlpath).exists() and Path(dlpath).stat().st_size > 0


def check_dl_cache(name: str) -> bool:
    """Check if the application is already in the download cache."""
    return Path(DL_CACHE, f"{name}{PYAPP_EXT}").exists()


def get_from_repo_or_cache(
    name: str, version: str, config: PyAPPMConfiguration
) -> None:
    if not check_dl_cache(name):
        print(f"Downloading {name}...")
        downloaded = False
        for url in config.repositories:
            apps = load_repo_app_list(url)
            if name in apps:
                downloaded = download_app(url=url, name=name, version=version)
                if downloaded:
                    return
                print(f"Failed to download {name}")
                sys.exit(1)
        print(f"{name} not found in the repositories.")
    print(f"Installing {name} from cache.")


def write_executables(name: str, config: PyAPPMConfiguration) -> None:
    """Write the executable files."""
    app_path = Path(config.app_dir, name)
    toml = load_toml(Path(app_path, APP_TOML))

    executables = toml.get("executable", {})
    if len(executables) == 0:
        return
    for exe, cmd in executables.items():
        path = Path(app_path, "env", "bin", exe)
        module, func = cmd.split(":")
        with open(path, "w") as file:
            file.write(
                f"""#!/bin/bash
cd {path.parent}
source activate
cd ../..
./{module}_runner $@
"""
            )
        run_command(f"chmod +x {path}")
        run_command(f"ln -s {path} {Path(config.bin_dir, exe)}")
        path = Path(app_path, f"{exe}_runner")
        with open(path, "w") as file:
            file.write(
                f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from {module} import {func}

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit({func}())
"""
            )
        run_command(f"chmod +x {path}")


def check_if_installed(name: str) -> bool:
    """Check if the application is installed."""
    if PYAPP_EXT in name:
        name = Path(name).resolve().name.replace(PYAPP_EXT, "")
    return name in create_apps_list()


def install_app(name: str, version: str, config: PyAPPMConfiguration) -> None:
    local = False
    if PYAPP_EXT in name:
        source_path = Path(name).resolve()
        name = source_path.name.replace(PYAPP_EXT, "")
        local = True
    if local is False:
        source_path = Path(DL_CACHE, f"{name}{PYAPP_EXT}")
        get_from_repo_or_cache(name, version, config)
        if not (source_path.exists() and source_path.stat().st_size > 0):
            print(f"Failed to retrieve from cache or repository {name}")
            sys.exit(1)

    install_path = Path(config.app_dir, name)
    print(f"Installing {name}... (this may take a while)")
    # Unzip the application to the install path
    run_command(f"unzip {source_path} -d {install_path}")
    # Read the application toml file
    data = load_app_toml(name)

    # create the virtual environment
    create_virtual_env(
        install_path,
        config,
        name=str(data.tools.env_name),
        ltool=data.tools.env_lib_installer,
        ctool=data.tools.env_create_tool,
    )
    # install the dependencies
    for dep in data.project.dependencies:
        run_command(make_dependancy_cmd(install_path, config, "install", dep.name))
    # write the executables
    write_executables(name, config)
    print(f"Installed {name}")


def uninstall_app(name: str, config: PyAPPMConfiguration) -> None:
    app_path = Path(config.app_dir, name)
    print(f"Uninstalling {name}... (this may take a while)")
    run_command(f"rm -rf {app_path}")  # remove the application
    run_command(f"rm -f {Path(config.bin_dir, name)}")  # remove the symlink
    print(f"Uninstalled {name}")
