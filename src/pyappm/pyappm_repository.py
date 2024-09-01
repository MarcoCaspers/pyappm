#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyappm Installer
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-08-17
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

# This module provides the functions for handling the pyappm repository.

from pathlib import Path

from simple_requests import get  # type: ignore
from simple_requests import Response

from pyappm_tools import compare_parsed_versions  # type: ignore
from pyappm_tools import parse_version

REPOSITORY_FILE = "repositories.txt"
REPOSITORY_PATH = Path(f"~/.config/pyappm/{REPOSITORY_FILE}").expanduser()

pyappm_app_version = dict[str, str]  # {"name": name, "version": version}
pyappm_repo_app_version = dict[str, pyappm_app_version]  # {"repo": repo, "app": app}


class PyAPPMRepository:
    def __init__(self, name: str, url: str) -> None:
        self.name: str = name
        self.url: str = url


DEFAULT_REPOSITORIES: list[PyAPPMRepository] = [
    PyAPPMRepository("pyappm_main", "https://pyappm.nl/repo")
]


class PyAPPMRepositoryManager:
    def __init__(self) -> None:
        self.repositories: list[PyAPPMRepository] = []
        if REPOSITORY_PATH.exists():
            self.load_repository_file(REPOSITORY_PATH)
        else:
            self.repositories = DEFAULT_REPOSITORIES
            self.save_repository_file(REPOSITORY_PATH)

    def __repo_exists__(self, name: str) -> bool:
        return any(repo.name for repo in self.repositories if repo.name == name)

    def __repo_by_name__(self, name: str) -> PyAPPMRepository:
        return next(repo for repo in self.repositories if repo.name == name)

    def __repo_get_app_list__(self, repo: PyAPPMRepository) -> list[pyappm_app_version]:
        """Load the list of applications from a repository."""
        apps: list[dict[str, str]] = []
        header = {"Accept": "application/json"}
        response: Response = get(url=f"{repo.url}/apps/list", headers=header)
        if response.status_code != 200:
            return apps
        data = response.json
        if data is None:
            return apps
        if "applications" not in data:
            return apps
        for app in data["applications"]:
            app["version"] = parse_version(app["version"])
            apps.append(app)
        return apps

    def list_repositories(self) -> None:
        """List the available repositories."""
        print("Available repositories:")
        for repo in self.repositories:
            print(f"  {repo.name}: {repo.url}")

    def add_repository(self, name: str, url: str) -> None:
        """Add a repository."""
        if self.__repo_exists__(name):
            print(f"Repository {name}: {url} already exists.")
            return
        self.repositories.append(PyAPPMRepository(name, url))
        print(f"Repository {name}: {url} added.")

    def remove_repository(self, name: str) -> None:
        """Remove a repository."""
        if not self.__repo_exists__(name):
            print(f"Repository {name} does not exist.")
            return
        repo: PyAPPMRepository = self.__repo_by_name__(name)
        self.repositories.remove(repo)
        print(f"Repository {repo.name}: {repo.url} removed.")

    def get_applications_list(self) -> list[pyappm_repo_app_version]:
        """Load the list of applications from all repositories."""
        apps: list[pyappm_repo_app_version] = []
        for repo in self.repositories:
            rapl: list[pyappm_app_version] = self.__repo_get_app_list__(repo)
            for app in rapl:
                repo_name: str = repo.name
                rap: pyappm_repo_app_version = {"repo": repo_name, "app": app}  # type: ignore
                apps.append(rap)
        return apps

    def get_app(
        self, name: str, op: str | None, version: str | None
    ) -> list[pyappm_repo_app_version]:
        """Get the application from the repository."""
        apps = self.get_applications_list()
        if op is None:
            op = "*"  # default to any version
        if version is None:
            op = "*"
        else:
            version = parse_version(version)
        return [
            app
            for app in apps
            if app["app"]["name"] == name
            and compare_parsed_versions(app["app"]["version"], op, version) is True
        ]

    def get_latest_app(
        self, app_list: list[pyappm_repo_app_version]
    ) -> pyappm_repo_app_version:
        """Get the latest version of the application."""
        latest = app_list[0]
        for app in app_list:
            if app["app"]["version"] > latest["app"]["version"]:
                latest = app
        return latest

    def load_repository_file(self, filename: Path) -> None:
        """Load the repository file."""
        with open(filename, "r") as file:
            data = file.readlines()
            for line in data:
                line = line.strip()
                if line == "":
                    continue
                if line.startswith("#"):
                    continue
                parts = line.split(" ")
                if len(parts) != 2:
                    print(f"Invalid repository line: {line}")
                    continue
                self.add_repository(parts[0], parts[1])

    def save_repository_file(self, filename: Path) -> None:
        """Save the repository file."""
        with open(filename, "w") as file:
            file.write("# PyAPPM repositories\n")
            file.write("#\n")
            file.write("# Repository name and URL\n")
            file.write("#\n")
            file.write("# Default repositories, please don't change these\n")
            file.write("#\n")
            for repo in DEFAULT_REPOSITORIES:
                file.write(f"{repo.name} {repo.url}\n")
            file.write("# End of default repositories\n")
            file.write("#\n")
            for repo in self.repositories:
                if repo in DEFAULT_REPOSITORIES:
                    continue
                file.write(f"{repo.name} {repo.url}\n")
            file.write("\n")
