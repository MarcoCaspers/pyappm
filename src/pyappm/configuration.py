#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyappm
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-07-07
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

# This is the configuration object for the pyappm application itself.


from __future__ import annotations
from dotdict import DotDict  # type: ignore
from simple_toml import TomlReader, TomlWriter  # type: ignore
from pathlib import Path
from application import PyAPPMApplication  # type: ignore

from pyappm_constants import INSTALL_DIR  # type: ignore
from pyappm_constants import BIN_DIR  # type: ignore
from pyappm_constants import APP_DIR  # type: ignore
from pyappm_constants import TMP_DIR  # type: ignore
from pyappm_constants import CFG_DIR  # type: ignore
from pyappm_constants import REPOSITORY_URLS  # type: ignore
from pyappm_constants import CONFIG_FILE_NAME  # type: ignore


class PyAPPMConfiguration:
    def __init__(self) -> None:
        # Define the paths
        self.install_dir: Path = INSTALL_DIR
        self.config_dir: Path = CFG_DIR
        self.bin_dir: Path = BIN_DIR
        self.app_dir: Path = APP_DIR
        self.temp_dir: Path = TMP_DIR
        self.repositories: list[str] = REPOSITORY_URLS
        # ---
        self.applications: list[PyAPPMApplication] = []
        self.env_create_tool: str = "python3 -m venv"
        self.env_activate_tool: str = "source bin/activate"
        self.env_deactivate_tool: str = "deactivate"
        self.default_env_name: str = "env"
        self.default_app_type: str = "application"
        self.env_lib_installer_tool: str = "python3 -m pip"
        self.requires_python: str = ">=3.10"
        self.default_app_version: str = "0.1.0"
        self.authors: list[dict[str, str]] = []
        self.dependencies: list[str] = []
        self.create_venv: bool = True
        self.create_license: bool = True
        self.create_readme: bool = True
        self.create_init: bool = False
        self.create_about: bool = True
        self.create_typed: bool = False
        self.create_gitignore: bool = False
        self.run_git_init: bool = False

    @staticmethod
    def default() -> PyAPPMConfiguration:
        # Set the default configuration
        default = PyAPPMConfiguration()
        if not default.install_dir.exists():
            default.install_dir.mkdir(parents=True)
        if not default.config_dir.exists():
            default.config_dir.mkdir(parents=True)
        if not default.bin_dir.exists():
            default.bin_dir.mkdir(parents=True)
        if not default.app_dir.exists():
            default.app_dir.mkdir(parents=True)
        return default

    def load(self) -> PyAPPMConfiguration | None:
        # Load the configuration
        if not self.config_dir.exists():
            self.default().save()
        # Load the configuration file
        config_file = self.config_dir / CONFIG_FILE_NAME
        if not config_file.exists():
            raise ValueError("Configuration file not found")
        with TomlReader(config_file) as reader:
            config = reader.read()
        if "pyappm" not in config.keys():
            raise ValueError("Configuration file is invalid")

        # Load the configuration
        pyappm = config["pyappm"]
        self.temp_dir = Path(pyappm.get("temp_dir", str(self.temp_dir)))
        self.repositories = pyappm.get("repositories", self.repositories)
        self.env_create_tool = pyappm.get("env_create_tool", self.env_create_tool)
        self.env_activate_tool = pyappm.get("env_activate_tool", self.env_activate_tool)
        self.env_deactivate_tool = pyappm.get(
            "env_deactivate_tool", self.env_deactivate_tool
        )
        self.default_env_name = pyappm.get("default_env_name", self.default_env_name)
        self.default_app_type = pyappm.get("default_app_type", self.default_app_type)
        self.env_lib_installer_tool = pyappm.get(
            "env_lib_installer_tool", self.env_lib_installer_tool
        )
        # ---
        self.dependencies = pyappm.get("dependencies", self.dependencies)
        self.requires_python = pyappm.get("requires_python", self.requires_python)
        self.default_app_version = pyappm.get(
            "default_app_version", self.default_app_version
        )
        self.authors = pyappm.get("authors", self.authors)
        self.create_venv = pyappm.get("create_venv", self.create_venv)
        self.create_license = pyappm.get("create_license", self.create_license)

        self.create_readme = pyappm.get("create_readme", self.create_readme)
        self.create_init = pyappm.get("create_init", self.create_init)
        self.create_about = pyappm.get("create_about", self.create_about)
        self.create_typed = pyappm.get("create_typed", self.create_typed)
        self.create_gitignore = pyappm.get("create_gitignore", self.create_gitignore)
        self.run_git_init = pyappm.get("run_git_init", self.run_git_init)

        # Load the applications
        for section in config.keys():
            if section == "pyappm":
                continue
            app: PyAPPMApplication = PyAPPMApplication(
                name=config[section].get("name", None),
                version=config[section].get("version", "0.1.0"),
                description=config[section].get("description", None),
                readme_file=config[section].get("readme_file", "README.md"),
                license=config[section].get("license", None),
                license_file=config[section].get("license_file", "LICENSE.txt"),
                copyright=config[section].get("copyright", None),
                author=config[section].get("author", None),
                dependencies=config[section].get("dependencies", []),
            )
            self.applications.append(app)

        return self

    def save(self) -> None:
        # Save the configuration
        config = DotDict()
        config["pyappm"] = DotDict(
            {
                "temp_dir": str(self.temp_dir),
                "repositories": self.repositories,
                "env_create_tool": self.env_create_tool,
                "env_activate_tool": self.env_activate_tool,
                "env_deactivate_tool": self.env_deactivate_tool,
                "default_env_name": self.default_env_name,
                "env_lib_installer_tool": self.env_lib_installer_tool,
                "requires_python": self.requires_python,
                "default_app_version": self.default_app_version,
                "default_app_type": self.default_app_type,
                "authors": self.authors,
                "create_venv": self.create_venv,
                "create_license": self.create_license,
                "create_readme": self.create_readme,
                "create_init": self.create_init,
                "create_about": self.create_about,
                "create_typed": self.create_typed,
                "create_gitignore": self.create_gitignore,
                "run_git_init": self.run_git_init,
                "dependencies": self.dependencies,
            }
        )
        for app in self.applications:
            config[app.name] = DotDict(
                {
                    "name": app.name,
                    "version": app.version,
                    "description": app.description,
                    "readme_file": app.readme_file,
                    "license": app.license,
                    "license_file": app.license_file,
                    "copyright": app.copyright,
                    "author": app.author,
                    "dependencies": app.dependencies,
                }
            )
        # Save the configuration file
        config_file = self.config_dir / CONFIG_FILE_NAME
        with TomlWriter(config_file) as file:
            file.write(config)
