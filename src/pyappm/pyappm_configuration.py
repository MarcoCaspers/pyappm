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

from pyappm_constants import INSTALL_DIR
from pyappm_constants import BIN_DIR
from pyappm_constants import APP_DIR
from pyappm_constants import TMP_DIR
from pyappm_constants import CFG_DIR
from pyappm_constants import CONFIG_FILE_NAME

from pyappm_app_model import PyAPPMApplication

from pyappm_license_texts import MIT_LICENSE_TEXT

DEFAULT_CONFIG_CREATE_INIT = False
DEFAULT_CONFIG_CREATE_PYTYPED = False
DEFAULT_CONFIG_CREATE_GITIGNORE = False
DEFAULT_CONFIG_RUN_GIT_INIT = False

DEFAULT_CONFIG_CREATE_VENV = True
DEFAULT_CONFIG_CREATE_CHANGELOG = True
DEFAULT_CONFIG_CREATE_ABOUT = True
DEFAULT_CONFIG_CREATE_LICENSE = True
DEFAULT_CONFIG_CREATE_README = True

DEFAULT_CONFIG_LICENSE_TEXT = MIT_LICENSE_TEXT

DEFAULT_CONFIG_ENV_CREATE_TOOL = "python3 -m venv"
DEFAULT_CONFIG_ENV_ACTIVATE_TOOL = "source bin/activate"
DEFAULT_CONFIG_ENV_DEACTIVATE_TOOL = "deactivate"
DEFAULT_CONFIG_ENV_NAME = "env"
DEFAULT_CONFIG_DEFAULT_APP_TYPE = "application"
DEFAULT_CONFIG_DEFAULT_MAIN_FUNCTION_NAME = "main"
DEFAULT_CONFIG_LIB_INSTALLER_TOOL = "pip3 install"
DEFAULT_CONFIG_REQUIRE_PYTHON = ">=3.10"
DEFAULT_CONFIG_DEFAULT_APP_VERSION = "0.1.0"
DEFAULT_CONFIG_DEFAULT_DEPENDENCIES: list[str] = []


