# -*- coding: utf-8 -*-
#
# Product:   Pyappm
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-06-22
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

# Simple toml is a small simple utility that parses toml files and returns a dictionary
# The goal is to not being dependant on 3rd party libraries so pyapp can run without
# a vritual environment of its own.

# TomlReader Usage example:
# path = Path("path/to/your.toml")
# with TomlReader(path) as reader:
#     reader.read()
#     print(reader.tools.tool1.option)

# TomlWriter Usage example:
# path = Path("path/to/your.toml")
# with TomlWriter(path) as writer:
#     # NOTE: The data structure must be a DotDict
#     data.tool1.option = "value"
#     data.tool2.option = "value"
#     writer.write(data)

from __future__ import annotations
from typing import Any
from io import TextIOWrapper
from pathlib import Path
from toml_parser import TomlParser  # type: ignore
from toml_tokenizer import TomlTokenizer  # type: ignore
from pyappm_tools import DotDict  # type: ignore


class TomlReader:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def read(self) -> DotDict:
        data = DotDict()  # Reset the data
        with TomlTokenizer(self.file_path) as tokenizer:
            tokens = tokenizer.tokenize()
            with TomlParser() as parser:
                data = parser.parse(tokens)
        return data

    def __enter__(self) -> TomlReader:
        return self  # Return the DotDict for direct access

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Cleanup resources if needed
        pass


class TomlWriter:
    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path

    def __write_value__(self, value: Any, file: TextIOWrapper, dolf: bool) -> None:
        if isinstance(value, DotDict):
            self.__write_dict__(data=value, file=file, root=False, dolf=dolf)
        elif isinstance(value, list):
            self.__write_list__(data=value, file=file, dolf=dolf)
        elif isinstance(value, str):
            self.__write_string__(data=value, file=file, dolf=dolf)
        else:
            file.write(f"{value}")

    def __write_list__(
        self, data: list, file: TextIOWrapper, dolf: bool = True
    ) -> None:
        file.write("[")
        n = len(data) - 1  # -1 because zero based index
        for i, value in enumerate(data):
            self.__write_value__(value=value, file=file, dolf=False)
            if i < n:
                file.write(", ")
        file.write("]")
        if dolf is True:
            file.write("\n")

    def __write_dict__(
        self, data: DotDict, file: TextIOWrapper, root: bool = False, dolf: bool = True
    ) -> None:
        if not isinstance(data, DotDict):
            raise ValueError("Data must be a DotDict")
        n = len(data.keys()) - 1  # -1 because zero based index
        if root is False:
            file.write("{")
        for i, (key, value) in enumerate(data.items()):
            file.write(f"{key}=")
            self.__write_value__(value=value, file=file, dolf=False)
            if i < n and root is False:
                file.write(", ")
            if root is True:
                file.write("\n")
        if root is False:
            file.write("}")
            if dolf is True:
                file.write("\n")

    def __write_string__(
        self, data: str, file: TextIOWrapper, dolf: bool = True
    ) -> None:
        file.write(f'"{data}"')
        if dolf is True:
            file.write("\n")

    def __write_data__(self, data: DotDict, file: TextIOWrapper) -> None:
        if not isinstance(data, DotDict):
            raise ValueError("Data must be a DotDict")
        for key, value in data.items():
            if not isinstance(value, DotDict):
                raise ValueError("Value of a section must be a DotDict")
            file.write(f"[{key}]\n")
            self.__write_dict__(data=value, file=file, root=True, dolf=True)
            file.write("\n")  # blank line between sections

    def write(self, data: DotDict) -> None:
        if not isinstance(data, DotDict):
            raise ValueError("Data must be a DotDict")
        with open(self.file_path, "w") as f:
            self.__write_data__(data=data, file=f)

    def __enter__(self) -> TomlWriter:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Cleanup resources if needed
        if exc_type is not None:
            raise exc_type(exc_val)
