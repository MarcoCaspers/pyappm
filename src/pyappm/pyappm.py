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

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional

from __about__ import __version__  # type: ignore

from pyappm_constants import APP_TOML  # type: ignore

from configuration import PyAPPMConfiguration  # type: ignore

from pyappm_tools import is_virtual_env_active  # type: ignore
from pyappm_tools import find_pyapp_toml
from pyappm_tools import get_arg_value
from pyappm_tools import create_apps_list
from pyappm_tools import load_toml

# Command implementations
from app_init import init_pyapp  # type: ignore
from app_init import check_if_initialized

from app_dependencies import add_dependency  # type: ignore
from app_dependencies import remove_dependency
from app_dependencies import check_if_dep_installed

from app_local_dependencies import add_local  # type: ignore
from app_local_dependencies import remove_local
from app_local_dependencies import check_if_local_dep_installed

from app_builder import build_app  # type: ignore

from app_installer import install_app  # type: ignore
from app_installer import uninstall_app
from app_installer import check_if_installed


def help() -> None:
    print(
        "Pyappm is a toolset that allows building, installing, maintaining and distributing Python applications."
    )
    print()
    print("Usage:*")
    print(
        "  pyappm init [application name]  Initialize the application (default: current directory name)"
    )
    print("  pyappm add [dependency]         Add a dependency to the application.")
    print("  pyappm remove [dependency]      Remove a dependency from the application.")
    print()
    print(
        "  pyappm install [application]    Install the application from the repository, optionally provide the version number with ==<version.number>."
    )
    print("  pyappm uninstall [application]  Uninstall the application.")
    print()
    print("  pyappm build                       Build the application.")
    print()
    print("  pyappm list                        List the installed applications.")
    print()
    print("  pyappm version, --version, -v      Show the version and exit.")
    print("  pyappm help, --help, -h, -?        Show this message and exit.")
    print()
    print(
        "* The commands also have versions with -- in front, e.g. `pyappm init` can be written as `pyappm --init`."
    )
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


def validate_args() -> None:
    for arg in sys.argv[1:]:
        if arg not in [
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
        ]:
            print(f"Invalid argument: {arg}")
            help()
            sys.exit(1)


def parse_args() -> PaAppArgs:
    """Parse the command line arguments."""
    validate_args()
    res = PaAppArgs(None, None, None, None, None, None, None, False, False, False)
    if "version" in sys.argv or "--version" in sys.argv or "-v" in sys.argv:
        print()
        print(f"Python Application Manager version: {__version__}")
        print()
        sys.exit(0)
    if (
        "help" in sys.argv
        or "--help" in sys.argv
        or "-h" in sys.argv
        or "-?" in sys.argv
    ):
        help()
        sys.exit(0)

    if "init" in sys.argv or "--init" in sys.argv:
        res.init = get_arg_value(["init", "--init"], ".")
    if "add" in sys.argv or "--add" in sys.argv or "-a" in sys.argv:
        res.add = get_arg_value(["add", "--add", "-a"])
    if "add_local" in sys.argv or "--add_local" in sys.argv:
        res.add_local = get_arg_value(["add_local", "--add_local"])
    if "remove" in sys.argv or "--remove" in sys.argv or "-r" in sys.argv:
        res.remove = get_arg_value(["remove", "--remove", "-r"])
    if "remove_local" in sys.argv or "--remove_local" in sys.argv:
        res.remove_local = get_arg_value(["remove_local", "--remove_local"])
    if "install" in sys.argv or "--install" in sys.argv or "-i" in sys.argv:
        res.install = get_arg_value(["install", "--install", "-i"])
    if "uninstall" in sys.argv or "--uninstall" in sys.argv or "-u" in sys.argv:
        res.uninstall = get_arg_value(["uninstall", "--uninstall", "-u"])
    if "build" in sys.argv or "--build" in sys.argv or "-b" in sys.argv:
        res.build = True
    if "list" in sys.argv or "--list" in sys.argv or "-l" in sys.argv:
        res.list = True
    if "deps" in sys.argv or "--deps" in sys.argv or "-d" in sys.argv:
        res.list_deps = True

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Invalid command(s).")
        help()
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
        app = load_toml(app_toml)
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

    if not is_virtual_env_active():
        print("A virtual environment is not active.")
        print("Please activate a virtual environment before removing dependencies.")
        sys.exit(1)

    toml_path = find_pyapp_toml()
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

    # if args.add_local is not None:
    #    if not validate_local(args.add_local):
    #        print(f"Invalid file: {args.add_local}, only .whl files are supported.")
    #        sys.exit(1)
    #    if check_if_local_dep_installed(toml_path, args.add_local):
    #        print(f"{args.add_local} is already installed.")
    #        sys.exit(1)
    #    return add_local(toml_path, args.add_local, config)
    #
    # if args.remove_local is not None:
    #    if not check_if_local_dep_installed(toml_path, args.remove_local):
    #        print(f"{args.remove_local} is not installed.")
    #        sys.exit(1)
    #    return remove_local(toml_path, args.remove_local, config)

    if args.list is True:
        return list_installed_apps(config)


if __name__ == "__main__":
    main()
