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

# This module contains the pyappm application initialization code.

import os
from pathlib import Path
from datetime import datetime

from configuration import PyAPPMConfiguration  # type: ignore
from pyappm_tools import ensure_no_virtual_env  # type: ignore
from pyappm_tools import APP_TOML  # type: ignore
from pyappm_tools import create_virtual_env  # type: ignore
from pyappm_tools import DotDict  # type: ignore
from simple_toml import TomlWriter  # type: ignore


def write_pyapp_py(path: Path, app_name: str, config: PyAPPMConfiguration) -> None:
    """Write the default pyapp.py file to the specified path."""
    with open(path, "w") as file:
        file.write(
            f"""# -*- coding: utf-8 -*-
# Path: src/{app_name}/{app_name}.py
# Authors: {", ".join([author["name"] for author in config.authors])}
# Email: {", ".join([author["email"] for author in config.authors])}
# License: MIT License
# Date: {datetime.now().strftime("%Y-%m-%d")}

# Description:
#
# This is the main entry point for the {app_name} application
#

def run() -> None:
    print("Hello from {app_name}!")
    
if __name__ == "__main__":
    run()

"""
        )


def write_default_pyapp_toml(
    path: Path, app_name: str, config: PyAPPMConfiguration
) -> None:
    """Write the default pyapp.toml file to the specified path."""
    authors = [
        DotDict(
            {"author": author, "email": email}
            for author, email in zip(config.authors, config.emails)
        )
    ]
    print(authors)
    print(config.dependencies)
    toml = DotDict(
        {
            "tools": DotDict(
                {
                    "env_create_tool": config.env_create_tool,
                    "env_activate_tool": config.env_activate_tool,
                    "env_deactivate_tool": config.env_deactivate_tool,
                    "env_name": config.default_env_name,
                    "env_lib_installer": config.env_lib_installer_tool,
                }
            ),
            "project": DotDict(
                {
                    "name": app_name,
                    "version": config.default_app_version,
                    "readme": "README.md",
                    "license": "LICENSE.txt",
                    "description": "",
                    "authors": authors,
                    "requires_python": config.requires_python,
                    "type": "application",
                    "dependencies": config.dependencies,
                    "local_dependencies": [],
                }
            ),
            "executable": DotDict({app_name: f"{app_name}:run"}),
        }
    )
    with TomlWriter(path) as writer:
        writer.write(toml)


def init_pyapp(path: str, config: PyAPPMConfiguration) -> None:
    """Initialize the application in the specified directory."""
    ensure_no_virtual_env()
    pth: Path
    if path == ".":
        pth = Path(os.getcwd())
    elif "~" in path:
        pth = Path(path).expanduser()
    else:
        pth = Path(path)
    app_name = pth.name
    if not pth.exists():
        pth.mkdir(parents=True, exist_ok=True)
    print(f"Initializing {app_name}")
    # Create the directory structure
    Path(pth, "src", app_name).mkdir(parents=True, exist_ok=True)
    if config.create_gitignore:
        print("Initializing .gitignore")
        Path(pth, ".gitignore").touch()
    if config.create_init:
        print("Initializing __init__.py")
        Path(pth, "src", app_name, "__init__.py").touch()
    if config.create_about:
        print("Initializing __about__.py")
        Path(pth, "src", app_name, "__about__.py").touch()
    if config.create_typed:
        print("Initializing py.typed")
        Path(pth, "src", app_name, "py.typed").touch()
    Path(pth, "tests").mkdir(exist_ok=True)
    Path(pth, "docs").mkdir(exist_ok=True)
    Path(pth, "dist").mkdir(exist_ok=True)
    Path(pth, "deps").mkdir(exist_ok=True)
    Path(pth, "build").mkdir(exist_ok=True)
    if config.create_readme:
        print("Initializing README.md")
        Path(pth, "README.md").touch()
    if config.create_license:
        print("Initializing LICENSE.txt")
        Path(pth, "LICENSE.txt").touch()
    print(f"Initializing {app_name}.py")
    write_pyapp_py(
        Path(pth, "src", app_name, f"{app_name}.py"),
        app_name,
        config,
    )
    print(f"Initializing {APP_TOML}")
    write_default_pyapp_toml(Path(pth, APP_TOML), app_name, config)
    if config.create_venv:
        abs_path = Path(pth).resolve()
        create_virtual_env(abs_path, config)
    print("Done!")
    print()
