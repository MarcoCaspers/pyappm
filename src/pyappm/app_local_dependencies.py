# -*- coding: utf-8 -*-
#
# Product:   Pyappm
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

# Description:
#
# This will add or remove a local dependency to the pyappm managed application.
# Local dependencies are dependencies that are not available on PyPI, but are available locally on the system as a .whl file.
#

import sys
from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore

from simple_toml import TomlReader, TomlWriter  # type: ignore
from dotdict import DotDict  # type: ignore

from pyappm_tools import run_command  # type: ignore
from pyappm_tools import get_installed_packages  # type: ignore
from pyappm_tools import make_dependancy_cmd  # type: ignore
from pyappm_tools import get_list_diff  # type: ignore
from pyappm_tools import load_toml  # type: ignore
from pyappm_tools import save_toml  # type: ignore


def check_if_local_dep_installed(toml_path: Path, dep: str) -> bool:
    """Check if a local dependency is installed."""
    toml = load_toml(toml_path)
    if "local_dependencies" not in toml["project"]:
        return False

    return any(pkg["name"] == Path(dep).name for pkg in toml.project.local_dependencies)


def add_local(toml_path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Add a local dependency to the pyapp.toml file, and install it in the virtual environment."""
    toml = load_toml(toml_path)
    app_path = Path(toml_path).parent
    dep_path = Path(dep)

    if not dep_path.exists():
        print(f"Local dependency {dep} not found.")
        return

    if "local_dependencies" not in toml["project"]:
        toml["project"]["local_dependencies"] = []

    deps_file_path = Path(app_path, "deps")

    print("Installing local dependency... (this may take a while)")
    if dep_path.resolve().parent != deps_file_path:
        # only copy the file if it's not already in the deps directory
        run_command(f"cp {dep_path.resolve()} {deps_file_path}")
    packages = get_installed_packages(app_path, config)
    run_command(
        make_dependancy_cmd(
            app_path.parent, config, "install", str(Path(deps_file_path, dep_path.name))
        )
    )
    new_packages = get_installed_packages(app_path, config)
    new_deps = get_list_diff(packages, new_packages, dep)
    pkg = DotDict({"name": dep, "new_packages": new_deps})
    toml["project"]["local_dependencies"].append(pkg)
    save_toml(toml_path, toml)
    print(f"Installed local dependency {dep_path.name}")


def remove_local(toml_path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Remove a dependency from the pyapp.toml file."""
    toml = load_toml(toml_path)
    app_path = toml_path.parent
    dep_path = Path(dep)
    found = next(
        DotDict(pkg)
        for pkg in toml.project.local_dependencies
        if pkg["name"] == dep_path.name
    )

    print("Removing dependency... (this may take a while)")
    # run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", dep)) # this is not needed for local dependencies, the local depedency will also be in new_packages
    for pkg in found["new_packages"]:
        run_command(make_dependancy_cmd(app_path, config, "uninstall -y", pkg))

    toml.project.local_dependencies = [
        DotDict(pkg)
        for pkg in toml.project.local_dependencies
        if pkg["name"] != dep_path.name
    ]
    save_toml(toml_path, toml)

    deps_path = Path(app_path, "deps", dep_path.name)
    if deps_path.exists():
        deps_path.unlink()

    print(f"Removed {dep_path.name}")
