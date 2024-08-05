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
# This module implements some simple pyapp.toml functions.

from pathlib import Path

from simple_toml import TomlReader, TomlWriter  # type: ignore
from dotdict import DotDict  # type: ignore

from configuration import PyAPPMConfiguration  # type: ignore


def LoadAppToml(path: Path) -> DotDict:
    """Load the toml file."""
    if path is None or not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with TomlReader(path) as reader:
        data = reader.read()
    return data


def SaveAppToml(path: Path, data: DotDict) -> None:
    """Save the toml file."""
    if path is None:
        raise ValueError("Path is None")
    with TomlWriter(path) as writer:
        writer.write(data)


def AppTomlGetDependencies(path: Path) -> list[tuple[str, str]]:
    """Read the requirements from the pyapp.toml file."""
    if path is None or not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    data = LoadAppToml(path)
    deps = data["project"]["dependencies"]
    return [(dep["name"], dep["extra"]) for dep in deps]


def CreateAppToml(path: Path, app_name: str, config: PyAPPMConfiguration) -> None:
    """Write a default pyapp.toml file to the specified path."""
    if path is not None and path.exists():
        raise FileExistsError(f"File already exists: {path}")
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
                    "authors": config.authors,
                    "requires_python": config.requires_python,
                    "type": "application",
                    "dependencies": config.dependencies,
                }
            ),
            "executable": DotDict({app_name: f"{app_name}:run"}),
        }
    )
    SaveAppToml(path, toml)


def AppTomlListDependencies(path: Path) -> None:
    """List the dependencies in the pyapp.toml file."""
    if path is None or not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    deps = AppTomlGetDependencies(path)
    print("Project dependencies:")
    for dep in deps:
        print(dep)
