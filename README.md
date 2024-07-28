#pyappm

## Description

This is an easy to use command line tool to manage your Python applications.<br>

NOTE:<br>
This is a work in progress and not yet ready for production use.<br>
DO NOT run the installer as root.<br><br>

## Features

- Install applications from a repository
- Install applications from a file
- Uninstall applications
- List installed applications<br>
- Initialize a new application project
- Build an application
- Add an dependency to an application (from PyPi)
- Add an dependency to an application (from a file)
- Remove a dependency from an application<br><br>

## Roadmap

- Add an application to a repository
- Remove an application from a repository
- Use versioning for application installation
- Update an application
- A repository for applications<br><br>

## Pre-requisites

- Python 3.10 or higher
- wget
- unzip<br><br>

## Installation

```bash
wget https://pyappm.nl/downloads/installer.py -O - | python3
```  

<br>

## Usage

```text
Usage: pyappm [options] [command]

pyappm init, --init [<name>]                            Initialize a new application project
pyappm build, --build, -b                               Build the application

pyappm install, --install, -i [<name>||<file.pap>]      Install an application from a repository or a local file
pyappm uninstall, --uninstall, -u <name>                Uninstall an application

pyappm list, --list, -l                                 List installed applications

pyappm add, --add, -a <name>                             Add a dependency to an application from PyPi
pyappm add_local, --add_local <file.whl>                 Add a local dependency to an application from a .whl file

pyappm remove, --remove, -r <name>                      Remove a dependency from an application
pyappm remove_local, --remove_local <name>              Remove a local dependency from an application (.whl file)

pyappm help, --help, -h, -?                              Show this help message
```  
