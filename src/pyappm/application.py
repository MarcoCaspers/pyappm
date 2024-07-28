#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyapp
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

# This is the application object for a pyappm managed application


class PyAPPMApplication:
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        readme_file: str,
        license: str,
        license_file: str,
        copyright: str,
        author: str,
        dependencies: list[str] = [],
    ) -> None:
        self.name: str = name
        self.version: str = version
        self.license: str = license
        self.license_file: str = license_file
        self.copyright: str = copyright
        self.author: str = author
        self.description: str = description
        self.readme_file: str = readme_file
        self.dependencies: list[str] = dependencies

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
