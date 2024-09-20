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
from pyappm_constants import PYAPP_EXT
from pyappm_constants import APP_TOML
from pyappm_constants import EX_UNSUPPORTED_APP_TYPE

from simple_requests import get  # type: ignore
from simple_requests import Response  # type: ignore

from pyappm_tools import run_command  # type: ignore
from pyappm_tools import make_dependancy_cmd
from pyappm_tools import create_apps_list


from pyapp_toml import LoadAppToml  # type: ignore

from virtual_env import CreateVirtualEnv  # type: ignore

from pyappm_configuration import PyAPPMConfiguration  # type: ignore

from pyappm_repository import PyAPPMRepositoryManager  # type: ignore


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
    name: str,
    op: str | None,
    version: str,
    repo: PyAPPMRepositoryManager,
) -> None:
    if not check_dl_cache(name):
        print(f"Downloading {name}...")
        apps = repo.find_app(name, op, version)
        if apps == []:
            print(f"App ({name}) or version ({op} {version}) not found.")
            sys.exit(1)
        app = repo.get_latest_app(apps)
        downloaded = False
        repo_url = app["repo"].url
        downloaded = download_app(
            url=repo_url, name=name, version=app["app"]["version"]
        )
        if downloaded:
            return
        print(f"Failed to download {name}")
        sys.exit(1)
    print(f"Installing {name} from cache.")


def write_executables(name: str, config: PyAPPMConfiguration) -> None:
    """Write the executable files."""
    app_path = Path(config.app_dir, name)
    toml = LoadAppToml(Path(app_path, APP_TOML))

    executables = toml.get("executable", {})
    if len(executables) == 0:
        return
    app_type = executables.get("app_type", "application")
    module = executables.get("module", toml.get("project", {}).get("name", ""))
    func = executables.get("function", "")
    if app_type == "application":
        write_application_executable(app_path, module, func, config)
    else:
        print(f"{EX_UNSUPPORTED_APP_TYPE} {app_type}")
        sys.exit(1)


def write_application_executable(
    app_path: Path, module: str, func: str, config: PyAPPMConfiguration
) -> None:
    path = Path(app_path, "env", "bin", module)
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
        run_command(f"ln -s {path} {Path(config.bin_dir, module)}")
        path = Path(app_path, f"{module}_runner")
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


def get_app_name(path: Path, config: PyAPPMConfiguration) -> str:
    """Get the application name from the local file."""
    run_command(f"unzip -j {path} {APP_TOML} -d {config.temp_dir}")
    toml = LoadAppToml(Path(config.temp_dir, APP_TOML))
    name = toml.get("project", {}).get("name", "")
    if name == "":
        print(f"Failed to get the application name from {path}")
        sys.exit(1)
    run_command(f"rm -f {Path(config.temp_dir, APP_TOML)}")
    return name


def install_app(
    name: str,
    op: str,
    version: str,
    config: PyAPPMConfiguration,
    repo: PyAPPMRepositoryManager,
) -> None:
    local = False
    if PYAPP_EXT in name:
        source_path = Path(name).resolve()
        name = get_app_name(source_path, config)
        local = True
    if local is False:
        source_path = Path(DL_CACHE, f"{name}{PYAPP_EXT}")
        get_from_repo_or_cache(name=name, op=op, version=version, repo=repo)
        if not (source_path.exists() and source_path.stat().st_size > 0):
            print(f"Failed to retrieve from cache or repository {name}")
            sys.exit(1)

    install_path = Path(config.app_dir, name)
    print(f"Installing {name}... (this may take a while)")
    # Unzip the application to the install path
    run_command(f"unzip {source_path} -d {install_path}")
    # Read the application toml file
    toml_path = Path(install_path, APP_TOML)
    data = LoadAppToml(toml_path)

    # create the virtual environment
    CreateVirtualEnv(
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
