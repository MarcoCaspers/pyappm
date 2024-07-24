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
import os
import urllib.parse
from pathlib import Path
import subprocess
import sys
from typing import Optional

from simple_toml import TomlReader, TomlWriter  # type: ignore
from simple_requests import get, post, Response  # type: ignore

# It works fine this way, but mypy can't deal with it, and the solution suggested by copilot (.<module name>) will result in: ImportError: attempted relative import with no known parent package
from __about__ import __version__  # type: ignore

from configuration import PyAPPMConfiguration  # type: ignore

# Command implementations
from app_init import init_pyapp  # type: ignore
from app_dependencies import add_dependency  # type: ignore
from app_dependencies import remove_dependency  # type: ignore

from pyappm_tools import DotDict  # type: ignore
from pyappm_tools import is_virtual_env_active  # type: ignore
from pyappm_tools import find_pyapp_toml  # type: ignore
from pyappm_tools import ensure_no_virtual_env  # type: ignore
from pyappm_tools import run_command  # type: ignore
from pyappm_tools import get_installed_packages  # type: ignore
from pyappm_tools import make_dependancy_cmd  # type: ignore
from pyappm_tools import get_arg_value  # type: ignore


def help() -> None:
    print(
        "Pyapp is a toolset that allows building, installing, maintaining and distributing Python applications."
    )
    print()
    print("Usage:")
    print(
        "  pyapp init [application name]  Initialize the application (default: current directory name)"
    )
    print("  pyapp add [dependency]         Add a dependency to the application.")
    print("  pyapp remove [dependency]      Remove a dependency from the application.")
    print()
    print(
        "  pyapp install [application]    Install the application from the repository, optionally provide the version number with ==<version.number>."
    )
    print("  pyapp uninstall [application]  Uninstall the application.")
    print()
    print("  pyapp build                    Build the application.")
    print(
        "  pyapp deploy                   Deploy the application to the repository (build required)."
    )
    print()
    print("  pyapp version                  Show the version and exit.")
    print("  pyapp help                     Show this message and exit.")
    print()


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


def parse_args() -> PaAppArgs:
    """Parse the command line arguments."""
    res = PaAppArgs(None, None, None, None, None, None, None, False, False, False)
    if "version" in sys.argv or "--version" in sys.argv or "-v" in sys.argv:
        # Version is always printed, so no need to show it a second time.
        # print(f"Pyapp version: {__version__}")
        sys.exit(0)
    if "help" in sys.argv or "--help" in sys.argv or "-h" in sys.argv:
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


def load_installed_apps_list() -> list[str]:
    """Get the installed applications from the repository."""
    apps: list[str] = []
    path_to_check = Path(os.path.expanduser(APP_PATH))
    if not path_to_check.exists():
        # create the path if it doesn't exist, you should never get here, but just in case.
        path_to_check.mkdir(parents=True, exist_ok=True)
        return apps
    for app in path_to_check.iterdir():
        if app.is_dir():
            apps.append(app.name)
    return apps


def save_installed_apps_list(apps: list[str]) -> None:
    """Save the list of applications to the repository."""
    with open(Path(os.path.expanduser(APP_PATH), "apps.lst"), "w") as file:
        file.write("\n".join(apps))


def load_repo_app_list(url: str) -> list[str]:
    """Load the list of applications from the repository."""
    header = {"Accept": "application/json"}
    response = get(url=f"{url}/apps/list", headers=header)
    if response.status_code != 200:
        print(f"Failed to load the apps list from {url}")
        print(f"Status code:  {response.status_code}")
        print(f"Error detail: {response.detail}")
        return []
    return response.json().get("apps", [])


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


def validate_filename(name: str) -> str:
    """Validate the filename for use as a url node."""
    safe_name = urllib.parse.quote(name)
    return safe_name


def download_app(url: str, name: str, version: str) -> None:
    """Download an application from the repository."""
    header = {"Accept": "application/zip"}
    response: Response = get(
        url=f"{url}/apps/{name}",
        headers=header,
        params={"version": version},
    )
    if response.status_code != 200:
        print(f"Failed to download {name} from {url}")
        print(f"Status code:  {response.status_code}")
        print(f"Error detail: {response.detail}")
        sys.exit(1)
    dlpath = Path(os.path.expanduser(APP_PATH), f"{name}.pap")
    with open(dlpath, "wb") as file:
        file.write(response.data)
    run_command(f"unzip {name}.pap -d {Path(os.path.expanduser(APP_PATH), name)}")
    run_command(f"rm {name}.pap")


