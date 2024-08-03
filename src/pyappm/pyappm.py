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
# This is the main entry point for the myapp tool.

import sys
import os
from typing import Optional

from dataclasses import dataclass
from pathlib import Path


from __about__ import __version__  # type: ignore

from pyappm_constants import APP_TOML  # type: ignore

from configuration import PyAPPMConfiguration  # type: ignore

from virtual_env import IsVirtualEnvActive  # type: ignore
from virtual_env import DeleteVirtualEnv
from virtual_env import CreateVirtualEnv
from virtual_env import VirtualEnvInstallDependencies
from virtual_env import VirtualEnvListDependencies

from pyappm_tools import FindAppToml  # type: ignore
from pyappm_tools import create_apps_list

from pyapp_toml import LoadAppToml  # type: ignore
from pyapp_toml import CreateAppToml
from pyapp_toml import AppTomlListDependencies

# Command implementations
from app_init import init_pyapp  # type: ignore
from app_init import check_if_initialized

from app_dependencies import add_dependency  # type: ignore
from app_dependencies import remove_dependency
from app_dependencies import check_if_dep_installed

from app_builder import build_app  # type: ignore

from app_installer import install_app  # type: ignore
from app_installer import uninstall_app
from app_installer import check_if_installed


def help() -> None:
    """Print the help message."""
    print()
    print(
        "Python Application Manager (pyappm) is a tool to manage Python applications and their dependencies."
    )
    print()
    print("Usage: pyappm [command] [arguments]")
    print()
    print("  pyappm init [application name]     Initialize the application")
    print()
    print("  pyappm build                       Build the application")
    print()
    print("  pyappm add [dependency]            Add a dependency")
    print("  pyappm remove [dependency]         Remove a dependency")
    print()
    print("  pyappm install [application]       Install an application")
    print("  pyappm uninstall [application]     Uninstall an application")
    print()
    print("  pyappm list                        List the installed applications.")
    print()
    print("  pyappm version                     Show the version number")
    print("  pyappm help                        Show this message")

    print()
    print("  pyappm venv create                 Create a virtual environment")
    print("  pyappm venv delete                 Delete the virtual environment")
    print("  pyappm venv list                   Lists installed dependencies")
    print("  pyappm venv requirements           Installs the dependencies")
    print()
    print("  pyappm toml create                 Create a default pyapp.toml")
    print("  pyappm toml list                   List the dependencies in pyapp.toml")
    print()
    print("For more information, see the README.md file.")


@dataclass
class PaAppArgs:
    init: Optional[str]
    add: Optional[str]
    add_local: Optional[str]
    remove: Optional[str]
    remove_local: Optional[str]
    install: Optional[str]
    uninstall: Optional[str]
    build: bool = False
    list: bool = False
    list_deps: bool = False
    venv_create: bool = False
    venv_delete: bool = False
    venv_requirements: bool = False
    venv_list: bool = False
    toml_list: bool = False
    toml_create: bool = False


def validate_args() -> None:
    """Validate the command line arguments."""
    if sys.argv[1] not in [
        "help",
        "--help",
        "-h",
        "-?",
        "version",
        "--version",
        "-v",
        "init",
        "--init",
        "add",
        "--add",
        "-a",
        "add_local",
        "--add_local",
        "remove",
        "--remove",
        "-r",
        "remove_local",
        "--remove_local",
        "install",
        "--install",
        "-i",
        "uninstall",
        "--uninstall",
        "-u",
        "build",
        "--build",
        "-b",
        "list",
        "--list",
        "-l",
        "deps",
        "--deps",
        "-d",
        "venv",
        "--venv",
        "toml",
        "--toml",
    ]:
        print(f"Invalid command: {sys.argv[1]}")
        help()
        sys.exit(1)


def arg_or_default(arg: str | None, default: str | None) -> str | None:
    """Return the argument or the default value."""
    if arg is None:
        return default
    return arg


def parse_args() -> PaAppArgs:
    """Parse the command line arguments."""
    if len(sys.argv) < 2:
        print("No command specified.")
        help()
        sys.exit(1)
    if len(sys.argv) > 3:
        print("Invalid invalid number of arguments specified.")
        help()
        sys.exit(1)
    validate_args()
    res = PaAppArgs(None, None, None, None, None, None, None, False, False, False)
    cmd = sys.argv[1]
    arg = None
    if len(sys.argv) >= 3:
        arg = sys.argv[2]
    if cmd in ["version", "--version", "-v"]:
        print()
        print(f"Python Application Manager version: {__version__}")
        print()
        sys.exit(0)
    if (cmd in ["help", "--help", "-h", "-?"]) or (len(sys.argv) == 1):
        help()
        sys.exit(0)

    if cmd in ["init", "--init"]:
        res.init = arg_or_default(arg, ".")
    if cmd in ["add", "--add", "-a"]:
        if arg is None:  # pragma: no cover
            print("No dependency specified.")
            sys.exit(1)
        res.add = arg
    if cmd in ["remove", "--remove", "-r"]:
        if arg is None:
            print("No dependency specified.")
            sys.exit(1)
        res.remove = arg
    if cmd in ["install", "--install", "-i"]:
        if arg is None:
            print("No application specified.")
            sys.exit(1)
        res.install = arg
    if cmd in ["uninstall", "--uninstall", "-u"]:
        if arg is None:
            print("No application specified.")
            sys.exit(1)
        res.uninstall = arg
    if cmd in ["build", "--build", "-b"]:
        res.build = True
    if cmd in ["list", "--list", "-l"]:
        res.list = True
    if cmd in ["deps", "--deps", "-d"]:
        res.list_deps = True
    if cmd in ["venv", "--venv"]:
        if arg == "create":
            res.venv_create = True
        elif arg == "delete":
            res.venv_delete = True
        elif arg in ["requirements", "reqs", "r"]:
            res.venv_requirements = True
        elif arg == "list":
            res.venv_list = True
        else:
            print(f"Invalid venv command {arg}.")
            sys.exit(1)
    if cmd in ["toml", "--toml"]:
        if arg == "create":
            res.toml_create = True
        elif arg == "list":
            res.toml_list = True
        else:
            print(f"Invalid toml command {arg}.")
            sys.exit(1)
    return res


