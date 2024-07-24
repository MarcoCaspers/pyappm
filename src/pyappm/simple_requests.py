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
# This is a simple implementation of the requests library in Python.
# It provides a simple API to make HTTP requests using GET and POST methods.
# The Response class is used to store the response data, including the status code and response text.
# The get() and post() functions are used to make GET and POST requests, respectively.

from typing import Any
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
import json


class Response:
    def __init__(
        self,
        url: str,
        data: Any = None,
        method: str = "GET",
        headers: dict | None = None,
        timeout: float = 10.0,
        verify: bool = True,
        params: dict | None = None,
    ):
        self.url: str = url
        self.data: Any = data
        self.method: str = method
        self.headers: dict = headers if headers is not None else {}
        self.status_code: int = 500
        self.text: str = ""
        self.json: dict | None = None
        self.timeout: float = timeout
        self.verify: bool = verify
        self.params: dict | None = params
        self.raw: bytes | None = None
        self.detail: str = ""
        self._make_request()

    def _make_request(self):
        if self.data is not None:
            data = urllib.parse.urlencode(self.data).encode()
        else:
            data = None

        if self.params is not None:
            self.url += "?" + urllib.parse.urlencode(self.params)

        req = urllib.request.Request(
            self.url,
            data=data,
            method=self.method,
            headers=self.headers,
            unverifiable=not self.verify,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                self.status_code = response.status
                self.raw = response.read()
                self.headers = dict(response.headers)
                content_type = response.headers.get("Content-Type")
                if content_type:
                    if "application/json" in content_type:
                        self.data = None
                        self.text = self.raw.decode("utf-8")
                        self.json = json.loads(self.text)
                    elif content_type in ["text/plain", "text/html"]:
                        self.data = None
                        self.text = self.raw.decode("utf-8")
                        self.json = None
                    else:
                        self.data = self.raw
                        self.text = None
                        self.json = None
                else:
                    self.data = self.raw
                    self.text = None
                    self.json = None
        except HTTPError as e:
            self.status_code = e.code
            self.detail = e.reason
            self.json = None
        except URLError as e:
            self.status_code = 500
            self.detail = str(e)
            self.json = None
        except Exception as e:
            self.status_code = 500
            self.detail = f"Unhandled exception: {e}"
            self.json = None

    @property
    def has_json(self):
        return self.json is not None


def get(
    url, headers=None, params=None, verify: bool = True, timeout: float = 10.0
) -> Response:
    return Response(url, headers=headers, params=params, verify=verify, timeout=timeout)


def post(
    url,
    data=None,
    headers=None,
    params=None,
    verify: bool = True,
    timeout: float = 10.0,
) -> Response:
    return Response(
        url,
        data=data,
        method="POST",
        headers=headers,
        params=params,
        verify=verify,
        timeout=timeout,
    )


# Example usage
if __name__ == "__main__":
    # Mimicking requests.get with headers
    response = get("http://httpbin.org/get", headers={"User-Agent": "Custom"})
    print("status_code: ", response.status_code)
    print("response headers:")
    for key, value in response.headers.items():
        print(f"{key:>33}: {value}")

    if response.has_json is True:
        print()
        print("response.json:")
        for key, value in response.json.items():  # type: ignore
            print(f"{key:<10}: {value}")
    else:
        print("No JSON data")
        print("text: ", response.text)
    print()
    # Mimicking requests.post with headers
    response = post(
        "http://httpbin.org/post",
        data={"key": "value"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("status_code: ", response.status_code)
    print("response headers:")
    for key, value in response.headers.items():
        print(f"{key:>33}: {value}")
    if response.has_json is True:
        print()
        print("response.json:")
        for key, value in response.json.items():  # type: ignore
            print(f"{key:<10}: {value}")
    else:
        print("No JSON data")
        print("text: ", response.text)
    print()
