#pyappm

## Description

This is an easy to use command line tool to manage your Python applications.<br>

NOTE:<br>
This is a work in progress and not yet ready for production use.<br>
DO NOT run the installer as root.<br><br>

## Features v1.0.0

- Install applications from a repository
- Install applications from a file
- Uninstall applications
- List installed applications
- Initialize a new application project
- Build an application
- Add an dependency to an application (from PyPi)
- Add an dependency to an application (from a file)
- Remove a dependency from an application<br><br>

## Roadmap for v1.1.0

- Add an application to a repository
- Remove an application from a repository
- Use versioning for application installation
- Update an application
- A repository for applications<br><br>

## Dependencies

- Python 3.10 or higher
- wget
- unzip<br><br>

## Installation

```bash
wget https://pyappm.nl/downloads/installer.py && python3 installer.py install
```  

<br>

## Usage

```text
Usage: pyappm [options] [command]

pyappm init, --init [<name>]                            Initialize a new application project
pyappm build, --build, -b                               Build the application

pyappm install, --install, -i [<name>|<file.pap>]       Install application from a repository or a local file
pyappm uninstall, --uninstall, -u <name>                Uninstall application

pyappm list, --list, -l                                 List installed applications

pyappm add, --add, -a <name> | <file.whl>               Add a dependency to the application from PyPi or a .whl file

pyappm remove, --remove, -r <name>                      Remove a dependency from an application

pyappm help, --help, -h, -?                              Show this help message
```  