def load_config() -> PyAPPMConfiguration:
    """Create the configuration object and execute its load function."""
    config = PyAPPMConfiguration().load()
    return config


def validate_version(version: str) -> str:
    """Velidate the version string for use as a url parameter."""
    v: list = []
    l = len(version)
    i = 0
    while i < l:
        if version[i].isdigit():
            start = i
            while i < l and version[i].isdigit():
                i += 1
            v.append(version[start:i])
        if version[i] == ".":
            v.append(".")
        if version[i].isalpha():
            start = i
            while i < l and version[i].isalpha():
                i += 1
            v.append(version[start:i])
        else:
            print(f"Invalid version string: {version}")
            sys.exit(1)
        i += 1
    for part in v:
        if part.isalpha():
            if (
                part != "a"
                and part != "b"
                and part != "rc"
                and part != "dev"
                and part != "latest"
            ):
                print(f"Invalid version string: {version}")
                sys.exit(1)
        elif part == ".":
            continue
        elif not part.isdigit():
            print(f"Invalid version string: {version}")
            sys.exit(1)

    return version


def list_installed_apps(config: PyAPPMConfiguration) -> None:
    """List the installed applications."""
    apps = create_apps_list()
    if len(apps) == 0:
        print("No applications installed.")
        return
    print("Installed applications:")
    for app in apps:
        app_path = config.app_dir / app
        app_toml = app_path / APP_TOML
        app = LoadAppToml(app_toml)
        print(f"  {app.project.name} v{app.project.version}")


def validate_local(dep: str) -> bool:
    """Validate the local dependency file."""
    dep_path = Path(dep)
    if not Path(dep).exists():
        return False
    if not dep_path.is_file():
        return False
    if dep_path.suffix != ".whl":
        return False
    return True


def main() -> None:
    config: PyAPPMConfiguration = load_config()

    args: PaAppArgs = parse_args()
    if args.init is not None:
        if check_if_initialized(args.init, config):
            print("Application already initialized.")
            sys.exit(1)
        return init_pyapp(args.init, config)

    if args.install is not None:
        if IsVirtualEnvActive():
            print(
                "Please deactivate the virtual environment before installing an application."
            )
            sys.exit(1)
        version = "latest"
        name = args.install
        if "==" in args.install:
            name, version = args.install.split("==")
            version = validate_version(version)
        if check_if_installed(name):
            print(f"{name} is already installed.")
            sys.exit(1)
        return install_app(name, version, config)

    if args.uninstall is not None:
        if not check_if_installed(args.uninstall):
            print(f"{args.uninstall} is not installed.")
            sys.exit(1)
        return uninstall_app(args.uninstall, config)

    toml_path = FindAppToml()
    venv_root_path = Path(os.getcwd()) if toml_path is None else toml_path.parent

    if args.toml_create is True:
        toml_path = Path(os.getcwd()) / APP_TOML
        app_name = Path(os.getcwd()).name
        CreateAppToml(toml_path, app_name, config)
        print(f"Created {APP_TOML}")
        return

    if args.venv_delete is True:
        DeleteVirtualEnv(venv_root_path, config)
        print("Deleted the virtual environment.")
        return

    if args.venv_create is True:
        CreateVirtualEnv(venv_root_path, config)
        print("Created the virtual environment.")
        return

    if args.venv_requirements is True:
        return VirtualEnvInstallDependencies(venv_root_path, config)

    if args.venv_list is True:
        return VirtualEnvListDependencies(venv_root_path, config)

    if args.toml_list is True:
        return AppTomlListDependencies(toml_path)

    if not IsVirtualEnvActive():
        print("A virtual environment is not active.")
        print("Please activate a virtual environment before removing dependencies.")
        sys.exit(1)

    if toml_path is None:
        print("pyapp.toml not found.")
        print("Please run `pyapp --init` to create the file.")
        sys.exit(1)

    if args.build is True:
        return build_app(toml_path, config)

    if args.add is not None:
        if Path(args.add).is_file() and not validate_local(args.add):
            print(f"Invalid dependency: {args.add}")
            sys.exit(1)
        if check_if_dep_installed(toml_path, args.add):
            print(f"{args.add} is already installed.")
            sys.exit(1)
        return add_dependency(toml_path, args.add, config)

    if args.remove is not None:
        if not check_if_dep_installed(toml_path, args.remove):
            print(f"{args.remove} is not installed.")
            sys.exit(1)
        return remove_dependency(toml_path, args.remove, config)

    if args.list is True:
        return list_installed_apps(config)


if __name__ == "__main__":
    main()