def install_application(name: str, config: PyAPPMConfiguration) -> None:
    """Install an application with name."""
    apps = load_installed_apps_list()
    print(f"Installing {name}... (this may take a while)")
    app_path = Path(os.path.expanduser(APP_PATH), name)
    with TomlReader(Path(app_path, "pyapp.toml")) as reader:
        data = reader.read()

    create_virtual_env(
        app_path,
        config,
        name=str(data.tools.env_name),
        ltool=data.tools.env_lib_installer,
        ctool=data.tools.env_create_tool,
    )
    for dep in data["project"]["dependencies"]:
        run_command(make_dependancy_cmd(app_path, config, "install", dep["name"]))
    apps.append(name)
    save_installed_apps_list(apps)
    print(f"Installed {name}")


def install_app(name: str, version: str, config: PyAPPMConfiguration) -> None:
    """Install an application with name."""
    if name.endswith(".pap"):
        install_local(name, config)
        return
    ensure_no_virtual_env()
    apps = load_installed_apps_list()
    if name in apps:
        print(f"{name} is already installed for this user.")
        return
    for url in config.repositories:
        print(f"Checking {url}...")
        apps = load_repo_app_list(url)
        if name in apps:
            print(f"Downloading {name}... (this may take a while)")
            download_app(url, name, version)
            install_application(name, config)
            write_executables(name, config)
            return
    print(f"{name} not found in any repository.")


def install_local(name: str, config: PyAPPMConfiguration) -> None:
    """Install an application from a local .pap file."""
    ensure_no_virtual_env()
    app_name = Path(name).stem.split("-")[0]
    apps = load_installed_apps_list()
    if app_name in apps:
        print(f"{app_name} is already installed for this user.")
        return
    app_path = Path(os.path.expanduser(config.app_dir), app_name)
    run_command(f"unzip -q {name} -d {app_path}")
    install_application(app_name, config)
    write_executables(app_name, config)


def list_installed_apps(config: PyAPPMConfiguration) -> None:
    """List the installed applications."""
    apps = config.applications
    if len(apps) == 0:
        print("No applications installed.")
        return
    print("Installed applications:")
    for app in apps:
        print(f"  {app.name} v{app.version}")


