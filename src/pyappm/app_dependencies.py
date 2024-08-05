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
# This will add or remove a dependency to a pyappm managed application
# These dependencies are installed in the virtual environment of the application using the standard pip install command
#

import sys
import subprocess

from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore

from dotdict import DotDict  # type: ignore

from pyappm_constants import SHELL_EXE  # type: ignore

from pyappm_tools import run_command  # type: ignore
from pyappm_tools import make_dependancy_cmd
from pyappm_tools import get_list_diff

from virtual_env import GetVirtualEnvInstalledPackages  # type: ignore

from pyapp_toml import LoadAppToml  # type: ignore
from pyapp_toml import SaveAppToml


def get_dep_pkg(toml: DotDict, dep: str) -> DotDict:
    """Check if a dependency is installed."""
    return next(pkg for pkg in toml["project"]["dependencies"] if pkg["name"] == dep)


def parse_dep(dep: str) -> tuple[str, str, str, bool]:
    """Parse a dependency string."""
    if ".whl" in dep:
        output = subprocess.check_output(
            f"unzip -l -q {dep} | awk 'NR>2 {{print $NF}}' | head -n -2 ",
            shell=True,
            executable=SHELL_EXE,
        ).decode("utf-8")
        files = output.split("\n")
        (info, _) = next(file.split("/") for file in files if ".dist-info" in file)
        (info, _) = info.split(".dist-info")
        (pkg_name, pkg_version, _) = info.split("-")
        return pkg_name, f"=={pkg_version}", "", True
    pkg_name = dep
    pkg_version = ""
    pkg_extra = ""
    if "[" in dep:
        pkg_name = dep.split("[")[0]
        dep = dep[len(pkg_name) :]
        i = dep.index("]")
        pkg_extra = dep[1:i]
        if i + 1 < len(dep):
            dep = dep[i + 1 :]
        else:
            dep = ""
    if ">" in dep or "=" in dep or "<" in dep:
        i = 0
        while i < len(dep) and not (dep[i] in [">", "=", "<"]):
            i += 1
        if i > 0:
            pkg_name = dep[:i]
        pkg_version = dep[i:]
    return pkg_name, pkg_version, pkg_extra, False


def check_if_dep_installed(toml_path: Path, pkg_name: str) -> bool:
    """Check if a dependency is installed."""
    toml = LoadAppToml(toml_path)
    if "dependencies" not in toml["project"]:
        return False
    return any(
        pkg["name"] == pkg_name or (".whl" in pkg["name"] and pkg_name in pkg["name"])
        for pkg in toml["project"]["dependencies"]
    )


def add_dependency(toml_path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Add a dependency to the pyapp.toml file and install it in the virtual environment."""
    toml = LoadAppToml(toml_path)
    if "dependencies" not in toml["project"]:
        toml["project"]["dependencies"] = []
    print("Installing dependency... (this may take a while)")

    pkg_path = toml_path.parent
    deps_file_path = pkg_path / "deps"
    packages = GetVirtualEnvInstalledPackages(pkg_path, config)
    dep_cmd = dep
    pkg_name, pkg_version, pkg_extra, pkg_wheel = parse_dep(dep)
    if pkg_wheel is True:
        dep_path = Path(dep).resolve()
        if dep_path.parent != deps_file_path:
            # only copy the file if it's not already in the deps directory
            run_command(f"cp {dep_path} {deps_file_path}")
        dep_cmd = str(Path(deps_file_path, dep_path.name))
    cmd = make_dependancy_cmd(pkg_path, config, "install", dep_cmd)
    run_command(cmd)
    new_packages = GetVirtualEnvInstalledPackages(pkg_path, config)

    # print(f"Checking if {pkg_name} is installed...")
    # print(f"Old packages: {packages}")
    # print(f"New packages: {new_packages}")
    # print(f"Package in new packages: {pkg_name in new_packages}")
    if not pkg_name in new_packages:
        print(f"Failed to install {pkg_name}")
        print("Trying to roll back installation (this may take a while)")
        pkgs = get_list_diff(new_packages, packages, "@@@xxx@@@")
        for pkg in pkgs:
            run_command(make_dependancy_cmd(pkg_path, config, "uninstall -y", pkg))
        return
    new_deps = get_list_diff(packages, new_packages, pkg_name)
    pkg = DotDict(
        {
            "name": pkg_name,
            "version": pkg_version,
            "extra": pkg_extra,
            "wheel": pkg_wheel,
            "new_packages": new_deps,
        }
    )
    toml["project"]["dependencies"].append(pkg)
    SaveAppToml(toml_path, toml)
    print(f"Installed {pkg_name}")


def remove_dependency(toml_path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Remove a dependency from the pyapp.toml file."""
    toml = LoadAppToml(toml_path)
    pkg = get_dep_pkg(toml, dep)
    print("Removing dependency... (this may take a while)")
    pkg_path = toml_path.parent
    rmv_pkg = pkg["name"]
    if pkg["extra"] != "":
        rmv_pkg = f"{pkg['name']}[{pkg['extra']}]"
    run_command(make_dependancy_cmd(pkg_path, config, "uninstall -y", rmv_pkg))

    for pkg in pkg["new_packages"]:
        run_command(make_dependancy_cmd(pkg_path, config, "uninstall -y", pkg))

    toml["project"]["dependencies"] = [
        DotDict(pkg) for pkg in toml["project"]["dependencies"] if pkg["name"] != dep
    ]
    SaveAppToml(toml_path, toml)
    if pkg["wheel"] is True:
        filename = f"{pkg['name']}*.whl"
        run_command(f'rm {Path(pkg_path, "deps", filename)}')
    print(f"Removed {dep}")
