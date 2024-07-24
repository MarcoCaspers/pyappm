# -*- coding: utf-8 -*-
#
# Product:   Pyapp
# Author:    Marco Caspers
# Email:     SamaDevTeam@westcon.com
# License:   MIT License
# Date:      2024-06-06
#
# Copyright 2024 Westcon-Comstor
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

# UPDATE: 2024-06-22 - Marco Caspers
#   tomli library is no longer needed, we implemented TomlReader/TomlWriter
#   in src/pyapp/simple_toml.py to replace the usage of toml and tomli libraries.
#   The TomlReader/TomlWriter classes are used to read and write TOML files.
#   The DotDict class is used to represent the TOML data as a dictionary with dot notation.
#   This implementation eliminates the need to depend on 3rd party libraries for TOML parsing.
#   It also solves the problem of running pyapp with a virtual environment that does not have the toml or tomli library installed.

# This is a simple case study to investigate the usage of the tomli library.
# The case study is to read a TOML file and print the contents of the file.

# The TOML file is named pyapp.toml and is located in the root directory of the project.

# The TOML file contains the following data:
# [tools]
# env-create-tool = "venv"
# env-lib-installer = "pip"
#
# [project]
# name = "pyapp"
# description = "Pyapp is a toolset that allows building, installing, maintaining and distributing Python applications."
# authors = [
#   { name="Marco Caspers", email="SamaDevTeam@westcon.com" },
# ]
# requires-python = ">=3.9"
# dynamic = ["version", "readme", "license"]
# dependencies = [
#     "requests",
#     "tomli",
# ]
#
# [executable]
# pyapp = "pyapp:run"
#
# [dynamic]
# version = "__about__.__version__"
# readme = "__about__.__readme__"
# license = "__about__.__license__"
#
# [include]
# files=["LICENSE.txt", "README.md"]
# path="documentation"

from pydantic import BaseModel
import sys


class Author(BaseModel):
    name: str
    email: str


class VersionInfo(BaseModel):
    major: str
    minor: str
    micro: str


class PythonVersion:
    def __init__(self) -> None:
        self.versions: list[VersionInfo] = []
        self.operators: list[str] = []

    def __str__(self) -> str:
        return ",".join(
            f"{self.operator}{self.version}"
            for self.operator, self.version in zip(self.operators, self.versions)
        )

    def __repr__(self) -> str:
        return self.__str__()

    def str_to_version(self, value: str) -> VersionInfo:
        # Convert a string to a VersionInfo object
        parts = value.split(".")
        major = parts[0] if len(parts) >= 1 else ""
        minor = parts[1] if len(parts) >= 2 else ""
        micro = parts[2] if len(parts) >= 3 else ""
        return VersionInfo(major=major, minor=minor, micro=micro)

    def parse(self, value: str | None) -> None:
        # Parse the value of requires-python as described in PEP 440
        # https://peps.python.org/pep-0440/#grammar

        # Split the value into versions and operators
        if value is None:
            self.versions.append(
                VersionInfo(
                    major=str(sys.version_info.major),
                    minor=str(sys.version_info.minor),
                    micro=str(sys.version_info.micro),
                )
            )
            self.operators.append(">=")
            return
        for item in value.split(","):
            if item.startswith("=="):
                self.operators.append("==")
                self.versions.append(self.str_to_version(item[2:]))
            elif item.startswith("<="):
                self.operators.append("<=")
                self.versions.append(self.str_to_version(item[2:]))
            elif item.startswith(">="):
                self.operators.append(">=")
                self.versions.append(self.str_to_version(item[2:]))
            elif item.startswith("<"):
                self.operators.append("<")
                self.versions.append(self.str_to_version(item[1:]))
            elif item.startswith(">"):
                self.operators.append(">")
                self.versions.append(self.str_to_version(item[1:]))
            elif item.startswith("~="):
                self.operators.append("~=")
                self.versions.append(self.str_to_version(item[2:]))
            elif item.startswith("!="):
                self.operators.append("!=")
                self.versions.append(self.str_to_version(item[2:]))
            elif item.startswith("==="):
                self.operators.append("===")
                self.versions.append(self.str_to_version(item[3:]))
            else:
                raise ValueError(f"Invalid operator in requires-python: {item}")
        if not self.validate():
            raise ValueError("Invalid Python version")

    def validate(self) -> bool:
        # validate the versions and operators
        for version, operator in zip(self.versions, self.operators):
            if not eval(f"{sys.version} {operator} {version}"):
                return False
        return True


# Read the contents of the TOML file
# Ingoring type because mypy type checker is not able to correctly identify that i am opening a binary file instead of a text file.
Tomli was removed from the project and replaced with a custom implementation of TomlReader and TomlWriter
with open("pyapp.toml", "rb") as file:  # type: ignore
    project = None  # tomli.load(file)

# Print the contents of the TOML file
print(project)


env_create_tool = project.get("tools", {}).get("env-create-tool", None) or "venv"
env_lib_installer = project.get("tools", {}).get("env-lib-installer", None) or "pip"

project_name = project.get("project", {}).get("name", None)
if project_name is None:
    raise ValueError("Project name is required")

project_description = project.get("project", {}).get("description", None)
if project_description is None:
    raise ValueError("Project description is required")

project_authors = project.get("project", {}).get("authors", None)
if project_authors is None:
    raise ValueError("Project authors are required")
authors = [Author(**author) for author in project_authors]


project_requires_python = project.get("project", {}).get("requires-python", None)
versions = PythonVersion()
versions.parse(project_requires_python)

dependencies = project.get("project", {}).get("dependencies", None)

dynamic = project.get("project", {}).get("dynamic", None)

if dynamic is not None:
    for key in dynamic:
        if key not in project.get("dynamic", {}):
            raise ValueError(f"Dynamic key {key} is required")

print(f"Project name: {project_name}")
print(f"Project description: {project_description}")
print(f"Authors: {authors}")
print(f"Requires Python version: {project_requires_python}")

# Output:
# {'tools': {'env-create-tool': 'venv', 'env-lib-installer': 'pip'}, 'project': {'name': 'pyapp', 'description': 'Pyapp is a toolset that allows building, installing, maintaining and distributing Python applications.', 'authors': [{'name': 'Marco Caspers', 'email': 'SamaDevTeam@westcon.com'}], 'requires-python': '>=3.9', 'dynamic': ['version', 'readme', 'license'], 'dependencies': ['requests', 'tomli']}, 'executable': {'pyapp': 'pyapp:run'}, 'dynamic': {'version': '__about__.__version__', 'readme': '__about__.__readme__', 'license': '__about__.__license__'}, 'include': {'files': ['LICENSE.txt', 'README.md'], 'path': 'documentation'}}

# assuming Linux and Bash as the shell.
# Project name: pyapp
# I need to create a virtual environment using the venv tool and install the dependencies using the pip tool.
# I also need to activate the virtual environment using the source command.
# However i want to do this in a python script.