def write_executables(name: str, config: PyAPPMConfiguration) -> None:
    """Write the executable files."""
    app_path = Path(os.path.expanduser(config.app_dir), name)
    toml = TomlReader(Path(app_path, "pyapp.toml")).read()
    executables = toml.get("executable", {})
    if len(executables) == 0:
        return
    for exe, cmd in executables.items():
        path = Path(app_path, "env", "bin", exe)
        module, func = cmd.split(":")
        with open(path, "w") as file:
            file.write(
                f"""#!/bin/bash
cd {path.parent}
source activate
cd ../..
./{module}_runner $@
"""
            )
        run_command(f"chmod +x {path}")
        path = Path(app_path, f"{exe}_runner")
        with open(path, "w") as file:
            file.write(
                f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
from {module} import {func}

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit({func}())
"""
            )
        run_command(f"chmod +x {path}")


def uninstall_app(name: str, config: PyAPPMConfiguration) -> None:
    """uninstall an application with name."""
    apps = load_installed_apps_list()
    if name not in apps:
        print(f"{name} is not installed for this user.")
        return
    print(f"Uninstalling {name}... (this may take a while)")
    app_path = Path(os.path.expanduser(config.app_dir), name)
    run_command(f"cd {app_path}; python3 setup.py uninstall")
    print(f"Uninstalled {name}")


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
    if Path.exists(archive):
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
    zip_cmd_local = f"cd {Path(path.parent, 'deps')};zip -q -u -r {zip_archive}"
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
    commands.append(f"{zip_cmd_local} ./*")
    commands.append(f"{zip_cmd_parent} pyapp.toml")
    commands.append(f"{zip_cmd_parent} LICENSE.txt")
    commands.append(f"{zip_cmd_parent} README.md")
    commands.append(f"{cmd_list_files} > build/files.lst")
    commands.append(f"{zip_cmd_parent} build/files.lst")
    commands.append(f"{cmd_move_archive} dist/{path.parent.name}-{version}.pap")
    commands.append(cmd_files_list)
    for command in commands:
        run_command(command)
    print("Done!")


def add_local(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Add a local dependency to the pyapp.toml file, and install it in the virtual environment."""

    dep_path = Path(dep)

    if not dep_path.exists():
        print(f"Local dependency {dep} not found.")
        return

    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore

    if "local_dependencies" not in data["project"]:
        data["project"]["local_dependencies"] = []

    for pkg in data["project"]["local_dependencies"]:
        if pkg["name"] == dep_path.name:
            print(f"{dep_path.name} is already in the local dependencies.")
            return

    deps_file_path = Path(path.parent, "deps")

    print("Installing local dependency... (this may take a while)")
    if dep_path.resolve().parent != deps_file_path:
        # only copy the file if it's not already in the deps directory
        run_command(f"cp {dep_path.resolve()} {deps_file_path}")
    packages = get_installed_packages(path.parent, config)
    run_command(
        make_dependancy_cmd(
            path.parent, config, "install", str(Path(deps_file_path, dep_path.name))
        )
    )
    new_packages = get_installed_packages(path.parent, config)
    new_deps = get_new_packages(packages, new_packages, dep)
    pkg = {"name": dep, "new_packages": new_deps}
    data["project"]["local_dependencies"].append(pkg)
    with TomlWriter(path) as writer:
        writer.write(data)
    print(f"Installed local dependency {dep_path.name}")


def remove_local(path: Path, dep: str, config: PyAPPMConfiguration) -> None:
    """Remove a dependency from the pyapp.toml file."""
    dep_path = Path(dep)

    with TomlReader(path) as reader:
        data = reader.read()  # type: ignore

    if "local_dependencies" not in data["project"]:
        print("No dependencies found.")
        sys.exit(1)
    found = None

    for pkg in data["project"]["local_dependencies"]:
        if pkg["name"] == dep_path.name:
            found = pkg
            break
    if not found:
        print(f"{dep} is not in the local dependencies.")
        return

    print("Removing dependency... (this may take a while)")
    # run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", dep)) # this is not needed for local dependencies, the local depedency will also be in new_packages
    for pkg in found["new_packages"]:
        run_command(make_dependancy_cmd(path.parent, config, "uninstall -y", pkg))

    data["project"]["local_dependencies"] = [
        pkg
        for pkg in data["project"]["local_dependencies"]
        if pkg["name"] != dep_path.name
    ]
    with TomlWriter(path) as writer:
        writer.write(data)

    deps_path = Path(path.parent, "deps", dep_path.name)
    if deps_path.exists():
        deps_path.unlink()

    print(f"Removed {dep_path.name}")


def main() -> None:
    print(f"Pyapp version: {__version__}")
    print()
    config: PyAPPMConfiguration = load_config()

    args: PaAppArgs = parse_args()
    if args.init is not None:
        return init_pyapp(args.init, config)

    if args.install is not None:
        if "==" in args.install:
            name, version = args.install.split("==")
            version = validate_version(version)
            return install_app(name, version, config)
        return install_app(args.install, "latest", config)

    if not is_virtual_env_active():
        print("A virtual environment is not active.")
        print("Please activate a virtual environment before removing dependencies.")
        sys.exit(1)

    path = find_pyapp_toml()
    if path is None:
        print("pyapp.toml not found.")
        print("Please run `pyapp --init` to create the file.")
        sys.exit(1)

    if args.build is True:
        return build_app(path, config)

    if args.add is not None:
        return add_dependency(path, args.add, config)

    if args.remove is not None:
        return remove_dependency(path, args.remove, config)

    if args.add_local is not None:
        return add_local(path, args.add_local, config)

    if args.remove_local is not None:
        return remove_local(path, args.remove_local, config)

    if args.list is True:
        return list_installed_apps(config)


if __name__ == "__main__":
    main()