class PyAPPMConfiguration:
    def __init__(self) -> None:
        # Define the paths
        self.install_dir: Path = INSTALL_DIR
        self.config_dir: Path = CFG_DIR
        self.bin_dir: Path = BIN_DIR
        self.app_dir: Path = APP_DIR
        self.temp_dir: Path = TMP_DIR
        # ---
        self.applications: list[PyAPPMApplication] = []
        self.env_create_tool: str = DEFAULT_CONFIG_ENV_CREATE_TOOL
        self.env_activate_tool: str = DEFAULT_CONFIG_ENV_ACTIVATE_TOOL
        self.env_deactivate_tool: str = DEFAULT_CONFIG_ENV_DEACTIVATE_TOOL
        self.default_env_name: str = DEFAULT_CONFIG_ENV_NAME
        self.default_app_type: str = DEFAULT_CONFIG_DEFAULT_APP_TYPE
        self.default_main_function: str = DEFAULT_CONFIG_DEFAULT_MAIN_FUNCTION_NAME
        self.env_lib_installer_tool: str = DEFAULT_CONFIG_LIB_INSTALLER_TOOL
        self.requires_python: str = DEFAULT_CONFIG_REQUIRE_PYTHON
        self.default_app_version: str = DEFAULT_CONFIG_DEFAULT_APP_VERSION
        self.authors: list[dict[str, str]] = []
        self.dependencies: list[str] = DEFAULT_CONFIG_DEFAULT_DEPENDENCIES
        self.create_venv: bool = DEFAULT_CONFIG_CREATE_VENV
        self.create_license: bool = DEFAULT_CONFIG_CREATE_LICENSE
        self.create_readme: bool = DEFAULT_CONFIG_CREATE_README
        self.create_changelog: bool = DEFAULT_CONFIG_CREATE_CHANGELOG
        self.create_init: bool = DEFAULT_CONFIG_CREATE_INIT
        self.create_about: bool = DEFAULT_CONFIG_CREATE_ABOUT
        self.create_typed: bool = DEFAULT_CONFIG_CREATE_PYTYPED
        self.create_gitignore: bool = DEFAULT_CONFIG_CREATE_GITIGNORE
        self.run_git_init: bool = DEFAULT_CONFIG_RUN_GIT_INIT
        self.license_text: str = DEFAULT_CONFIG_LICENSE_TEXT

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
        cfg = config["pyappm"]
        self.temp_dir = Path(cfg.get("temp_dir", str(self.temp_dir)))
        self.env_create_tool = cfg.get("env_create_tool", self.env_create_tool)
        self.env_activate_tool = cfg.get("env_activate_tool", self.env_activate_tool)
        self.env_deactivate_tool = cfg.get(
            "env_deactivate_tool", self.env_deactivate_tool
        )
        self.default_env_name = cfg.get("default_env_name", self.default_env_name)
        self.default_app_type = cfg.get("default_app_type", self.default_app_type)
        self.env_lib_installer_tool = cfg.get(
            "env_lib_installer_tool", self.env_lib_installer_tool
        )
        # ---
        self.dependencies = cfg.get("dependencies", self.dependencies)
        self.requires_python = cfg.get("requires_python", self.requires_python)
        self.default_app_version = cfg.get(
            "default_app_version", self.default_app_version
        )
        self.default_app_type = cfg.get("default_app_type", self.default_app_type)
        self.default_main_function = cfg.get(
            "default_main_function", self.default_main_function
        )
        self.authors = cfg.get("authors", self.authors)
        self.create_venv = cfg.get("create_venv", self.create_venv)
        self.create_license = cfg.get("create_license", self.create_license)

        self.create_readme = cfg.get("create_readme", self.create_readme)
        self.create_init = cfg.get("create_init", self.create_init)
        self.create_about = cfg.get("create_about", self.create_about)
        self.create_typed = cfg.get("create_typed", self.create_typed)
        self.create_gitignore = cfg.get("create_gitignore", self.create_gitignore)
        self.create_changelog = cfg.get("create_changelog", self.create_changelog)
        self.run_git_init = cfg.get("run_git_init", self.run_git_init)

        # Load the applications
        for section in config.keys():
            if section == "pyappm":
                continue
            app: PyAPPMApplication = PyAPPMApplication(
                name=config[section].get("name", None),
                version=config[section].get(
                    "version", DEFAULT_CONFIG_DEFAULT_APP_VERSION
                ),
                description=config[section].get("description", None),
                readme_file=config[section].get("readme_file", "README.md"),
                license=config[section].get("license", None),
                license_file=config[section].get("license_file", "LICENSE.txt"),
                copyright=config[section].get("copyright", None),
                author=config[section].get("author", None),
                app_type=config[section].get(
                    "app_type", DEFAULT_CONFIG_DEFAULT_APP_TYPE
                ),
                module=config[section].get("module", None),
                function=config[section].get(
                    "function", DEFAULT_CONFIG_DEFAULT_MAIN_FUNCTION_NAME
                ),
                dependencies=config[section].get(
                    "dependencies", DEFAULT_CONFIG_DEFAULT_DEPENDENCIES
                ),
            )
            self.applications.append(app)

        return self

    def save(self) -> None:
        # Save the configuration
        config = DotDict()
        config["pyappm"] = DotDict(
            {
                "temp_dir": str(self.temp_dir),
                "env_create_tool": self.env_create_tool,
                "env_activate_tool": self.env_activate_tool,
                "env_deactivate_tool": self.env_deactivate_tool,
                "default_env_name": self.default_env_name,
                "default_app_type": self.default_app_type,
                "default_main_function": self.default_main_function,
                "env_lib_installer_tool": self.env_lib_installer_tool,
                "requires_python": self.requires_python,
                "default_app_version": self.default_app_version,
                "default_app_type": self.default_app_type,
                "default_main_function": self.default_main_function,
                "authors": self.authors,
                "create_venv": self.create_venv,
                "create_license": self.create_license,
                "create_readme": self.create_readme,
                "create_init": self.create_init,
                "create_about": self.create_about,
                "create_typed": self.create_typed,
                "create_gitignore": self.create_gitignore,
                "create_changelog": self.create_changelog,
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
                    "app_type": app.app_type,
                    "module": app.module,
                    "function": app.function,
                }
            )
        # Save the configuration file
        config_file = self.config_dir / CONFIG_FILE_NAME
        with TomlWriter(config_file) as file:
            file.write(config)
