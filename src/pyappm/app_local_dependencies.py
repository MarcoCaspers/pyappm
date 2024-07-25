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
# This will add or remove a local dependency to the Pyappm application.
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


def add_local(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Add a local dependency to the pyapp.toml file, and install it in the virtual environment."""

    dep_path = Path(dep)

    if not dep_path.exists():
        print(f"Local dependency {dep} not found.")
        return

    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore

    if "local_dependencies" not in data["project"]:
        data["project"]["local_dependencies"] = []

    for pkg in data["project"]["local_dependencies"]:
        if pkg["name"] == dep_path.name:
            print(f"{dep_path.name} is already in the local dependencies.")
            return

    deps_file_path = Path(path.parent, "deps")

    print("Installing local dependency... (this may take a while)")
    if dep_path.resolve().parent != deps_file_path:
        # only copy the file if it's not already in the deps directory
        run_command(f"cp {dep_path.resolve()} {deps_file_path}")
    packages = get_installed_packages(path.parent, config)
    run_command(
        make_dependancy_cmd(
            path.parent, config, "install", str(Path(deps_file_path, dep_path.name))
        )
    )
    new_packages = get_installed_packages(path.parent, config)
    new_deps = get_list_diff(packages, new_packages, dep)
    pkg = DotDict({"name": dep, "new_packages": new_deps})
    data["project"]["local_dependencies"].append(pkg)
    with TomlWriter(path) as writer:
        writer.write(data)
    print(f"Installed local dependency {dep_path.name}")


def remove_local(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Remove a dependency from the pyapp.toml file."""
    dep_path = Path(dep)

    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore

    if "local_dependencies" not in data["project"]:
        print("No dependencies found.")
        sys.exit(1)
    found = None

    for pkg in data["project"]["local_dependencies"]:
        if pkg["name"] == dep_path.name:
            found = pkg
            break
    if not found:
        print(f"{dep} is not in the local dependencies.")
        return

    print("Removing dependency... (this may take a while)")
    # run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", dep)) # this is not needed for local dependencies, the local depedency will also be in new_packages
    for pkg in found["new_packages"]:
        run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", pkg))

    data["project"]["local_dependencies"] = [
        DotDict(pkg)
        for pkg in data["project"]["local_dependencies"]
        if pkg["name"] != dep_path.name
    ]
    with TomlWriter(path) as writer:
        writer.write(data)

    deps_path = Path(path.parent, "deps", dep_path.name)
    if deps_path.exists():
        deps_path.unlink()

    print(f"Removed {dep_path.name}")
