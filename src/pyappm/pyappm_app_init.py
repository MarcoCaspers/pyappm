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

# This module provides the functions for the pyappm init command to initialize a new application.
#
# usage: pyappm init
# usage: pyappm init <app_name>
#
# The init command initializes a new application in the current directory or in the specified directory.
# The command creates the directory structure for the application, including the source directory, tests directory,
# docs directory, dist directory, deps directory, and build directory.

import os
from pathlib import Path
from datetime import datetime
import sys
import subprocess

from pyappm_configuration import PyAPPMConfiguration  # type: ignore

from pyappm_constants import APP_TOML  # type: ignore

from virtual_env import EnsureVirtualEnvIsNotActive  # type: ignore
from virtual_env import CreateVirtualEnv  # type: ignore

from dotdict import DotDict  # type: ignore

from pyapp_toml import CreateAppToml  # type: ignore

from pyappm_tools import run_command  # type: ignore


def check_dependencies():
    try:
        # Check if pip3 is installed
        subprocess.run(
            ["pip3", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Check if venv is installed
        subprocess.run(
            ["python3", "-m", "venv", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError:
        print("Please install pip3 and venv to continue.")
        print("To install pip3, run: sudo apt install python3-pip")
        print("To install venv, run: sudo apt install python3-venv")
        sys.exit(404)


def write_pyapp_py(path: Path, app_name: str, config: PyAPPMConfiguration) -> None:
    """Write the default <app_name>.py file to the specified path."""
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


def init_pyapp(path: str, is_service: bool, config: PyAPPMConfiguration) -> None:
    """Initialize the application in the specified directory."""
    check_dependencies()
    EnsureVirtualEnvIsNotActive()
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
    if config.create_gitignore is True:
        print("Initializing .gitignore")
        Path(pth, ".gitignore").touch()
        cmd_list = [
            "echo 'dist/' > .gitignore",
            "echo 'build/' >> .gitignore",
            "echo 'deps/' >> .gitignore",
            "echo 'env/' >> .gitignore",
            "echo '__pycache__/' >> .gitignore",
            "echo '*.pyc' >> .gitignore",
            "echo '*.pyo' >> .gitignore",
            "echo '*.pyd' >> .gitignore",
            "echo '*.egg-info' >> .gitignore",
            "echo '*.code-workspace' >> .gitignore",
            "echo '.vscode/' >> .gitignore",
            "echo '.mypy_cache/' >> .gitignore",
        ]
        for cmd in cmd_list:
            run_command(cmd)

    if config.create_init is True:
        print("Initializing __init__.py")
        Path(pth, "src", app_name, "__init__.py").touch()
    if config.create_about is True:
        print("Initializing __about__.py")
        Path(pth, "src", app_name, "__about__.py").touch()
    if config.create_typed is True:
        print("Initializing py.typed")
        Path(pth, "src", app_name, "py.typed").touch()
    if config.create_changelog is True:
        print("Initializing CHANGELOG.md")
        Path(pth, "CHANGELOG.md").touch()
        cmd = f"echo '# {app_name} Changelog' > CHANGELOG.md"
        run_command(cmd)
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
    CreateAppToml(Path(pth, APP_TOML), app_name, config, is_service)
    if config.create_venv:
        abs_path = Path(pth).resolve()
        CreateVirtualEnv(abs_path, config)
    if config.run_git_init:
        # Check if git is installed
        cmd = "git --version"
        result = run_command(cmd)
        if result.returncode != 0:
            print("Git is not installed. Skipping git init.")
        else:
            print("Running git init")
            cmd = "git init"
            run_command(cmd)
    print("Done!")
    print()


def check_if_initialized(path: str, config: PyAPPMConfiguration) -> bool:
    """Check if the application has already been initialized."""
    pth: Path
    if path == ".":
        pth = Path(os.getcwd())
    elif "~" in path:
        pth = Path(path).expanduser()
    else:
        pth = Path(path)
    return Path(pth, APP_TOML).exists()
