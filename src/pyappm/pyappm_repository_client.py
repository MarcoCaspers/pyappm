#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Product:   Pyappm
# Author:    Marco Caspers
# Email:     marco@0xc007.nl
# License:   MIT License
# Date:      2024-09-11
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

# This module provides the functions for handling the pyappm repository client connection.

from pathlib import Path
from simple_requests import Session, Response  # type: ignore

BASE_URL = "https://pyappm.nl/api/v1"
# BASE_URL = "http://localhost:8000/api/v1"  # for testing


class PyappmRepositoryClient:
    def __init__(self, url: str = BASE_URL) -> None:
        self.url: str = url
        self.session = Session()

    # Don't call the below methods directly

    def _get_headers(self, token: str | None) -> dict:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _get(self, path: str, params: dict | None, token: str | None) -> Response:
        return self.session.get(
            f"{self.url}/{path}", params=params, headers=self._get_headers(token)
        )

    def _post(
        self, path: str, data: dict | None, params: dict | None, token: str | None
    ) -> Response:
        return self.session.post(
            f"{self.url}/{path}",
            data=data,
            params=params,
            headers=self._get_headers(token),
        )

    def _put(
        self, path: str, data: dict | None, params: dict | None, token: str | None
    ) -> Response:
        return self.session.put(
            f"{self.url}/{path}",
            data=data,
            params=params,
            headers=self._get_headers(token),
        )

    def _delete(
        self, path: str, data: dict | None, params: dict | None, token: str | None
    ) -> Response:
        return self.session.delete(
            f"{self.url}/{path}",
            data=data,
            params=params,
            headers=self._get_headers(token),
        )

    def _close(self) -> None:
        self.session.close()

    # below two methods are used to make the class a context manager
    # so that the session is closed when the context is exited
    # Usage:
    # with PyappmRepositoryClient("https://pyappm.nl/api/v1") as client:
    #     response = client.login()
    #

    def __enter__(self) -> "PyappmRepositoryClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._close()

    # Below are the methods that can be called by the user

    # standard authentication methods

    def login(self, username: str, password: str) -> Response:
        return self._post(
            "login",
            data={"username": username, "password": password},
            params=None,
            token=None,
        )

    def logout(self, token: str) -> Response:
        return self._get("logout", token=token, params=None)

    def register(self, email: str, password: str, password_confirm: str) -> Response:
        return self._post(
            "register",
            data={
                "email": email,
                "password": password,
                "password_confirm": password_confirm,
            },
            params=None,
            token=None,
        )

    # otp methods

    def otp_validate(self, token: str, otp: str) -> Response:
        return self._post(
            "otp/validate",
            data=None,
            params={"totp_code": otp},
            token=token,
        )

    def otp_generate(self, token: str) -> Response:
        return self._put("otp/generate-qr", token=token, params=None, data=None)

    def otp_verify(self, token: str, otp: str) -> Response:
        return self._post(
            "otp/verify",
            data=None,
            params={"totp_code": otp},
            token=token,
        )

    def otp_disable(self, token: str) -> Response:
        return self._put("otp/disable", token=token, params=None, data=None)

    # apps methods

    def apps_list(self) -> Response:
        return self._get("apps/list", token=None, params=None)

    def apps_get(self, app_id: str) -> Response:
        return self._get(f"apps/id/{app_id}", token=None, params=None)

    def apps_find(self, app: str) -> Response:
        return self._get(f"apps/find/{app}", token=None, params=None)

    # admin user functions

    def admin_user_list(self, token: str) -> Response:
        return self._get("admin/users", token=token, params=None)

    def admin_user_get(self, token: str, user_id: str) -> Response:
        return self._get(f"admin/users/{user_id}", token=token, params=None)

    def admin_user_apps(self, token: str, user_id: str) -> Response:
        return self._get(f"admin/users/{user_id}/apps", token=token, params=None)

    def authors_list(self, token: str) -> Response:
        return self._get("authors/list", token=token, params=None)
