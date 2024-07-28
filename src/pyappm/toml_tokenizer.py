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

# Simple tokenizer for toml files
# The tokenizer is used to parse toml files and return a list of tokens


from __future__ import annotations
from pathlib import Path


class TomlToken:
    def __init__(
        self, token_type: str, value: str | tuple | list | dict | bool
    ) -> None:
        self.token_type = token_type
        self.value = value

    def __str__(self) -> str:
        return f"{self.token_type}: {self.value}"

    def __repr__(self) -> str:
        return f"{self.token_type}: {self.value}"


class TomlTokenizer:
    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise TypeError("Path must be a pathlib.Path object")
        self.path: Path = path
        self.tokens: list[TomlToken] = []

    def read_tokens(self, line: str) -> None:
        for char in line:
            if char == "=":
                self.tokens.append(TomlToken("EQUAL", char))
            elif char == "[":
                self.tokens.append(TomlToken("LBRACKET", char))
            elif char == "]":
                self.tokens.append(TomlToken("RBRACKET", char))
            elif char == "{":
                self.tokens.append(TomlToken("LCURLY", char))
            elif char == "}":
                self.tokens.append(TomlToken("RCURLY", char))
            elif char == '"' or char == "'":
                self.tokens.append(TomlToken("QUOTE", char))
            elif char == ",":
                self.tokens.append(TomlToken("COMMA", char))
            elif char == "#":
                self.tokens.append(TomlToken("COMMENT", char))
            elif char == "\n":
                self.tokens.append(TomlToken("LF", char))
            elif char == "\r":
                self.tokens.append(TomlToken("CR", char))
            elif char == " ":
                self.tokens.append(TomlToken("SPACE", char))
            else:
                self.tokens.append(TomlToken("CHAR", char))

    def tokenize(self) -> list[TomlToken]:
        with self.path.open("r") as file:
            for line in file:
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                self.read_tokens(line)
        self.tokens.append(TomlToken("EOF", ""))
        return self.tokens

    def __enter__(self) -> TomlTokenizer:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Cleanup resources if needed
        if exc_type is not None:
            raise exc_type(exc_val)
