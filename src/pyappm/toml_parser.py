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

from __future__ import annotations
from pathlib import Path
from typing import Any, Union
from toml_tokenizer import TomlToken  # type: ignore
from dotdict import DotDict  # type: ignore


class TomlParser:
    def __init__(self) -> None:
        self.data: list[TomlToken] = []
        self.index: int = 0
        self.tokens: list[TomlToken] = []

    def _parse_inner(self, tokens: list[TomlToken]) -> list[TomlToken]:
        # print()
        # print("Parsing tokens")
        self.tokens = tokens
        self.index = 0
        self.data = []
        count = len(self.tokens)
        if count == 0:
            # print("No tokens found")
            return self.data
        while self.index < count:
            token = self._parse_token(False)
            # print(token, "\n")
            if token.token_type == "EOF":
                break
            if token.token_type != "COMMENT":
                self.data.append(token)
        return self.data

    def _current(self):
        return self.tokens[self.index]

    def _next(self):
        self.index += 1
        return self.tokens[self.index]

    def _peek(self):
        return self.tokens[self.index + 1]

    def _parse_string(self) -> TomlToken:
        # print(self._current())
        self._next()  # skip quote
        start = self.index
        while self._current().token_type != "QUOTE":
            # print(self._current())
            self._next()
        # print(self._current())
        end = self.index
        value = "".join([str(token.value) for token in self.tokens[start:end]])
        self._next()  # skip quote
        # print(self._current())
        return TomlToken("STRING", value)

    def _parse_identifier(self, isvalue: bool = False) -> TomlToken:
        start = self.index
        while self._peek().token_type == "CHAR":
            self._next()
        end = self.index + 1
        value = "".join([str(token.value) for token in self.tokens[start:end]])
        token = TomlToken("IDENTIFIER", value)
        if isvalue is True and value == "True" or value == "False":
            token = TomlToken("BOOL", bool(value))
        # print(f"Parse identifier: {token}")
        self._next()  # skip the last character
        return token

    def _parse_comment(self) -> TomlToken:
        start = self.index
        while self._peek().token_type != "LF":
            self._next()
        end = self.index
        value = "".join([str(token.value) for token in self.tokens[start:end]])
        return TomlToken("COMMENT", value)

    def _is_whitespace(self) -> bool:
        return (
            self._current().token_type == "SPACE"
            or self._current().token_type == "LF"
            or self._current().token_type == "CR"
        )

    def _skip_whitespace(self) -> None:
        while self._is_whitespace():
            self._next()
        if self._current().token_type == "LF":
            self._next()
        if self._current().token_type == "CR":
            self._next()

    def _parse_key_value(self) -> TomlToken:
        # print("Parse key value")
        ident = self._parse_identifier()
        # print(f"Ident: {ident}")
        self._skip_whitespace()
        # print("skipped whitespace", self.index, self._current())
        if self._current().token_type != "EQUAL":
            raise ValueError("Expected equal sign")
        self._next()  # skip equal
        value = self._parse_token(True)
        return TomlToken("KEY_VALUE", (ident, value))

    def _parse_list(self) -> TomlToken:
        self._next()  # skip lbracket
        self._skip_whitespace()
        values = []
        while self._current().token_type != "RBRACKET":
            value = self._parse_token(True)
            values.append(value)
            self._skip_whitespace()
            if self._current().token_type == "COMMA":
                self._next()  # skip comma
                self._skip_whitespace()
                if self._current().token_type == "RBRACKET":
                    raise ValueError("Unexpected comma")
        if self._current().token_type != "RBRACKET":
            raise ValueError("Expected right bracket")
        self._next()  # skip rbracket
        return TomlToken("LIST", values)

    def _parse_dict(self) -> TomlToken:
        # print("Parse dict")
        self._next()  # skip lcurly
        self._skip_whitespace()
        values = {}
        while self._current().token_type != "RCURLY":
            key = self._parse_identifier()
            # print("KEY: ", key)
            self._skip_whitespace()
            if self._current().token_type != "EQUAL":
                raise ValueError("Expected equal sign")
            self._next()  # skip equal
            value = self._parse_token(True)

            values[key] = value
            self._skip_whitespace()
            if self._current().token_type == "COMMA":
                self._next()  # skip comma
                self._skip_whitespace()
                if self._current().token_type == "RCURLY":
                    raise ValueError("Unexpected comma")
        if self._current().token_type != "RCURLY":
            raise ValueError("Expected right curly bracket")
        self._next()  # skip rcurly
        return TomlToken("DICT", values)

    def _parse_section(self) -> TomlToken:
        self._next()  # skip lbracket
        start = self.index
        while self._next().token_type != "RBRACKET":
            pass
        end = self.index
        value = "".join([str(token.value) for token in self.tokens[start:end]])
        self._next()  # skip rbracket
        return TomlToken("SECTION", value)

    def _parse_token(self, value: bool) -> TomlToken:
        # print(f"Parse token value: {value}")
        self._skip_whitespace()
        # print("skipped whitespace", self.index, self._current())
        token = self._current()
        # print(f"Parse token: {token}")
        if token.token_type == "LBRACKET":
            if value is True:
                return self._parse_list()
            return self._parse_section()
        elif token.token_type == "CHAR":
            if value is True:
                return self._parse_identifier(True)
            return self._parse_key_value()
        elif token.token_type == "LCURLY":
            return self._parse_dict()
        elif token.token_type == "QUOTE":
            return self._parse_string()
        elif token.token_type == "COMMENT":
            return self._parse_comment()
        elif token.token_type == "EOF":
            return token
        raise ValueError(f"Unexpected token {token.token_type}")

    def __enter__(self) -> TomlParser:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Cleanup resources if needed
        pass

    def _parse_value(self, value: TomlToken) -> Any:
        if value.token_type == "STRING":
            return value.value
        if value.token_type == "IDENTIFIER":
            return value.value
        if value.token_type == "BOOL":
            return value.value
        if value.token_type == "LIST":
            if not isinstance(value.value, list):
                raise ValueError("Expected list")
            return [self._parse_value(v) for v in value.value]
        if value.token_type == "DICT":
            if not isinstance(value.value, dict):
                raise ValueError("Expected dict")
            dd = {k.value: self._parse_value(v) for k, v in value.value.items()}
            return DotDict(dd)
        raise ValueError(f"Unexpected token {value.token_type}")

    def parse(self, tokens: list[TomlToken]) -> DotDict:
        result = DotDict()
        layer = result
        rtokens = self._parse_inner(tokens)
        for token in rtokens:
            # print("Token to parse: ", token)
            if token.token_type == "SECTION":
                result[token.value] = DotDict()
                layer = result[token.value]
            elif token.token_type == "KEY_VALUE":
                if not isinstance(token.value, tuple):
                    raise ValueError("Expected tuple")
                ident, value = token.value
                key = ident.value.replace("-", "_")  # replace - with _
                layer[key] = self._parse_value(value)
            else:
                raise ValueError(f"Unexpected token {token.token_type}")
        return result
