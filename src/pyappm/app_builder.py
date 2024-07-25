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
# This will build the Pyappm application.
#

import sys
from pathlib import Path

from configuration import PyAPPMConfiguration  # type: ignore

from simple_toml import TomlReader  # type: ignore
from pyappm_tools import run_command  # type: ignore

from pyappm_constants import PYAPP_EXT  # type: ignore


def build_app(path: Path, config: PyAPPMConfiguration) -> None:
    """Build the application."""
    print("Building the application...")
    # [tools]
    # env_create_tool = "python3 -m venv"
    # env_name = "env"
    # env_lib_installer = "python3 -m pip"
    #
    # [project]
    # name = "demo"
    # version = "1.0.0"
    # readme = "README.md"
    # license = "LICENSE.txt"
    # description = ""
    # authors = [{ name="Marco Caspers", email="SamaDevTeam@Westcon.com" }]
    # requires_python = ">=3.9"
    # dependencies = []
    # local_dependencies = []
    #
    # [executable]
    # demo = "demo:run"
    #
    # [includes]
    # files = ["py.typed", ...]
    # directories = [...]
    archive = Path(path.parent, "build", f"{path.parent.name}.zip")
    if archive.exists():
        archive.unlink()
    toml = TomlReader(path).read()
    zip_archive_relative = Path("../../build", f"{path.parent.name}.zip")
    zip_archive = Path("build", f"{path.parent.name}.zip")
    source_path = Path(path.parent, "src", path.parent.name)
    commands = []
    commands.append(
        f'cd {source_path}; find . -type f \( -name "*.py" -o -name "py.typed" \) -exec zip -q {zip_archive_relative} {{}} +'
    )
    includes = toml.get("includes", {})
    files = includes.get("files", [])
    project = toml.get("project", {})
    version = project.get("version", "1.0.0")
    directories = includes.get("directories", [])
    zip_cmd_source = f"cd {source_path};zip -q -u -r {zip_archive_relative}"
    zip_cmd_parent = f"cd {path.parent};zip -q -u -r {zip_archive}"
    zip_cmd_local = f"cd {path.parent};zip -q -u -r {zip_archive}"
    zip_cmd_build = f"cd {path.parent / 'build'}; zip -q -u -r {path.parent.name}.zip"
    cmd_list_files = f"cd {path.parent};unzip -l -q {zip_archive} | awk 'NR>2 {{print $NF}}' | head -n -2"
    cmd_move_archive = f"cd {path.parent};mv {zip_archive} "
    cmd_files_list = f'cd {path.parent}; rm {Path("build", "files.lst")}'
    for file in files:
        if ".." in file:
            print(f"Invalid file path in includes: {file}")
            sys.exit(1)
        commands.append(f"{zip_cmd_source} {file}")
    for directory in directories:
        if ".." in directory:
            print(f"Invalid directory path in includes: {directory}")
            sys.exit(1)
        commands.append(f"{zip_cmd_parent} {directory}/*")
    commands.append(f"{zip_cmd_local} deps/*")
    commands.append(f"{zip_cmd_parent} pyapp.toml")
    commands.append(f"{zip_cmd_parent} LICENSE.txt")
    commands.append(f"{zip_cmd_parent} README.md")
    commands.append(f"{cmd_list_files} > build/files.lst")
    commands.append(f"{zip_cmd_build} files.lst")
    commands.append(f"{cmd_move_archive} dist/{path.parent.name}-{version}.{PYAPP_EXT}")
    commands.append(cmd_files_list)
    for command in commands:
        run_command(command)
    print(f"Built {path.parent.name}-{version}.{PYAPP_EXT}")
    print("Done!")
