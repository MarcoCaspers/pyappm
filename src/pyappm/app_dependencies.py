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

# Description:
#
# This will add or remove a dependency to the Pyappm application.
#

import sys
from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore

from simple_toml import TomlReader, TomlWriter  # type: ignore

from pyappm_tools import find_pyapp_toml  # type: ignore
from pyappm_tools import run_command  # type: ignore
from pyappm_tools import get_installed_packages  # type: ignore
from pyappm_tools import make_dependancy_cmd  # type: ignore
from pyappm_tools import get_list_diff  # type: ignore


def add_dependency(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Add a dependency to the pyapp.toml file and install it in the virtual environment."""
    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore
    if "dependencies" not in data["project"]:
        data["project"]["dependencies"] = []

    print()
    print(data["project"]["dependencies"])
    print()

    for pkg in data["project"]["dependencies"]:
        print("PKG:")
        print(pkg)
        print()
        if pkg["name"] == dep:
            print(f"{dep} is already in the dependencies.")
            return
    print("Installing dependency... (this may take a while)")
    packages = get_installed_packages(path.parent, config)
    run_command(make_dependancy_cmd(path.parent, config, "install", dep))
    new_packages = get_installed_packages(path.parent, config)
    new_deps = get_list_diff(packages, new_packages, dep)
    pkg = {"name": dep, "new_packages": new_deps}
    data["project"]["dependencies"].append(pkg)
    with TomlWriter(path) as writer:
        writer.write(data)
    print(f"Installed {dep}")


def remove_dependency(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Remove a dependency from the pyapp.toml file."""
    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore
    if "dependencies" not in data["project"]:
        print("No dependencies found.")
        sys.exit(1)
    found = None

    for pkg in data["project"]["dependencies"]:
        if pkg["name"] == dep:
            found = pkg
            break
    if not found:
        print(f"{dep} is not in the dependencies.")
        return

    print("Removing dependency... (this may take a while)")
    run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", dep))
    for pkg in found["new_packages"]:
        run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", pkg))

    data["project"]["dependencies"] = [
        pkg for pkg in data["project"]["dependencies"] if pkg["name"] != dep
    ]
    with TomlWriter(path) as writer:
        writer.write(data)

    print(f"Removed {dep}")
